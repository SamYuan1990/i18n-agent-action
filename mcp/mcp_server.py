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
from starlette.routing import Mount, Route

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from AgentUtils.clientInfo import clientInfo  # noqa: E402
from AgentUtils.ExpiringDictStorage import ExpiringDictStorage  # noqa: E402
from AgentUtils.span import Span_Mgr  # noqa: E402
from Business.translate import translateAgent  # noqa: E402

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

# 创建 FastMCP 实例
mcp = FastMCP("translation-server")

storage = ExpiringDictStorage(expiry_days=7)
span_mgr = Span_Mgr(storage)
root_span = span_mgr.create_span("Root operation")


# Mock 翻译函数
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
    configfile_path = os.getenv("configfile_path", "")
    doc_folder = os.getenv("doc_folder", "")
    reserved_word = os.getenv("reserved_word", "")

    # 假设TranslationContext类的定义
    class TranslationContext:
        def __init__(
            self,
            target_language,
            file_list,
            configfile_path,
            doc_folder,
            reserved_word,
            max_files,
            disclaimers,
        ):
            self.target_language = target_language
            self.file_list = file_list
            self.configfile_path = configfile_path
            self.doc_folder = doc_folder
            self.reserved_word = reserved_word
            self.max_files = max_files
            self.disclaimers = disclaimers

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
    return TsAgent.translate(context, context.target_language, text, root_span)


# MCP 工具
@mcp.tool()
def translate_text(text: str, target_lang: str = "en") -> str:
    """
    Translate text to the target language.

    Args:
        text: The text to translate
        target_lang: The target language code (en, es, fr, de, ja, zh)

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


@mcp.tool()
def translate_audio(audio_base64: str, target_lang: str = "en") -> str:
    """
    Translate audio to the target language and extract proper nouns.

    Args:
        audio_base64: Base64 encoded audio data (WAV format)
        target_lang: The target language code (en, es, fr, de, ja, zh)

    Returns:
        A JSON string containing recognized text, translated text
    """
    try:
        audio_data = base64.b64decode(audio_base64)
        with open("/tmp/test.wav", "wb") as f:
            f.write(audio_data)
    except Exception as e:
        return f'{{"error": "Invalid base64 audio data: {e}"}}'

    recognizer = sherpa_onnx.OfflineRecognizer.from_whisper(
        encoder=os.getenv("encoder", "/tmp/base-encoder.onnx"),
        decoder=os.getenv("decoder", "/tmp/base-decoder.onnx"),
        tokens=os.getenv("tokens", "/tmp/base-tokens.onnx"),
        language="",
    )
    stream = recognizer.create_stream()

    try:
        audio, sample_rate = sf.read("/tmp/test.wav", dtype="float32", always_2d=True)
    except Exception as e:
        print(e)

    audio = audio[:, 0]
    stream.accept_waveform(sample_rate, audio)
    recognizer.decode_stream(stream)
    recognized_text = stream.result.text
    translated_text = _translate_text(recognized_text, target_lang)

    result = {
        "recognized_text": recognized_text,
        "translated_text": translated_text,
        "target_language": target_lang,
    }

    return json.dumps(result, ensure_ascii=False)


def create_starlette_app(mcp_server: Server, *, debug: bool = False) -> Starlette:
    """Create a Starlette application that can serve the provided mcp server with SSE."""
    sse = SseServerTransport("/messages/")

    async def handle_sse(request: Request) -> None:
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

    return Starlette(
        debug=debug,
        routes=[
            Route("/sse", endpoint=handle_sse),
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
