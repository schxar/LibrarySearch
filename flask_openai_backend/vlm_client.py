import os
from openai import OpenAI

def create_vlm_client(api_key):
    """创建VLM客户端"""
    return OpenAI(
        api_key=api_key,
        base_url="https://ark.cn-beijing.volces.com/api/v3"
    )
