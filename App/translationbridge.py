import logging
import os
import sys

from pdfminer.high_level import extract_text

# 添加项目根目录到Python路径
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from AgentUtils.span import Span_Mgr  # noqa: E402
from Business.translate import translateAgent  # noqa: E402


def is_pdf_file(filepath):
    """
    检查文件是否以.pdf结尾（不区分大小写）

    参数:
    filepath (str): 文件的绝对路径

    返回:
    bool: 如果是PDF文件返回True，否则返回False
    """
    # 使用os.path.splitext获取文件扩展名并转换为小写进行比较
    return os.path.splitext(filepath)[1].lower() == ".pdf"


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

        return TsAgent.translate(context, context.target_language, text, root_span)

    def translate_file(self, filepath, filename):
        """翻译文件内容"""
        file_content = ""
        try:
            # if file is pdf
            if is_pdf_file(filepath):
                file_content = extract_text(filepath)
            else:
                with open(filepath, "r", encoding="utf-8") as f:
                    file_content = f.read()
            # 执行翻译
            result = self.translate_text(file_content)
            logging.info(f"文件翻译完成: {filename}")

            return result
        except Exception as e:
            error_msg = f"文件处理失败: {str(e)}"
            logging.error(error_msg)
            raise Exception(error_msg)
