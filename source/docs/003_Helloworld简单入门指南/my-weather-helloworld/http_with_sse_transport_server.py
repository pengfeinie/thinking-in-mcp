import json
import asyncio
import httpx
from typing import Any
from fastapi import FastAPI, Request, HTTPException, Response
from sse_starlette.sse import EventSourceResponse
from mcp.server.fastmcp import FastMCP
import os
from dotenv import load_dotenv
import logging

# 配置日志
logging.basicConfig(level=logging.DEBUG)

# 加载.env文件，确保API Key受到保护
load_dotenv()

# 初始化 MCP 服务器
mcp = FastMCP("WeatherServer")
app = FastAPI()

# OpenWeather API 配置
OPENWEATHER_API_BASE = os.getenv("OPENWEATHER_API_BASE")  
OPEN_WEATHER_API_KEY = os.getenv("OPEN_WEATHER_API_KEY")  
USER_AGENT = os.getenv("OPEN_WEATHER_USER_AGENT")  


async def fetch_weather(city: str) -> dict[str, Any] | None:
    """
    从 OpenWeather API 获取天气信息。
    :param city: 城市名称（需使用英文，如 Beijing）
    :return: 天气数据字典；若出错返回包含 error 信息的字典
    """
    params = {
        "q": city,
        "appid": OPEN_WEATHER_API_KEY,
        "units": "metric",
        "lang": "zh_cn"
    }
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(OPENWEATHER_API_BASE, params=params, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()  # 返回字典类型
        except httpx.HTTPStatusError as e:
            return {"error": f"HTTP 错误: {e.response.status_code}"}
        except Exception as e:
            return {"error": f"请求失败: {str(e)}"}


def format_weather(data: dict[str, Any] | str) -> str:
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except Exception as e:
            return f"无法解析天气数据: {e}"
    # 如果数据中包含错误信息，直接返回错误提示
    if "error" in data:
        return f"⚠ {data['error']}"
    # 提取数据时做容错处理
    city = data.get("name", "未知")
    country = data.get("sys", {}).get("country", "未知")
    temp = data.get("main", {}).get("temp", "N/A")
    humidity = data.get("main", {}).get("humidity", "N/A")
    wind_speed = data.get("wind", {}).get("speed", "N/A")
    # weather 可能为空列表，因此用 [0] 前先提供默认字典
    weather_list = data.get("weather", [{}])
    description = weather_list[0].get("description", "未知")
    return (
        f"🌍 {city}, {country}\n"
        f"🌡 温度: {temp}°C\n"
        f"💧 湿度: {humidity}%\n"
        f"🌬 风速: {wind_speed} m/s\n"
        f"⛅ 天气: {description}\n"
    )


@mcp.tool()
async def query_weather(city: str) -> str:
    """
    输入指定城市的英文名称，返回今日天气查询结果。
    :param city: 城市名称（需使用英文）
    :return: 格式化后的天气信息
    """
    data = await fetch_weather(city)
    return format_weather(data)


@app.get("/connect")
async def connect(request: Request):
    async def event_generator():
        while True:
            if await request.is_disconnected():
                break
            yield {"data": json.dumps({"message": "Connected"})}
            await asyncio.sleep(1)
    return EventSourceResponse(event_generator())


@app.post("/call_tool")
async def call_tool(data: dict):
    tool_name = data.get("tool_name")
    tool_args = data.get("tool_args")
    try:
        logging.debug(f"调用工具: {tool_name}, 参数: {tool_args}")
        result = await mcp.call_tool(tool_name, tool_args)
        logging.debug(f"工具调用结果: {result}")
        if result and isinstance(result, list) and len(result) > 0 and hasattr(result[0], 'text'):
            response_data = {"result": result[0].text}
        else:
            logging.error("工具执行结果为空")
            response_data = {"result": None}
        # 设置正确的 Content-Type 头
        return Response(content=json.dumps(response_data), media_type="application/json")
    except Exception as e:
        logging.error(f"调用工具时出错: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/list_tools")
async def list_tools():
    try:
        tools = []
        # 使用 await 等待 mcp.list_tools() 协程执行完毕
        tool_instances = await mcp.list_tools()  
        for tool in tool_instances:
            tool_info = {
                "name": tool.name,
                "description": tool.description,
                "inputSchema": tool.inputSchema
            }
            tools.append(tool_info)
        return {"tools": tools}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)