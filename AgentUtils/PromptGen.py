import json
from string import Template
from threading import Lock
from typing import Dict, List, Optional


class PromptGen:
    def __init__(self):
        self.Role: str = ""
        self.Situation: str = ""
        self.Action: str = ""
        self.Task_steps: List[str] = []
        self.Quality_assurance: List[str] = []
        self.Output_structure: dict = {}
        self.self_evaluate_vars: Dict[str, str] = {}
        # 添加线程锁
        self._lock = Lock()

    def _template_to_string(
        self, template: str, vars_dict: Optional[Dict[str, str]] = None
    ) -> str:
        """
        内部函数：将模板字符串中的变量替换为字典中的值
        """
        if vars_dict is None:
            vars_dict = self.self_evaluate_vars

        try:
            # 使用Template进行安全替换
            template_obj = Template(template)
            result = template_obj.safe_substitute(vars_dict)
            return result
        except Exception as e:
            print(f"模板替换错误: {e}")
            return template

    def to_sys_prompt(self) -> str:
        """
        构建系统提示模板
        """
        # 构建基础部分
        parts = [
            f"{self.Role}, {self.Situation}, {self.Action}\n",
            "Task methodology: \n",
        ]

        # 添加Task步骤
        for i, task in enumerate(self.Task_steps[:7]):  # 不超过7个
            parts.append(f"\tStep_{i+1}: {task}\n")

        # 添加Quality assurance
        parts.append("\nQuality assurance: \n")
        for i, qa in enumerate(self.Quality_assurance[:7]):  # 不超过7个
            parts.append(f"\tQuality_assurance_{i+1}: {qa}\n")

        # 添加Output Structure
        output_structure_str = json.dumps(
            self.Output_structure, indent=2, ensure_ascii=False
        )
        parts.append(f"\nOutput Structure in json:\n{output_structure_str}\n")

        # 组合所有部分
        template = "".join(parts)

        # 使用模板替换变量
        return self._template_to_string(template)

    def to_task_prompt(
        self,
        task_specific: str,
        example: Optional[str] = None,
        evaluate_vars: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        构建任务提示模板（线程安全版本）
        """
        parts = []

        # 添加示例（如果存在）
        if example:
            parts.append(f"You can reference example: {example}\n")

        # 添加任务内容
        parts.append(f"Here is task content: {task_specific}")

        # 组合模板
        template = "\n".join(parts)

        # 使用锁保护共享变量的更新
        with self._lock:
            # 合并评估变量
            merged_vars = self.self_evaluate_vars.copy()
            if evaluate_vars:
                merged_vars.update(evaluate_vars)
                self.self_evaluate_vars = merged_vars

        # 使用模板替换变量
        return self._template_to_string(template, merged_vars)

    def update_evaluate_vars(self, new_vars: Dict[str, str]) -> None:
        """
        线程安全地更新评估变量
        """
        with self._lock:
            self.self_evaluate_vars.update(new_vars)

    def get_evaluate_vars(self) -> Dict[str, str]:
        """
        线程安全地获取评估变量副本
        """
        with self._lock:
            return self.self_evaluate_vars.copy()
