from openai import OpenAI
from typing import Dict, Any

def create_search_client(api_key: str) -> OpenAI:
    """创建搜索专用客户端"""
    return OpenAI(
        api_key=api_key,
        base_url="https://ark.cn-beijing.volces.com/api/v3/bots"
    )

def perform_search(query: str, client: OpenAI) -> Dict[str, Any]:
    """执行搜索请求"""
    response = client.chat.completions.create(
        model="bot-20250506042211-5bscp",
        messages=[
            {"role": "system", "content": "你是一个专业的搜索引擎"},
            {"role": "user", "content": f"请搜索以下内容：{query}"}
        ]
    )
    return {
        "content": response.choices[0].message.content,
        "model": "bot-20250506042211-5bscp"
    }
