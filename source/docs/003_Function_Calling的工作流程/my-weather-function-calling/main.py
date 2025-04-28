import asyncio
import os
import json
from typing import Optional
from contextlib import AsyncExitStack
from openai import OpenAI
from dotenv import load_dotenv
import requests

# 加载.env文件，确保API Key受到保护
load_dotenv()

# OpenWeather API 配置
OPENWEATHER_API_BASE = os.getenv("OPENWEATHER_API_BASE")
OPEN_WEATHER_API_KEY = os.getenv("OPEN_WEATHER_API_KEY")
USER_AGENT = os.getenv("OPEN_WEATHER_USER_AGENT")

# 从环境变量中获取 API 密钥
openai_api_key = os.getenv("OPENAI_API_KEY")

functions = [
    {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The name of the location to get the weather for."
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"]
                }
            },
            "required": ["location"]
        }
    }
]


def get_current_weather(location):
    url = f"{OPENWEATHER_API_BASE}?q={location}&appid={OPEN_WEATHER_API_KEY}&units=metric&lang=zh_cn"
    print(url)
    try:
        response = requests.get(url, headers={"User-Agent": USER_AGENT})
        data = response.json()
        if response.status_code == 200:
            temperature = data['main']['temp']
            description = data['weather'][0]['description']
            humidity = data['main']['humidity']
            wind_speed = data['wind']['speed']
            return f"当前温度为：{temperature}℃\n天气状况：{description}\n湿度：{humidity}%\n风速：{wind_speed} m/s"
        else:
            return f"无法获取到该城市的天气"
    except requests.exceptions.RequestException as e:
        print(e)
        return f"请求失败，请稍后再试"


def get_response(client, user_query):
    response = client.chat.completions.create(
        model="deepseek-chat",  
        messages=[
            {"role": "user", "content": user_query}  # 使用用户消息
        ],
        functions=functions,
        function_call="auto"
    )
    message = response.choices[0].message
    print(message.function_call)

    if message.function_call:
        function_name = message.function_call.name

        if function_name == "get_current_weather":
            arguments = json.loads(message.function_call.arguments)
            location = arguments.get("location")
            return get_current_weather(location)

    return response.choices[0].message.content


if __name__ == "__main__":
    client = OpenAI(api_key=openai_api_key, base_url="https://api.deepseek.com")
    while True:
        user_input = input("Enter your query: ")
        if user_input.lower() in ['退出', 'quit', 'exit']:
            print("Bye")
            break
        print(get_response(client, user_input))
        print("-" * 50 + "\n")