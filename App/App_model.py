import logging
import os
import sys

# 添加项目根目录到Python路径
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)
from AgentUtils.clientInfo import clientInfo  # noqa: E402
from AgentUtils.ExpiringDictStorage import ExpiringDictStorage  # noqa: E402
from Business.translateConfig import TranslationContext  # noqa: E402


class _AppModel:
    def __init__(self):
        """初始化应用模型，设置默认值和配置路径"""
        # 应用数据路径配置
        self.app_data_path = os.getenv("FLET_APP_STORAGE_DATA", "app_data")
        os.makedirs(self.app_data_path, exist_ok=True)  # 确保目录存在

        # 存储文件配置
        self.storage_file_path = os.path.join(self.app_data_path, "data_store.json")
        self.storage = ExpiringDictStorage(
            filename=self.storage_file_path, expiry_days=7
        )

        # API 配置字段
        self.api_key = ""
        self.base_url = ""
        self.model_field = ""
        self.target_language = ""

    def configure_api(self, api_key: str, base_url: str, model: str) -> None:
        """配置API参数"""
        self.api_key = api_key
        self.base_url = base_url
        self.model_field = model
        logging.info(f"API配置完成 - 模型: {model}, 基础URL: {base_url}")

    def set_target_language(self, language: str) -> None:
        """设置目标语言"""
        self.target_language = language
        logging.info(f"目标语言设置为: {language}")

    def GenClient(self):
        """生成LLM客户端实例"""
        if not all([self.api_key, self.base_url, self.model_field]):
            logging.error("生成客户端失败: API配置不完整")
            raise ValueError("API配置不完整，请先设置api_key、base_url和model_field")

        LLM_Client = clientInfo(
            api_key=self.api_key,
            base_url=self.base_url,
            model=self.model_field,
            dryRun=False,
            local_cache=self.storage,
            usecache=True,
        )
        logging.info("LLM客户端生成成功 =================")
        return LLM_Client

    def get_storage(self):
        """获取存储实例"""
        return self.storage

    def getTranslationContext(
        self,
        file_list: str = "",
        doc_folder: str = "",
        reserved_word: str = "",
        disclaimers: bool = False,
    ):
        """获取翻译上下文"""
        if not self.target_language:
            logging.warning("目标语言未设置，使用默认值")

        context = TranslationContext(
            target_language=self.target_language,
            file_list=file_list,
            doc_folder=doc_folder,
            reserved_word=reserved_word,
            disclaimers=disclaimers,
        )
        logging.info(f"翻译上下文创建完成 - 目标语言: {self.target_language}")
        return context


# 私有全局实例
_instance = None


def get_app_model() -> _AppModel:
    """获取全局AppModel实例"""
    global _instance
    if _instance is None:
        _instance = _AppModel()
    return _instance


def configure_app(
    api_key: str, base_url: str, model: str, target_language: str = ""
) -> None:
    """快速配置应用"""
    app_model = get_app_model()
    app_model.configure_api(api_key, base_url, model)
    if target_language:
        app_model.set_target_language(target_language)


def get_llm_client():
    """获取LLM客户端"""
    return get_app_model().GenClient()


def get_translation_context(
    file_list: str = "",
    doc_folder: str = "",
    reserved_word: str = "",
    disclaimers: bool = False,
):
    """获取翻译上下文"""
    return get_app_model().getTranslationContext(
        file_list=file_list,
        doc_folder=doc_folder,
        reserved_word=reserved_word,
        disclaimers=disclaimers,
    )


def set_app_target_language(language: str) -> None:
    """设置目标语言"""
    get_app_model().set_target_language(language)


def get_app_storage():
    """获取存储实例"""
    return get_app_model().get_storage()
