import logging
import os
import sys

from App_model import get_app_storage, get_llm_client, get_translation_context

# 添加项目根目录到Python路径
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from AgentUtils.span import Span_Mgr  # noqa: E402
from Business.translate import translateAgent  # noqa: E402


class TranslationBridge:
    """翻译桥接类，处理所有翻译相关功能"""

    def __init__(self):
        """初始化全局资源"""
        self._initialized = False
        self.LLM_client = None
        self.storage = None
        self.context = None
        self.span_mgr = None
        self.TsAgent = None

    def _initialize_globals(self):
        """初始化全局资源（懒加载）"""
        if not self._initialized:
            self.LLM_client = get_llm_client()
            self.storage = get_app_storage()
            self.context = get_translation_context()
            self.span_mgr = Span_Mgr(self.storage)
            self.TsAgent = translateAgent(self.LLM_client, self.span_mgr)
            self._initialized = True

    def translate_text(self, text):
        """翻译文本"""
        self._initialize_globals()
        root_span = self.span_mgr.create_span("Root operation")

        logging.info("start translate URL or text")
        logging.info(text)

        return self.TsAgent.translate_URLOrText(
            self.context, self.context.target_language, text, root_span
        )

    def translate_file(self, filepath, filename):
        """翻译文件内容"""
        self._initialize_globals()
        root_span = self.span_mgr.create_span("Root operation")

        logging.info(f"文件翻译: {filepath}")
        logging.info(f"文件翻译: {filename}")

        result = self.TsAgent.translate_file(
            self.context, self.context.target_language, filepath, root_span
        )

        logging.info(f"文件翻译完成: {filename}")
        return result


# 创建全局实例
translation_bridge = TranslationBridge()


# 提供便捷的全局函数
def translate_text(text):
    """全局函数：翻译文本"""
    return translation_bridge.translate_text(text)


def translate_file(filepath, filename):
    """全局函数：翻译文件内容"""
    return translation_bridge.translate_file(filepath, filename)
