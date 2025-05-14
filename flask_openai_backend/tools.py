"""工具定义模块，包含所有API工具的定义"""

# 初始化豆包客户端
import os
import pymysql
from openai import OpenAI

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '13380008373',
    'database': 'library',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# 初始化豆包客户端

with open(os.path.join(os.path.dirname(__file__), 'templates', 'doubao.txt'), 'r') as f:
    api_key = f.read().strip()
    
    
# 合并的客户端初始化代码
client = OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3",
    api_key=api_key
)

bot_client=OpenAI(
    base_url="https://ark.cn-beijing.volces.com/api/v3/bots",
    api_key=api_key
)

tools = [
    {
        "type": "function",
        "function": {
            "name": "google_cse_search",
            "description": "使用Google Custom Search Engine API执行搜索",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "搜索关键词"},
                    "cx": {"type": "string", "description": "搜索引擎ID", "default": "b7a4dfc41bb40428c"},
                    "num": {"type": "integer", "description": "返回结果数量", "default": 5}
                },
                "required": ["query"]
            }
        }
    },
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
    },
    {
        "type": "function",
        "function": {
            "name": "zlib_search",
            "description": "在在线图书馆中搜索图书",
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
            "name": "get_dlink",
            "description": "获取图书的下载链接",
            "parameters": {
                "type": "object",
                "properties": {
                    "book_url": {"type": "string", "description": "图书的URL地址"}
                },
                "required": ["book_url"]
            }
        }
    }
]
