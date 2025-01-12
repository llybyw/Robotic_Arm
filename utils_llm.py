import requests
import json
import os
import dashscope

dashscope.api_key = "sk-76a64e55b5ff4b89b63eafeb81186784"


def send_request(messages, model='qwen-vl-max-0809'):
    """发送POST请求到指定的API, 并返回响应数据。"""
    print("Querying Qwen ...")
    response = dashscope.MultiModalConversation.call(model='qwen-vl-max-0809', messages=messages)

    if response.status_code == 200:
        return response
    else:
        print(f"Request failed with status code {response.status_code}: {response.text}")
        return None


def generate_plan(prompt_text):
    """
    调用Qwen2-vl 模型 API 来生成文本计划。
    参数:
    - prompt_text (str): 用于生成文本的 prompt。
    返回:
    - 生成的文本 (str)，或错误信息。
    """

    print("Start generating plan ...")

    messages = prompt_text
    # ToDO: 将原有的messages上加入prompt

    response_data = send_request(messages, model='qwen-vl-max-0809')
    response_dict = response_data

    content = response_dict['output']['choices'][0]['message']['content'][0]['text']
    return content if content else print('Failed to get response from Qwen2-VL')

def read_prompt(file_path):
    """从指定文件中读取prompt内容。"""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"Error: File {file_path} not found.")
        return None




    
