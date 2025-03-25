import asyncio
import os
import json
from typing import Optional
from openai import AsyncOpenAI
from dotenv import load_dotenv
import aiohttp


# 加载.env文件，确保API Key受到保护
load_dotenv()


class MCPClient:
    def __init__(self):
        """初始化MCP客户端"""
        self.openai_api_key = os.getenv("OPENAI_API_KEY")  # 读取OpenAI API Key
        self.base_url = os.getenv("BASE_URL")  # 读取BASE YRL
        self.model = os.getenv("MODEL")  # 读取model

        if not self.openai_api_key:
            raise ValueError("❌未找到OpenAI API Key，请在.env文件中设置OPENAI_API_KEY")

        self.client = AsyncOpenAI(api_key=self.openai_api_key, base_url=self.base_url)
        self.session = aiohttp.ClientSession()
        self.tools = []

    async def connect_to_server(self):
        """连接到MCP服务器并列出可用工具"""
        async with self.session.get("http://localhost:8000/connect") as resp:
            async for line in resp.content:
                line = line.decode('utf-8').strip()
                if line.startswith('data:'):
                    data = json.loads(line[5:])
                    if data.get("message") == "Connected":
                        # 获取可用工具
                        # 这里可以根据实际情况修改获取工具的逻辑
                        response = await self.session.post("http://localhost:8000/list_tools")
                        tools_data = await response.json()
                        self.tools = tools_data.get("tools", [])
                        print("\n已连接到服务器，支持以下工具:", [tool.get("name") for tool in self.tools])
                        break

    async def process_query(self, query: str) -> str:
        """
        使用大模型处理查询并调用可用的MCP工具 (Function Calling)
        """
        messages = [{"role": "user", "content": query}]

        available_tools = [{
            "type": "function",
            "function": {
                "name": tool.get("name"),
                "description": tool.get("description"),
                "parameters": tool.get("inputSchema")
            }
        } for tool in self.tools]

        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=available_tools
        )

        # 处理返回的内容
        content = response.choices[0]
        if content.finish_reason == "tool_calls":
            # 如果是需要使用工具，就解析工具
            tool_call = content.message.tool_calls[0]
            tool_name = tool_call.function.name
            tool_args = json.loads(tool_call.function.arguments)

            # 执行工具
            data = {"tool_name": tool_name, "tool_args": tool_args}
            result_resp = await self.session.post("http://localhost:8000/call_tool", json=data)
            result = await result_resp.json()
            print(f"\n\n[Calling tool {tool_name} with args {tool_args}]\n\n")

            # 将模型返回的调用哪个工具数据和工具执行完成后的数据都存入messages中
            messages.append(content.message.model_dump())
            messages.append({
                "role": "tool",
                "content": result.get("result"),
                "tool_call_id": tool_call.id,
            })

            # 将上面的结果再返回给大模型用于生成最终的结果
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            return response.choices[0].message.content

        return content.message.content

    async def chat_loop(self):
        """运行交互式聊天循环"""
        print("\n🤖 MCP客户端已启动！输入'quit'退出")
        while True:
            try:
                query = input("\n你: ").strip()
                if query.lower() == 'quit':
                    break

                response = await self.process_query(query)  # 发送用户输入到OpenAI API
                print(f"\n🤖 OpenAI: {response}")
            except Exception as e:
                print(f"\n⚠发生错误: {str(e)}")

    async def cleanup(self):
        """清理资源"""
        await self.session.close()


async def main():
    client = MCPClient()
    try:
        await client.connect_to_server()
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())