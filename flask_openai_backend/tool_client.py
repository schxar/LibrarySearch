import os
import re
import base64
from openai import OpenAI
from .url_analyzer import create_url_client, analyze_url
from .search_client import create_search_client, perform_search
from .vlm_client import create_vlm_client, process_image

# 初始化主客户端
client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=os.environ.get("ARK_API_KEY")
)

# 创建专用工具客户端
url_tool = create_url_client(os.environ.get("ARK_API_KEY"))
search_tool = create_search_client(os.environ.get("ARK_API_KEY"))
vlm_tool = create_vlm_client(os.environ.get("ARK_API_KEY"))

# 工具定义
tools = [
    {
        "type": "function",
        "function": {
            "name": "url_analysis",
            "description": "解析URL内容并提取关键信息",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "需要分析的URL"},
                    "detail_level": {"type": "string", "enum": ["summary", "full"], "default": "summary"}
                },
                "required": ["url"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "执行网络搜索并返回结果",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"},
                    "result_type": {"type": "string", "enum": ["summary", "detailed"], "default": "summary"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "image_analysis",
            "description": "分析图片内容，支持DATAURI格式的base64编码",
            "parameters": {
                "type": "object",
                "properties": {
                    "image_data": {"type": "string", "description": "DATAURI格式的base64编码图片"},
                    "task": {"type": "string", "enum": ["describe", "analyze"], "default": "describe"}
                },
                "required": ["image_data"]
            }
        }
    }
]

def process_message(prompt: str):
    """处理用户消息，自动判断是否使用工具"""
    response = client.chat.completions.create(
        model="doubao-1-5-lite-32k-250115",
        messages=[{"role": "user", "content": prompt}],
        tools=tools,
        tool_choice="auto"  # 由模型决定是否调用工具
    )
    return response

def process_image_data(image_data: str, task: str = "describe"):
    """处理DATAURI格式的base64图片"""
    if not image_data.startswith("data:image/"):
        raise ValueError("Invalid DATAURI format")
    
    # 提取base64编码部分
    base64_str = image_data.split(",")[1]
    try:
        image_bytes = base64.b64decode(base64_str)
        return process_image(image_bytes, vlm_tool, task)
    except Exception as e:
        raise ValueError(f"Image processing failed: {str(e)}")
