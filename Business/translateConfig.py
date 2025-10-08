import logging
import os
from typing import Optional

import yaml
from AgentUtils.PromptGen import PromptGen


def load_translation_config(config_path: Optional[str] = None) -> dict:
    """
    加载翻译配置文件，如果不存在则返回空字典

    参数:
        config_path (str, optional): 配置文件路径，默认为 None

    返回:
        dict: 配置字典
    """
    # 如果没有提供配置路径，使用默认路径
    if config_path is None:
        config_path = "config.yaml"

    # 直接从检测配置文件路径开始
    try:
        if os.path.exists(config_path):
            with open(config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f)
        else:
            logging.info(f"配置文件 {config_path} 不存在，返回空配置")
            return {}
    except Exception as e:
        logging.info(f"加载配置文件 {config_path} 时出错: {e}，返回空配置")
        return {}


class TranslationContext(PromptGen):
    def __init__(
        self,
        target_language: str,
        # todo remove
        file_list: Optional[str] = None,
        # todo remove
        doc_folder: Optional[str] = None,
        reserved_word: Optional[str] = None,
        disclaimers: Optional[bool] = True,
    ):
        """
        初始化翻译上下文对象

        参数:
            target_language (str): 目标语言代码 (如 'zh', 'fr')
            file_list (str, optional): 逗号分隔的文件列表字符串
            doc_folder (str, optional): 文档目录路径
            reserved_word (str, optional): 保留字/关键词
            disclaimers (bool, optional): 是否添加免责声明
        """
        # 先初始化父类
        super().__init__()

        # TranslationContext 特有的属性初始化
        self._target_language = target_language
        self._file_list = file_list
        self._doc_folder = doc_folder
        self._reserved_word = reserved_word

        # 处理disclaimers参数
        if isinstance(disclaimers, bool):
            self._disclaimers = disclaimers
        elif isinstance(disclaimers, str):
            normalized = disclaimers.strip().lower()
            if normalized in ("true", "yes", "y", "1", "on"):
                self._disclaimers = True
            elif normalized in ("false", "no", "n", "0", "off", ""):
                self._disclaimers = False
            else:
                raise ValueError(f"无法将字符串 '{disclaimers}' 转换为布尔值")
        elif isinstance(disclaimers, (int, float)):
            self._disclaimers = bool(disclaimers)
        else:
            self._disclaimers = True

        # 设置默认的 PromptGen 属性（如果配置文件没有覆盖）
        self._set_default_prompt_attributes()

    def _set_default_prompt_attributes(self):
        """
        设置默认的 PromptGen 属性，仅在配置文件没有提供时使用
        """
        # 如果父类加载配置后这些属性仍然是空的，则设置默认值
        if not self.Role:
            self.Role = "You are a professional translator and a versatile expert with knowledge spanning various specialized fields, capable of handling technical, professional, and general content"
        if not self.Situation:
            self.Situation = "translating diverse content types including technical documentation, professional reports, academic materials, and general texts"
        if not self.Action:
            self.Action = "accurately preserve the original meaning, context, and nuance during translation while maintaining specialized terminology, proper nouns, command syntax, and special content fragments unchanged"
        if not self.Task_steps:
            self.Task_steps = [
                "Analyze the source text to identify specialized terms, special formatting, and structural elements",
                "Research appropriate expressions for proper nouns and terminology in the target language when necessary, and list all retained items in the result",
                "Translate explanatory text while ensuring professional accuracy",
                "Maintain terminology consistency and fully preserve all terminology and related content",
                "Adapt culturally specific examples as needed to facilitate target audience understanding",
                "Preserve all identified proper nouns and provide brief explanations in parentheses for ambiguous specialized terms or proper nouns",
                "Ensure code syntax, commands, and technical examples remain functional and unchanged",
            ]
        if not self.Quality_assurance:
            self.Quality_assurance = [
                "Do not add any extra explanations or markings",
                "Do not include any document chunking information (e.g., 'This is Part X')",
                "Strictly preserve the original formatting and structure",
                "Ensure all specialized terms are accurately translated or retained in their original form",
                "Verify that code syntax, commands, and technical examples remain functional",
                "Check that formatting and document structure are consistent",
                "Confirm that the translation maintains the same level of professional detail and accuracy as the original",
            ]
        if not self.Output_structure:
            self.Output_structure = {
                "content": "complete and accurate translation preserving all original elements",
                "proper_nouns": "list of all retained proper nouns and specialized terminology",
            }

    def load_config(self, config_path: Optional[str] = None) -> bool:
        """
        加载配置文件，如果存在则更新当前配置

        参数:
            config_path (str, optional): 要加载的配置文件路径，如果为None则使用默认路径

        返回:
            bool: 是否成功加载了配置文件
        """
        # 调用父类的加载配置方法
        success = super().load_config(config_path)

        # 重新设置默认属性（确保未被配置覆盖的属性有默认值）
        self._set_default_prompt_attributes()

        return success

    # ----------------------
    # 属性访问器 (使用 @property)
    # ----------------------
    @property
    def target_language(self) -> str:
        """获取目标语言代码"""
        return self._target_language

    @property
    def file_list(self) -> Optional[str]:
        """获取文件列表(已拆分的列表形式)"""
        if not self._file_list:
            return None
        return self._file_list

    @property
    def raw_file_list(self) -> Optional[str]:
        """获取原始未处理的文件列表字符串"""
        return self._file_list

    @property
    def doc_folder(self) -> Optional[str]:
        """获取文档目录路径"""
        return self._doc_folder

    @property
    def reserved_word(self) -> Optional[str]:
        """获取保留字/关键词"""
        return self._reserved_word

    @property
    def disclaimers(self) -> bool:
        """获取是否添加免责声明"""
        return self._disclaimers

    def show_config(self) -> None:
        """
        显示当前配置信息
        """
        logging.info("\nTranslation Context Configuration:")
        logging.info(f"  Target Language: {self._target_language}")
        logging.info(f"  File list: {self._file_list}")
        logging.info(f"  Doc folder: {self._doc_folder}")
        logging.info(f"  Reserved words: {self._reserved_word}")
        logging.info(f"  Disclaimers: {self._disclaimers}")
