import json
import logging
from string import Template
from threading import Lock
from typing import Any, Dict, List, Optional

import yaml


class PromptGen:
    def __init__(self, config_path: Optional[str] = None):
        self.Role: str = ""
        self.Situation: str = ""
        self.Action: str = ""
        self.Task_steps: List[str] = []
        self.Quality_assurance: List[str] = []
        self.Output_structure: dict = {}
        self.self_evaluate_vars: Dict[str, str] = {}

        # 新增配置相关属性
        self._config: Dict[str, Any] = {}
        self._configfile_path: Optional[str] = config_path
        self._use_custom_sys_prompt: bool = False
        self._custom_sys_prompt: str = ""

        # 添加线程锁
        self._lock = Lock()

        # 如果提供了配置路径，自动加载配置
        if config_path:
            self.load_config(config_path)

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
        # 如果配置中存在自定义系统提示，则使用配置中的提示
        if self._use_custom_sys_prompt and self._custom_sys_prompt:
            return self._template_to_string(self._custom_sys_prompt)

        # 否则使用原有逻辑构建系统提示
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

    def load_config(self, config_path: Optional[str] = None) -> bool:
        """
        加载配置文件，如果存在则更新当前配置

        参数:
            config_path (str, optional): 要加载的配置文件路径，如果为None则使用实例的_configfile_path

        返回:
            bool: 是否成功加载了配置文件
        """
        # 确定要加载的配置文件路径
        load_path = config_path or self._configfile_path

        if not load_path:
            logging.info("未指定配置文件路径，使用空配置")
            return False

        try:
            with open(load_path, "r", encoding="utf-8") as file:
                config_data = yaml.safe_load(file)

            if not config_data:
                logging.warning(f"配置文件 {load_path} 为空")
                return False

            # 更新配置字典
            self._config = config_data

            # 更新类属性
            self._update_from_config(config_data)

            logging.info(f"成功从 {load_path} 加载配置")
            return True

        except Exception as e:
            logging.error(f"加载配置文件时出错: {e}")
            return False

    def _update_from_config(self, config_data: Dict[str, Any]) -> None:
        """
        从配置数据更新类属性
        """
        # 更新基本属性
        if "Role" in config_data:
            self.Role = config_data["Role"]
        if "Situation" in config_data:
            self.Situation = config_data["Situation"]
        if "Action" in config_data:
            self.Action = config_data["Action"]
        if "Task_steps" in config_data:
            self.Task_steps = config_data["Task_steps"]
        if "Quality_assurance" in config_data:
            self.Quality_assurance = config_data["Quality_assurance"]
        if "Output_structure" in config_data:
            self.Output_structure = config_data["Output_structure"]
        if "self_evaluate_vars" in config_data:
            self.self_evaluate_vars = config_data["self_evaluate_vars"]

        # 检查是否存在自定义系统提示
        if "sys_prompt" in config_data:
            self._custom_sys_prompt = config_data["sys_prompt"]
            self._use_custom_sys_prompt = True
            logging.info("检测到自定义系统提示配置，将使用配置中的系统提示")
        else:
            self._use_custom_sys_prompt = False
            logging.info("未检测到自定义系统提示配置，将使用默认系统提示生成逻辑")

    def get_config(self) -> Dict[str, Any]:
        """
        获取当前配置的副本
        """
        return self._config.copy()
