import json
import logging
import os
import threading

from AgentUtils.Agent import Agent
from AgentUtils.tomarkdown import getfilecontent

from .metric import (
    FILES_TRANSLATED,
    SOURCE_FILE_MISSING,
    TARGET_FILE_EXISTS,
    TRANSLATION_REQUESTS,
)
from .utils import MergePN


class translateAgent(Agent):
    def __init__(self, LLM_Client, span_mgr):
        super().__init__(LLM_Client, span_mgr)

    def translate_file(self, TranslationContext, target_language, filepath, span):
        file_content = getfilecontent(filepath)
        return self.translate(TranslationContext, target_language, file_content, span)

    # todo
    # // if url
    # // try download url content
    # // translate as file

    def translate(self, TranslationContext, target_language, content, span):
        # Split content into chunks of 3000 characters
        chunk_size = 3000
        chunks = [
            content[i : i + chunk_size] for i in range(0, len(content), chunk_size)
        ]

        translated_chunks = []
        for i, chunk in enumerate(chunks):
            logging.info(f"Processing chunk {i+1}/{len(chunks)} of {content}")
            PN = TranslationContext.reserved_word
            messages = [
                {
                    "role": "system",
                    "content": TranslationContext.config["prompts"]["translator"],
                },
                {
                    "role": "user",
                    "content": f"""
        Please help translate the following content into {target_language}, reserved word: { PN } in English.
        This is part {i+1} of {len(chunks)} of the document.

        Example json output format:
        {{
            "content": "translated text here...",
            "metadata": {{"chunk": {i+1}, "total": {len(chunks)}}},
            "proper_nouns": "proper nouns 0, "proper nouns 1..."
        }}

        Content to translate:
        {chunk}
        """,
                },
            ]
            try:
                response = self.talk_to_LLM_Json(messages, span)
                translated_chunks.append(
                    json.loads(response.choices[0].message.content)["content"]
                )
                logging.info(
                    json.loads((response.choices[0].message.content))["proper_nouns"]
                )
                # self evaluate for proper_nouns
                PN = MergePN(
                    PN,
                    json.loads((response.choices[0].message.content))["proper_nouns"],
                )
            except Exception as e:
                logging.info(f"Error translating chunk {i+1}: {str(e)}")
                TRANSLATION_REQUESTS.labels(
                    reserved_word=TranslationContext.reserved_word,
                    target_language=target_language,
                    status="error",
                ).inc()
                raise

        # Combine all translated chunks
        output_content = "\n".join(translated_chunks)
        if TranslationContext.disclaimers:
            output_content = output_content + "\n\n " + self.get_legal_info()

        return output_content

    def should_refresh(self, target_file: str, force_refresh: bool = False) -> bool:
        """判断是否需要刷新文件"""
        return force_refresh or not os.path.isfile(target_file)

    # 定义处理函数
    #### todo if there is a existing file, then skip
    def translate_element(self, TranslationContext, element, span):
        TRANSLATION_REQUESTS.labels(
            reserved_word=TranslationContext.reserved_word,
            target_language=element["target_language"],
            status="started",
        ).inc()

        logging.info(f"processing: {element}")

        source_file = element["source_file"]
        if TranslationContext.doc_folder not in source_file:
            source_file = TranslationContext.doc_folder + "/" + source_file

        if not os.path.exists(source_file):
            logging.info("skip as source file missing file " + source_file)
            SOURCE_FILE_MISSING.labels(
                reserved_word=TranslationContext.reserved_word,
                target_language=element["target_language"],
            ).inc()
            TRANSLATION_REQUESTS.labels(
                reserved_word=TranslationContext.reserved_word,
                target_language=element["target_language"],
                status="source_missing",
            ).inc()
            return

        target_file = element["target_file"]
        if TranslationContext.doc_folder not in target_file:
            target_file = TranslationContext.doc_folder + "/" + target_file

        force_refresh = False
        if not TranslationContext.file_list:
            force_refresh = False
        else:
            files_list = [f.strip() for f in TranslationContext.file_list.split(",")]
            force_refresh = source_file in files_list

        if not self.should_refresh(target_file, force_refresh):
            logging.info("skip file as target already there," + target_file)
            TARGET_FILE_EXISTS.labels(
                reserved_word=TranslationContext.reserved_word,
                target_language=element["target_language"],
            ).inc()
            TRANSLATION_REQUESTS.labels(
                reserved_word=TranslationContext.reserved_word,
                target_language=element["target_language"],
                status="target_exists",
            ).inc()
            return

        target_language = element["target_language"]

        output_content = self.translate_file(
            TranslationContext, target_language, source_file, span
        )

        logging.info("translated " + target_file)
        os.makedirs(os.path.dirname(target_file), exist_ok=True)
        with open(target_file, "w", encoding="utf-8") as file:
            file.write(output_content)

        # Record successful translation metrics
        FILES_TRANSLATED.labels(
            reserved_word=TranslationContext.reserved_word,
            target_language=target_language,
        ).inc()
        TRANSLATION_REQUESTS.labels(
            reserved_word=TranslationContext.reserved_word,
            target_language=target_language,
            status="success",
        ).inc()

    ### Phase 2 this is used for action
    def translate_files(self, json_todo_list, TranslationContext, span):
        total = len(json_todo_list["todo"])
        if self.dryRun():
            logging.info("dry Run model skip")
            return

        # Create a list to hold our threads
        threads = []
        # Create a counter for completed tasks (similar to WaitGroup)
        completed = 0
        # Lock for thread-safe counter updates
        counter_lock = threading.Lock()

        def worker(item):
            nonlocal completed
            try:
                logging.info("processing...one file")
                self.translate_element(TranslationContext, item, span)
            finally:
                with counter_lock:
                    completed += 1
                    remaining = total - completed
                    logging.info(f"todo: {remaining}")

        # Create and start threads
        for item in json_todo_list["todo"]:
            thread = threading.Thread(target=worker, args=(item,))
            thread.start()
            threads.append(thread)

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        logging.info("All tasks completed")
