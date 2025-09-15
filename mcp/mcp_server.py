import logging
import os
import sys
import base64
import asyncio
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from mcp.server.fastmcp import FastMCP

root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

from AgentUtils.clientInfo import clientInfo  # noqa: E402
from AgentUtils.ExpiringDictStorage import ExpiringDictStorage  # noqa: E402
from AgentUtils.metric import print_metrics  # noqa: E402
from AgentUtils.span import Span_Mgr  # noqa: E402
from Business.translate import translateAgent  # noqa: E402

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)
# 创建 FastAPI 应用
app = FastAPI(title="Translation Server")

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 创建 FastMCP 实例
mcp = FastMCP("translation-server")

storage = ExpiringDictStorage(expiry_days=7)
span_mgr = Span_Mgr(storage)
root_span = span_mgr.create_span("Root operation")

# Mock 翻译函数
def translate_text(text: str, target_lang: str) -> str:
    """文本翻译功能"""
    LLM_Client = clientInfo(
        api_key=os.getenv("api_key"),
        base_url=os.getenv("base_url", "https://api.deepseek.com"),
        model=os.getenv("model", "deepseek-chat"),
        dryRun=os.getenv("dryRun", False),
        local_cache=storage,
        usecache=os.getenv("usecache", True),
    )
    context = TranslationContext(
        target_language=target_lang,
        file_list=file_list,
        configfile_path=configfile_path,
        doc_folder=doc_folder,
        reserved_word=reserved_word,
        max_files=os.getenv("max_files", 20),
        disclaimers=os.getenv("disclaimers", False),
    )
    TsAgent = translateAgent(LLM_client, span_mgr)
    return TsAgent.translate(context, context.target_language, text, root_span)

# Mock 语音识别函数
def mock_speech_to_text(audio_data: bytes) -> str:
    """模拟语音识别功能"""
    return "This is a mock speech recognition result from audio input."

# 请求模型
class TranslateRequest(BaseModel):
    text: str
    target_lang: str = "zh"

class AudioTranslateRequest(BaseModel):
    audio_base64: str
    target_lang: str = "zh"

# HTTP 端点
@app.post("/translate")
async def http_translate(request: TranslateRequest):
    """HTTP 端点用于文本翻译"""
    translated_text = translate_text(request.text, request.target_lang)

    return {
        "translated_text": translated_text,
        "source_text": request.text,
        "target_language": request.target_lang
    }

@app.post("/translate_audio")
async def http_translate_audio(request: AudioTranslateRequest):
    """HTTP 端点用于音频翻译"""
    try:
        audio_data = base64.b64decode(request.audio_base64)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid base64 audio data: {e}")
    
    recognized_text = mock_speech_to_text(audio_data)
    translated_text = translate_text(recognized_text, request.target_lang)
    
    return {
        "recognized_text": recognized_text,
        "translated_text": translated_text,
        "target_language": request.target_lang
    }

@app.get("/")
async def root():
    return {
        "name": "Translation Server",
        "version": "1.0.0",
        "endpoints": {
            "/translate": "POST - Translate text",
            "/translate_audio": "POST - Translate audio"
        }
    }

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
    translated_text = translate_text(text, target_lang)
    
    result = {
        "translated_text": translated_text,
        "source_text": text,
        "target_language": target_lang
    }
    
    import json
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
    except Exception as e:
        return f'{{"error": "Invalid base64 audio data: {e}"}}'
    
    recognized_text = mock_speech_to_text(audio_data)
    translated_text = translate_text(recognized_text, target_lang)
    
    result = {
        "recognized_text": recognized_text,
        "translated_text": translated_text,
        "target_language": target_lang
    }
    
    import json
    return json.dumps(result, ensure_ascii=False)

# 启动服务器
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)