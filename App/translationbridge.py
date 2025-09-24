import logging
import os
import sys

# 添加项目根目录到Python路径
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from AgentUtils.span import Span_Mgr  # noqa: E402
from Business.translate import translateAgent  # noqa: E402


class TranslationBridge:
    """翻译桥接类，处理所有翻译相关功能"""

    def __init__(self, left_sidebar):
        self.left_sidebar = left_sidebar

    def translate_text(self, text):
        """翻译文本"""
        LLM_client = self.left_sidebar.GenClient()
        storage = self.left_sidebar.get_storage()
        context = self.left_sidebar.getTranslationContext()
        span_mgr = Span_Mgr(storage)
        root_span = span_mgr.create_span("Root operation")
        TsAgent = translateAgent(LLM_client, span_mgr)
        logging.info("start translate URL or text")
        logging.info(text)
        return TsAgent.translate_URLOrText(
            context, context.target_language, text, root_span
        )

    def translate_file(self, filepath, filename):
        """翻译文件内容"""
        # 执行翻译
        LLM_client = self.left_sidebar.GenClient()
        storage = self.left_sidebar.get_storage()
        context = self.left_sidebar.getTranslationContext()
        span_mgr = Span_Mgr(storage)
        root_span = span_mgr.create_span("Root operation")
        TsAgent = translateAgent(LLM_client, span_mgr)
        logging.info(f"文件翻译: {filepath}")
        logging.info(f"文件翻译: {filename}")
        result = TsAgent.translate_file(
            context, context.target_language, filepath, root_span
        )
        logging.info(f"文件翻译完成: {filename}")

        return result
