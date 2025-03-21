import asyncio
import os
from openai import OpenAI
from dotenv import load_dotenv
from mcp import ClientSession
from contextlib import AsyncExitStack

#加载.env文件,确保API KEY受到保护
load_dotenv()

class MCPClient:
    def __init__(self):
        """初始化 MCP 客户端"""
        self.exit_stack = AsyncExitStack()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("BASE_URL")
        self.model = os.getenv("MODEL")
        
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY is not here, please setup into .env file.")
        
        self.client = OpenAI(api_key=self.openai_api_key, base_url=self.base_url)
        
    async def process_query(self, query: str) -> str:
        """调用 OpenAI API 处理用户查询"""
        messages = [{"role": "system", "content": "你是一个智能助手，帮助用户回答问题。"},
                    {"role": "user", "content": query}]
        
        try:
            # 调用 OpenAI API
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.client.chat.completions.create(
                    model=self.model,
                    messages=messages
                )
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"调用 OpenAI API 时出错: {str(e)}"

    async def chat_loop(self):
        """运行交互式聊天循环"""
        print("\nMCP 客户端已启动！输入 'quit' 退出")

        while True:
            try:
                query = input("\nQuery: ").strip()
                if query.lower() == 'quit':
                    break
                response = await self.process_query(query) # 发送用户输入到 DeepSeek
                print(f"\nDeepSeek: {response}")
            except Exception as e:
                print(f"\n发生错误: {str(e)}")

    async def cleanup(self):
        """清理资源"""
        await self.exit_stack.aclose()


async def main():
    client = MCPClient()
    try:
        await client.chat_loop()
    finally:
        await client.cleanup()


if __name__ == "__main__":
    asyncio.run(main())