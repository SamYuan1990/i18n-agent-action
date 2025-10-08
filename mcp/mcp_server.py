import base64
import json
import logging
import os
import sys

import sherpa_onnx
import soundfile as sf
import uvicorn
from mcp.server import Server
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse, Response  # 添加了JSONResponse
from starlette.routing import Mount, Route

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from AgentUtils.clientInfo import clientInfo  # noqa: E402
from AgentUtils.ExpiringDictStorage import ExpiringDictStorage  # noqa: E402
from AgentUtils.span import Span_Mgr  # noqa: E402
from Business.translate import translateAgent  # noqa: E402
from Business.translateConfig import TranslationContext  # noqa: E402

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

# 创建 FastMCP 实例
mcp = FastMCP("translation-server")

storage = ExpiringDictStorage(expiry_days=7)
span_mgr = Span_Mgr(storage)
root_span = span_mgr.create_span("Root operation")


def is_wav_file(filepath):
    """
    检查文件是否以.wav结尾（不区分大小写）

    参数:
    filepath (str): 文件的绝对路径

    返回:
    bool: 如果是PDF文件返回True，否则返回False
    """
    # 使用os.path.splitext获取文件扩展名并转换为小写进行比较
    return os.path.splitext(filepath)[1].lower() == ".wav"


def _translate_file(filename: str, target_lang: str) -> str:
    """文件翻译功能"""
    LLM_Client = clientInfo(
        api_key=os.getenv("api_key"),
        base_url=os.getenv("base_url", "https://api.deepseek.com"),
        model=os.getenv("model", "deepseek-chat"),
        dryRun=os.getenv("dryRun", False),
        local_cache=storage,
        usecache=os.getenv("usecache", True),
    )

    # 从环境变量获取或设置默认值
    file_list = os.getenv("file_list", "").split(",") if os.getenv("file_list") else []
    configfile_path = os.getenv("configfile_path", "")
    doc_folder = os.getenv("doc_folder", "")
    reserved_word = os.getenv("reserved_word", "")

    context = TranslationContext(
        target_language=target_lang,
        file_list=file_list,
        configfile_path=configfile_path,
        doc_folder=doc_folder,
        reserved_word=reserved_word,
        max_files=int(os.getenv("max_files", 20)),
        disclaimers=os.getenv("disclaimers", "False").lower() == "true",
    )
    TsAgent = translateAgent(LLM_Client, span_mgr)
    return TsAgent.translate_file(context, context.target_language, filename, root_span)


def _translate_text(text: str, target_lang: str) -> str:
    """文本翻译功能"""
    LLM_Client = clientInfo(
        api_key=os.getenv("api_key"),
        base_url=os.getenv("base_url", "https://api.deepseek.com"),
        model=os.getenv("model", "deepseek-chat"),
        dryRun=os.getenv("dryRun", False),
        local_cache=storage,
        usecache=os.getenv("usecache", True),
    )

    # 从环境变量获取或设置默认值
    file_list = os.getenv("file_list", "").split(",") if os.getenv("file_list") else []
    reserved_word = os.getenv("reserved_word", "")
    doc_folder = os.getenv("doc_folder", "")

    context = TranslationContext(
        target_language=target_lang,
        file_list=file_list,
        doc_folder=doc_folder,
        reserved_word=reserved_word,
        disclaimers=os.getenv("disclaimers", "False").lower() == "true",
    )
    TsAgent = translateAgent(LLM_Client, span_mgr)
    return TsAgent.translate_URLOrText(
        context, context.target_language, text, root_span
    )


# MCP 工具
@mcp.tool()
def translate_text(text: str, target_lang: str = "en") -> str:
    """
    Translate text to the target language.

    Args:
        text: The text to translate or URL as http/https
        target_lang: The target language code ISO 639-1 (en, es, fr, de, ja, zh)

    Returns:
        A JSON string containing translated text
    """
    translated_text = _translate_text(text, target_lang)

    result = {
        "translated_text": translated_text,
        "source_text": text,
        "target_language": target_lang,
    }

    return json.dumps(result, ensure_ascii=False)


@mcp.tool()  # 修正：添加了括号
def translate_file(file_name: str, target_lang: str = "en") -> str:
    """
    Translate file on mcp server to target language, it supports file like pdf, wav, txt and so on.

    Args:
        file_name: id for file
        target_lang: The target language code ISO 639-1 (en, es, fr, de, ja, zh)

    Returns:
        A JSON string containing translated text
    """

    if is_wav_file("/tmp/" + file_name):
        recognizer = sherpa_onnx.OfflineRecognizer.from_whisper(
            encoder=os.getenv("encoder", "/tmp/base-encoder.onnx"),
            decoder=os.getenv("decoder", "/tmp/base-decoder.onnx"),
            tokens=os.getenv("tokens", "/tmp/base-tokens.onnx"),
            language="",
        )
        stream = recognizer.create_stream()
        try:
            audio, sample_rate = sf.read(
                "/tmp/" + file_name, dtype="float32", always_2d=True
            )
        except Exception as e:
            print(e)
        audio = audio[:, 0]
        stream.accept_waveform(sample_rate, audio)
        recognizer.decode_stream(stream)
        text = stream.result.text
        translated_text = _translate_text(text, target_lang)
        result = {"translated_text": translated_text}
        return json.dumps(result, ensure_ascii=False)

    translated_text = _translate_file("/tmp/" + file_name, target_lang)

    result = {"translated_text": translated_text}

    return json.dumps(result, ensure_ascii=False)


# 新增的文件上传处理函数
async def handle_file_upload(request: Request) -> JSONResponse:
    """
    处理文件上传的REST接口
    接收JSON格式的请求体，包含filename和file_content_base64字段
    """
    try:
        # 解析请求体
        body = await request.json()

        # 获取文件名和base64内容
        filename = body.get("filename")
        file_content_base64 = body.get("file_content_base64")

        # 验证必要字段
        if not filename:
            return JSONResponse({"error": "Filename is required"}, status_code=400)

        if not file_content_base64:
            return JSONResponse(
                {"error": "file_content_base64 is required"}, status_code=400
            )

        # 清理文件名，防止路径遍历攻击
        filename = os.path.basename(filename)

        # 构建完整的文件路径
        file_path = os.path.join("/tmp", filename)

        try:
            # 解码base64数据
            file_data = base64.b64decode(file_content_base64)
        except Exception as e:
            return JSONResponse(
                {"error": f"Invalid base64 data: {str(e)}"}, status_code=400
            )

        # 确保/tmp目录存在
        os.makedirs("/tmp", exist_ok=True)

        # 写入文件
        with open(file_path, "wb") as f:
            f.write(file_data)

        # 验证文件是否成功写入
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            logging.info(
                f"File saved successfully: {file_path}, size: {file_size} bytes"
            )

            return JSONResponse(
                {
                    "status": "success",
                    "message": "File saved successfully",
                    "filename": filename,
                    "file_path": file_path,
                    "file_size": file_size,
                }
            )
        else:
            return JSONResponse({"error": "Failed to save file"}, status_code=500)

    except json.JSONDecodeError:
        return JSONResponse({"error": "Invalid JSON in request body"}, status_code=400)
    except Exception as e:
        logging.error(f"Error handling file upload: {str(e)}")
        return JSONResponse(
            {"error": f"Internal server error: {str(e)}"}, status_code=500
        )


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can serve the provided mcp server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> Response:  # Changed return type
        try:
            async with sse.connect_sse(
                request.scope,
                request.receive,
                request._send,  # noqa: SLF001
            ) as (read_stream, write_stream):
                await mcp_server.run(
                    read_stream,
                    write_stream,
                    mcp_server.create_initialization_options(),
                )

            return Response("Accepted", status_code=202)  # Added return statement

        except Exception:
            logging.info("Exception occurred while handling SSE")
            return Response(
                "Internal Server Error", status_code=500
            )  # Added return statement

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
            Route(
                "/upload", endpoint=handle_file_upload, methods=["POST"]
            ),  # 新增上传路由
            Mount("/messages/", app=sse.handle_post_message),
        ],
    )


if __name__ == "__main__":
    mcp_server = mcp._mcp_server  # noqa: WPS437

    import argparse

    parser = argparse.ArgumentParser(description="Run MCP SSE-based server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    args = parser.parse_args()

    # Bind SSE request handling to MCP server
    starlette_app = create_starlette_app(mcp_server, debug=True)

    uvicorn.run(starlette_app, host=args.host, port=args.port)
