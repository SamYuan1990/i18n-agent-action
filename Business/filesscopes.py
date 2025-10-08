import json
import logging

from AgentUtils.Agent import Agent

from .utils import get_all_files

# 默认配置常量
DEFAULT_CONFIG = {
    "prompts": {
        "config_analysis": "According to config file below:\n- Which i18n does the project cover?\n- What's the naming rule or file path rule for i18n mapping between different language editions?",
        "json_schema": 'Please result in mapping as default language file, target file.\nThe empty json schema is:\n{\n  "todo": []\n}\nIf there\'s one object in json:\n{\n  "todo": [\n    {\n      "source_file": "/path_to_default_language_file",\n      "target_file": "/path_to_target_file",\n      "target_language": "zh"\n    }\n  ]\n}',
        "analysis": "You are a senior software engineer\n\nYour core responsibilities:\n- Analysis user's provided i18n config file.\n- Analysis the naming rule or file path rule for i18n mapping between different language editions?\n- Base on file lists from user, help analysis the file paths.\n\nFile lists analysis steps:\n- According to naming rule or file path rule for i18n mapping between different language editions.\n- user will provide a list with absolute path, identify if the file is default language file or not.\n- if yes, please answer with translated language file name with absolute path.\n\nQuality assurance steps:\n- Verify you understand i18n config file.\n- Verify you understand the naming rule or file path rule for i18n mapping between different language editions.",
    }
}


class filescopeAgent(Agent):
    def __init__(self, LLM_Client, span_mgr):
        super().__init__(LLM_Client, span_mgr)

    ### Phase 1 missingfiles
    def filesscopes(
        self, configfile_path, file_list, doc_folder, target_language, max_files, span
    ):
        with open(configfile_path, "r", encoding="utf-8") as file:
            config_file_content = file.read()  # 读取全部内容为字符串

        # 使用默认配置常量
        prompts = DEFAULT_CONFIG["prompts"]

        messages = [
            {
                "role": "user",
                "content": prompts["analysis"],
            }
        ]
        messages.append(
            {
                "role": "user",
                "content": prompts["config_analysis"] + config_file_content,
            }
        )

        if self.dryRun():
            logging.info("dry Run model using cache")
            return {
                "todo": [
                    {
                        "source_file": "/workspace/docs/index.md",
                        "target_file": "/workspace/docs/index.zh.md",
                        "target_language": "zh",
                    }
                ]
            }

        response1 = self.talk_to_LLM(messages, span)
        answer1 = response1.choices[0].message.content
        logging.info("问题1 回答:" + answer1)
        messages.append({"role": "user", "content": answer1})

        filelist = [str(filepath) for filepath in get_all_files(doc_folder)]

        if file_list:  # 检查是否非空
            given_files = file_list.split(",")  # 拆分成列表
            filelist = given_files + filelist  # 合并到最前面

        # 将filelist分批次处理，每批30个文件
        batch_size = 30
        all_todos = []  # 用于累积所有批次的待办事项
        for i in range(0, len(filelist), batch_size):
            batch = filelist[i : i + batch_size]
            messages.append(
                {
                    "role": "user",
                    "content": (
                        f"here is part {i//batch_size + 1} of file lists for docs folder\n"
                        + "\n".join(batch)
                        + "\n\ncould you please list missing translated documents in "
                        + target_language
                        + " language?\n\n"
                        + prompts["json_schema"]
                    ),
                }
            )
            response2 = self.talk_to_LLM_Json(messages, span)
            logging.info(
                f"问题2 回答(批次 {i//batch_size + 1}):"
                + response2.choices[0].message.content
            )

            current_batch = json.loads(response2.choices[0].message.content)
            logging.info(f"本批次待办数量: {len(current_batch['todo'])}")
            all_todos.extend(current_batch["todo"])
            if len(all_todos) > max_files:
                break

        json_todo_list = {"todo": all_todos}
        logging.info(f"总待办数量: {len(all_todos)}")
        return json_todo_list
