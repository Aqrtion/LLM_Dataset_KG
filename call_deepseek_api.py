import json
import os
from openai import OpenAI
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 初始化 API 客户端
API_KEY = os.getenv("DEEPSEEK_API_KEY")
client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

def call_deepseek_api(system_prompt, user_prompt, input_message):
    """
    调用 deepseek
    :param system_prompt: 系统提示词
    :param user_prompt: 用户提示词
    :param input_message: 输入信息
    :return: deepseek 响应消息 (文本格式)
    """
    print("Sending request to DeepSeek API...")

    completion = client.chat.completions.create(
        model='deepseek-reasoner',
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt.replace("{input}", input_message)}
        ]
    )
    print("Received response from DeepSeek API.")

    return completion.choices[0].message.content

def call_deepseek_api_with_time(system_prompt, user_prompt, input_message, current_time):
    """
    调用 deepseek
    :param system_prompt: 系统提示词
    :param user_prompt: 用户提示词
    :param input_message: 输入信息
    :param current_time: 表示当前时间的字符串, 用于区分实体
    :return: deepseek 响应消息 (文本格式)
    """
    print("Sending request to DeepSeek API...")

    completion = client.chat.completions.create(
        model='deepseek-reasoner',
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt.replace("{input}", input_message).replace("{time}", current_time)}
        ]
    )
    print("Received response from DeepSeek API.")

    return completion.choices[0].message.content

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Call DeepSeek API")
    parser.add_argument("--system_prompt", help="System prompt to use")
    parser.add_argument("--user_prompt", help="User prompt to use")
    parser.add_argument("--input_message", help="Input message to send to the API")
    args = parser.parse_args()

    result = call_deepseek_api(args.system_prompt, args.user_prompt, args.input_message)
    if result is not None:
        print("API Result:")
        print(result)
    else:
        print("API call failed.")
