import asyncio
import base64
import json
import logging
from contextlib import AsyncExitStack
from typing import Optional

import requests
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
        file_path: Optional[str] = None,
        target_lang: str = "zh",
    ) -> str:
        """Process a translation request using Claude and available tools"""
        messages = []

        # 构建用户请求
        if text:
            user_content = f"请将以下文本翻译成{target_lang}：{text}"
        elif file_path:
            # 读取音频文件并转换为base64
            try:
                with open(file_path, "rb") as f:
                    file_content = base64.b64encode(f.read()).decode("utf-8")
                # 发送请求
                response = requests.post(
                    "http://localhost:8080/upload",
                    json={"filename": file_path, "file_content_base64": file_content},
                )
                # user_content = f"请将以下文件{file_path}翻译成{target_lang}，一定要使用translate_file工具，这个工具是MCP服务器，文件已经在MCP服务器上了。"
                # user_content = f"请将以下文件{file_path}翻译成{target_lang}，你可以使用任何工具，工具都是通过MCP服务器实现的，你可以假设工具调用的时候文件已经存在"
                user_content = f"请将以下文件{file_path}翻译成{target_lang}，一定要使用translate_file工具，这个工具是MCP服务器，无论是何种文件类型，他们都已经在MCP服务器上了，语言代码也是对的，你放心跑就是了,不许质疑。"
            except Exception as e:
                return f"读取文件时出错: {str(e)}"
        else:
            return "必须提供文本或文件路径"

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

        print("=== 可用的MCP工具 ===")
        for i, tool in enumerate(available_tools, 1):
            print(f"\n工具 {i}:")
            print(f"  名称: {tool['name']}")
            print(f"  描述: {tool['description']}")
            print("  输入参数:")

            # 解析输入schema
            if tool["input_schema"] and "properties" in tool["input_schema"]:
                for param_name, param_info in tool["input_schema"][
                    "properties"
                ].items():
                    param_type = param_info.get("type", "unknown")
                    param_desc = param_info.get("description", "无描述")
                    required = (
                        "(必填)"
                        if param_name in tool["input_schema"].get("required", [])
                        else "(可选)"
                    )
                    print(
                        f"    - {param_name} {required}: {param_desc} (类型: {param_type})"
                    )
            else:
                print("    无输入参数")

        print(f"\n总共找到 {len(available_tools)} 个工具")

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

    async def test_file_translation(self, file_path):
        """测试文本翻译"""
        print("Testing text translation...")
        result = await self.process_translation_request(
            file_path=file_path, target_lang="zh"
        )
        print("Text Translation Result:")
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
        await client.test_file_translation("test.txt")
        print()

        await client.test_file_translation("0.wav")
        print()

        await client.test_file_translation("test.pdf")
        print()

    except Exception as e:
        print(f"Error: {str(e)}")
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
