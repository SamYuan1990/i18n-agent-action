import logging
import os
from typing import Optional

import yaml


class TranslationContext:
    def __init__(
        self,
        target_language: str,
        file_list: Optional[str] = None,
        configfile_path: Optional[str] = None,
        doc_folder: Optional[str] = None,
        reserved_word: Optional[str] = None,
        max_files: Optional = int,
        disclaimers: Optional[bool] = True,
    ):
        """
        初始化翻译上下文对象

        参数:
            target_language (str): 目标语言代码 (如 'zh', 'fr')
            file_list (str, optional): 逗号分隔的文件列表字符串
            configfile_path (str, optional): 配置文件路径
            doc_folder (str, optional): 文档目录路径
            reserved_word (str, optional): 保留字/关键词
        """
        self._target_language = target_language
        self._file_list = file_list
        self._configfile_path = configfile_path
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

        # 处理max_files参数
        try:
            self._max_files = int(max_files)
        except (ValueError, TypeError):
            self._max_files = 20

        # 加载配置文件，如果不存在则使用默认配置
        self._config = self._load_config()

    def _load_config(self):
        """加载配置文件，如果不存在则使用默认配置"""
        # 默认配置
        default_config = {
            "prompts": {
                "config_analysis": "According to config file below:\n- Which i18n does the project cover?\n- What's the naming rule or file path rule for i18n mapping between different language editions?",
                "json_schema": 'Please result in mapping as default language file, target file.\nThe empty json schema is:\n{\n  "todo": []\n}\nIf there\'s one object in json:\n{\n  "todo": [\n    {\n      "source_file": "/path_to_default_language_file",\n      "target_file": "/path_to_target_file",\n      "target_language": "zh"\n    }\n  ]\n}',
                "translator": """You are a professional translator and a versatile expert with knowledge spanning various specialized fields, capable of handling technical, professional, and general content.
Core Responsibilities:
Accurately preserve the original meaning, context, and nuance during translation
Maintain specialized terminology, proper nouns, command syntax, and special content fragments unchanged
Ensure explanations and descriptions align with target language conventions while retaining accuracy
Handle diverse content types, including but not limited to technical documentation, professional reports, academic materials, and general texts
Translation Methodology:
Analyze the source text to identify specialized terms, special formatting, and structural elements
Research appropriate expressions for proper nouns and terminology in the target language when necessary, and list all retained items in the result
Translate explanatory text while ensuring professional accuracy
Maintain terminology consistency
Fully preserve all terminology and related content
Adapt culturally specific examples as needed to facilitate target audience understanding
Quality Assurance Steps:
Do not add any extra explanations or markings
Do not include any document chunking information (e.g., “This is Part X”)
Strictly preserve the original formatting and structure
Ensure all specialized terms are accurately translated or retained in their original form
Verify that code syntax, commands, and technical examples remain functional
Check that formatting and document structure are consistent
Confirm that the translation maintains the same level of professional detail and accuracy as the original
Retain all identified proper nouns
Provide brief explanations in parentheses for ambiguous specialized terms or proper nouns (reference may be made to user-provided reserved words)
                """,
                "analysis": "You are a senior software engineer\n\nYour core responsibilities:\n- Analysis user's provided i18n config file.\n- Analysis the naming rule or file path rule for i18n mapping between different language editions?\n- Base on file lists from user, help analysis the file paths.\n\nFile lists analysis steps:\n- According to naming rule or file path rule for i18n mapping between different language editions.\n- user will provide a list with absolute path, identify if the file is default language file or not.\n- if yes, please answer with translated language file name with absolute path.\n\nQuality assurance steps:\n- Verify you understand i18n config file.\n- Verify you understand the naming rule or file path rule for i18n mapping between different language editions.",
            }
        }

        config_path = "config.yaml"

        try:
            if os.path.exists(config_path):
                with open(config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
            else:
                logging.info(f"配置文件 {config_path} 不存在，使用默认配置")
                return default_config
        except Exception as e:
            logging.info(f"加载配置文件时出错: {e}，使用默认配置")
            return default_config

    # ----------------------
    # 属性访问器 (使用 @property)
    # ----------------------
    @property
    def target_language(self) -> str:
        """获取目标语言代码"""
        return self._target_language

    @property
    def file_list(self) -> str:
        """获取文件列表(已拆分的列表形式)"""
        if not self._file_list:
            return None
        return self._file_list

    @property
    def raw_file_list(self) -> Optional[str]:
        """获取原始未处理的文件列表字符串"""
        return self._file_list

    @property
    def configfile_path(self) -> Optional[str]:
        """获取配置文件路径(返回Path对象)"""
        return self._configfile_path if self._configfile_path else None

    @property
    def doc_folder(self) -> Optional[str]:
        """获取文档目录路径(返回Path对象)"""
        return self._doc_folder if self._doc_folder else None

    @property
    def reserved_word(self) -> Optional[str]:
        """获取保留字/关键词"""
        return self._reserved_word

    @property
    def max_files(self) -> int:
        return self._max_files

    @property
    def disclaimers(self) -> bool:
        return self._disclaimers

    @property
    def config(self) -> dict:
        return self._config

    def show_config(self) -> None:
        """
        显示当前配置信息

        参数:
            verbose (bool): 是否显示详细路径信息，默认为False
        """
        logging.info("\nTranslation Context Configuration:")
        logging.info(f"  Target Language: {self._target_language}")
        logging.info(f"  File list:' {self._file_list}")
        logging.info(f"  configfile path: {self._configfile_path}")
        logging.info(f"  doc folder: {self._doc_folder}")
        logging.info(f"  reserved words: {self._reserved_word}")
        logging.info(f"  max doc limits: {self._max_files}")
        logging.info(f"  disclaimers: {self._disclaimers}")
