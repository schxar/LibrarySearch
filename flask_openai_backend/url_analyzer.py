import re
from openai import OpenAI
from typing import Dict, Any

def create_url_client(api_key: str) -> OpenAI:
    """创建URL分析专用客户端"""
    return OpenAI(
        api_key=api_key,
        base_url="https://ark.cn-beijing.volces.com/api/v3/bots"
    )

def analyze_url(url: str, client: OpenAI) -> Dict[str, Any]:
    """执行URL内容分析"""
    if not re.match(r'^https?://', url):
        raise ValueError("Invalid URL format")
    
    response = client.chat.completions.create(
        model="bot-20250506034902-4psdn",
        messages=[
            {"role": "system", "content": "你是一个专业的URL内容解析器"},
            {"role": "user", "content": f"请解析以下URL内容：{url}"}
        ]
    )
    return {
        "content": response.choices[0].message.content,
        "model": "bot-20250506034902-4psdn"
    }
