
from pdfminer.high_level import extract_text
import os

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

def getfilecontent(filepath):
    file_content = ""
    try:
        ## pdf to text/markdown
        ## no wav to text/markdown as sst on client.(onnx is not cross plateform)
        if is_pdf_file(filepath):
            file_content = extract_text(filepath)
        else:
            with open(filepath, "r", encoding="utf-8") as f:
                file_content = f.read()
        return file_content
    except Exception as e:
        logging.error(error_msg)
        return file_content
