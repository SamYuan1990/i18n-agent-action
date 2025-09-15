import asyncio
import base64
import json
import logging
from contextlib import AsyncExitStack
from typing import Optional

from anthropic import Anthropic
from dotenv import load_dotenv
from mcp.client.session import ClientSession
from mcp.client.sse import sse_client

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO
)

load_dotenv()  # load environment variables from .env


class TranslationMCPClient:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.anthropic = Anthropic()

    async def connect_to_server(self):
        """Connect to the translation MCP server running on localhost:8080"""
        # Store the context managers so they stay alive
        self._streams_context = sse_client(url="http://localhost:8080/sse")
        streams = await self._streams_context.__aenter__()

        self._session_context = ClientSession(*streams)
        self.session: ClientSession = await self._session_context.__aenter__()

        # Initialize
        await self.session.initialize()

        # List available tools to verify connection
        print("Initialized SSE client...")
        print("Listing tools...")
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_translation_request(
        self,
        text: Optional[str] = None,
        audio_path: Optional[str] = None,
        target_lang: str = "zh",
    ) -> str:
        """Process a translation request using Claude and available tools"""
        messages = []

        # 构建用户请求
        if text:
            user_content = f"请将以下文本翻译成{target_lang}：{text}"
        elif audio_path:
            # 读取音频文件并转换为base64
            try:
                with open(audio_path, "rb") as audio_file:
                    audio_data = audio_file.read()
                audio_base64 = base64.b64encode(audio_data).decode("utf-8")
                user_content = (
                    f"请将以下音频内容翻译成{target_lang}，音频数据为：{audio_base64}"
                )
            except Exception as e:
                return f"读取音频文件时出错: {str(e)}"
        else:
            return "必须提供文本或音频路径"

        messages.append({"role": "user", "content": user_content})

        # 获取可用工具
        response = await self.session.list_tools()
        available_tools = [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.inputSchema,
            }
            for tool in response.tools
        ]

        # 初始Claude API调用
        response = self.anthropic.messages.create(
            model="deepseek-chat",
            max_tokens=1000,
            messages=messages,
            tools=available_tools,
        )

        # 处理响应并处理工具调用
        final_text = []

        for content in response.content:
            if content.type == "text":
                final_text.append(content.text)
            elif content.type == "tool_use":
                tool_name = content.name
                tool_args = content.input

                # 执行工具调用
                try:
                    result = await self.session.call_tool(tool_name, tool_args)
                    final_text.append(f"[调用工具 {tool_name}]")

                    # 将工具结果添加到消息中
                    messages.append(
                        {
                            "role": "assistant",
                            "content": [{"type": "tool_use", **content.dict()}],
                        }
                    )

                    messages.append(
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "tool_result",
                                    "tool_use_id": content.id,
                                    "content": result.content,
                                }
                            ],
                        }
                    )

                    # 获取Claude的下一步响应
                    next_response = self.anthropic.messages.create(
                        model="deepseek-chat",
                        max_tokens=1000,
                        messages=messages,
                    )

                    # 添加最终响应
                    for next_content in next_response.content:
                        if next_content.type == "text":
                            final_text.append(next_content.text)

                except Exception as e:
                    final_text.append(f"调用工具 {tool_name} 时出错: {str(e)}")

        return "\n".join(final_text)

    async def test_text_translation(self):
        """测试文本翻译"""
        print("Testing text translation...")
        result = await self.process_translation_request(
            text="Hello, how are you?", target_lang="zh"
        )
        print("Text Translation Result:")
        print(result)

    async def test_audio_translation(self, audio_path: str):
        """测试音频翻译"""
        print("Testing audio translation...")
        result = await self.process_translation_request(
            audio_path=audio_path, target_lang="zh"
        )
        print("Audio Translation Result:")
        print(result)

    async def test_server_info(self):
        """测试服务器信息"""
        try:
            # 假设你的MCP服务器提供了一个获取服务器信息的工具
            result = await self.session.call_tool("get_server_info", {})
            print("Server Info:")
            print(json.dumps(result.content, indent=2))
        except Exception as e:
            print(f"获取服务器信息时出错: {str(e)}")

    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()


async def main():
    client = TranslationMCPClient()
    try:
        logging.info("connect_to_server")
        await client.connect_to_server()
        logging.info("test_server_info")
        # 测试服务器信息
        await client.test_server_info()
        print()

        # 测试文本翻译
        await client.test_text_translation()
        print()

        # 测试音频翻译（需要提供音频文件路径）
        audio_path = "./mcp/0.wav"
        await client.test_audio_translation(audio_path)

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
