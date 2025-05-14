"""工具定义模块，包含所有API工具的定义"""

# 初始化豆包客户端
import os
import pymysql
from openai import OpenAI
import requests
from vlm import vlm_service

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
            "description": "在在线图书馆中搜索图书，返回书名和下载链接",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string", 
                        "description": "搜索关键词"
                    },
                    "result_type": {
                        "type": "string", 
                        "enum": ["summary", "detailed"], 
                        "default": "summary",
                        "description": "结果类型：summary返回简要信息，detailed返回详细信息"
                    }
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
    },
    {
        "type": "function",
        "function": {
            "name": "context_retrieval",
            "description": "Perform semantic search based on text embeddings of the user request",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The user's original request for context retrieval"
                    },
                    "context": {
                        "type": "array",
                        "description": "The full conversation context"
                    }
                },
                "required": ["query", "context"]
            }
        }
    }
]

import json

def evaluate_tool_results(context: list, tool_response: str):
    """评估工具结果是否满足用户需求"""
    print("开始评估工具结果...")
    try:
        # 1. 准备上下文数据
        context_str = json.dumps(context, ensure_ascii=False)
        print(f"原始上下文长度: {len(context_str)}字符")
        
        # 2. 分块处理(安全阈值设为3000字符)
        chunk_size = 3000
        chunks = [context_str[i:i+chunk_size] for i in range(0, len(context_str), chunk_size)]
        print(f"将上下文分成{len(chunks)}块进行处理")
        
        # 3. 生成分块嵌入
        all_embeddings = []
        for i, chunk in enumerate(chunks):
            print(f"正在处理第{i+1}/{len(chunks)}块...")
            try:
                embedding_response = client.embeddings.create(
                    model="doubao-embedding-large-text-240915",
                    input=[chunk],
                    encoding_format="float"
                )
                all_embeddings.extend(embedding_response.data[0].embedding)
            except Exception as e:
                print(f"第{i+1}块嵌入生成失败: {str(e)}")
                continue
                
        if not all_embeddings:
            raise Exception("所有分块嵌入生成失败")
            
        print(f"成功生成总维度{len(all_embeddings)}的嵌入向量")
        embedding = all_embeddings
        
        evaluation_prompt = f"""
        请根据以下用户请求上下文(嵌入维度:{len(embedding)})和工具返回结果，生成一个完整、流畅的最终回答：
        
        用户原始请求：
        {json.dumps(context, ensure_ascii=False)}
        
        工具返回的原始结果：
        {tool_response}
        
        请：
        1. 保持原始信息的准确性
        2. 用自然语言整合所有相关信息
        3. 确保回答流畅易读
        4. 不要添加额外的评估或建议
        """
        
        evaluation = client.chat.completions.create(
            model="doubao-1-5-thinking-pro-250415",
            messages=[{"role": "user", "content": evaluation_prompt}]
        )
        
        print("评估结果:", evaluation.choices[0].message.content)
        return evaluation.choices[0].message.content
        
    except Exception as e:
        print(f"评估工具结果失败: {str(e)}")
        return "评估工具结果时发生错误"

def context_retrieval(query: str, context: list, request=None):
    """执行上下文检索，基于文本嵌入和最新用户请求生成响应"""
    try:
        print("开始上下文检索处理...")
        
        # 1. 准备上下文数据
        context_str = json.dumps(context, ensure_ascii=False)
        print(f"原始上下文长度: {len(context_str)}字符")
        
        # 2. 分块处理(安全阈值设为3000字符)
        chunk_size = 3000
        chunks = [context_str[i:i+chunk_size] for i in range(0, len(context_str), chunk_size)]
        print(f"将上下文分成{len(chunks)}块进行处理")
        
        # 3. 生成分块嵌入
        all_embeddings = []
        for i, chunk in enumerate(chunks):
            print(f"正在处理第{i+1}/{len(chunks)}块...")
            try:
                embedding_response = client.embeddings.create(
                    model="doubao-embedding-large-text-240915",
                    input=[chunk],
                    encoding_format="float"
                )
                all_embeddings.extend(embedding_response.data[0].embedding)
            except Exception as e:
                print(f"第{i+1}块嵌入生成失败: {str(e)}")
                continue
                
        if not all_embeddings:
            raise Exception("所有分块嵌入生成失败")
            
        print(f"成功生成总维度{len(all_embeddings)}的嵌入向量")
        
        # 4. 构建提示(限制长度)
        context_summary = json.dumps(
            [msg for msg in context if msg['role'] != 'user'][-3:], 
            ensure_ascii=False
        )[:2000]  # 限制摘要长度
        
        prompt = f"""
        基于以下上下文(嵌入维度:{len(all_embeddings)})和最新用户请求，生成回答：
        
        最近3条系统消息:
        {context_summary}
        
        用户最新请求:
        {query}
        
        请根据上下文提供准确、简洁的回答。
        """
        print(f"提示长度: {len(prompt)}字符")
        
        # 5. 调用模型生成响应
        response = client.chat.completions.create(
            model="doubao-1-5-thinking-pro-250415",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000  # 限制响应长度
        )
        
        result = response.choices[0].message.content
        
        # 评估结果
        if request and request.content_type == 'application/json':
            data = request.get_json()
            evaluation = evaluate_tool_results(context, result)
            return {
                "content": evaluation,
                "raw_response": response
            }
        
        print("上下文检索完成")
        return result
        
    except Exception as e:
        error_msg = f"上下文检索时发生错误: {str(e)}"
        print(error_msg)
        return error_msg

def process_image_data(image_data: str, task: str = "describe", request=None):
    """处理图片分析请求"""
    print(f"调用VLM服务分析图片，任务类型: {task}")
    result = vlm_service.analyze_image(image_data, task)
    
    # 评估结果
    if request and request.content_type == 'application/json':
        data = request.get_json()
        context = data.get('messages', [])
        evaluation = evaluate_tool_results(context, json.dumps(result, ensure_ascii=False))
        return {
            "content": evaluation,
            "raw_results": result
        }
    
    return result

def process_url(url: str, request=None):
    """处理URL分析请求"""
    print(f"调用模型: bot-20250506034902-4psdn, 分析URL: {url[:100]}...")
    
    # 使用selenium获取页面源码
    from selenium import webdriver
    from selenium.webdriver.chrome.service import Service
    from webdriver_manager.chrome import ChromeDriverManager
    from selenium.webdriver.chrome.options import Options
    
    try:
        print("正在使用selenium获取页面源码...")
        options = Options()
        # 使用项目内的持久化profile目录
        profile_dir = os.path.join(os.path.dirname(__file__), "chrome-profiles", "GetDLinkImpl")
        options.add_argument(f"user-data-dir={profile_dir}")
        # Remove "--headless" if you want to see browser actions
        # options.add_argument("--headless") 
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.get(url)
        page_source = driver.page_source
        driver.quit()
        
        print("页面源码获取成功，开始解析...")
        # 将页面源码与URL一起发送给模型
        response = bot_client.chat.completions.create(
            model="bot-20250506034902-4psdn",
            messages=[
                {
                    "role": "system", 
                    "content": "你是一个专业的URL内容解析器，请解析用户提供的URL内容和页面源码，返回标题和主要内容"
                },
                {"role": "user", "content": f"请分析以下URL: {url}\n页面源码:\n{page_source[:10000]}"}
            ],
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "url_analysis"}}
        )
        
        # 评估结果
        if request and request.content_type == 'application/json':
            data = request.get_json()
            context = data.get('messages', [])
            evaluation = evaluate_tool_results(context, json.dumps(response, ensure_ascii=False))
            return {
                "content": evaluation,
                "raw_response": response
            }
        
        return response
        
    except Exception as e:
        print(f"selenium获取页面源码失败: {str(e)}，回退到原始URL分析")
        response = bot_client.chat.completions.create(
            model="bot-20250506034902-4psdn",
            messages=[
                {
                    "role": "system", 
                    "content": "你是一个专业的URL内容解析器，请解析用户提供的URL内容，返回标题和主要内容"
                },
                {"role": "user", "content": f"请分析以下URL: {url}"}
            ],
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "url_analysis"}}
        )
        
        # 评估结果
        if request and request.content_type == 'application/json':
            data = request.get_json()
            context = data.get('messages', [])
            evaluation = evaluate_tool_results(context, json.dumps(response, ensure_ascii=False))
            return {
                "content": evaluation,
                "raw_response": response
            }
        
        return response

def process_dlink_request(book_url: str, request=None):
    """处理下载链接请求"""
    print(f"调用GetDLinkController获取下载链接: {book_url[:100]}...")
    try:
        # 调用GetDLinkController的/getdlink接口
        response = requests.post(
            "http://localhost:8080/getdlink",
            json={"bookUrl": book_url},
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        
        if "downloadLink" in result:
            print(f"成功获取下载链接: {result['downloadLink']}")
            # 评估结果
            if request and request.content_type == 'application/json':
                data = request.get_json()
                context = data.get('messages', [])
                evaluation = evaluate_tool_results(context, json.dumps(result, ensure_ascii=False))
                return {
                    "content": evaluation,
                    "raw_response": result
                }
            
            return {
                "content": result["downloadLink"],
                "raw_response": result
            }
        else:
            error_msg = result.get("error", "Unknown error")
            print(f"获取下载链接失败: {error_msg}")
            return {
                "error": error_msg,
                "raw_response": result
            }
            
    except requests.exceptions.RequestException as req_e:
        print(f"GetDLinkController请求失败: {str(req_e)}")
        return {"error": f"下载服务不可用: {str(req_e)}"}
    except Exception as e:
        print(f"处理get_dlink时发生未知错误: {str(e)}")
        return {"error": f"处理下载请求时发生错误: {str(e)}"}

def process_zlib_search(query: str, result_type: str = "summary", request=None):
    """处理在线图书馆搜索请求"""
    print(f"调用SearchController搜索在线图书馆: {query[:100]}...")
    try:
        # 调用SearchController的/search接口
        response = requests.get(
            "http://localhost:8080/search",
            params={"q": query},
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        response.raise_for_status()
        results = response.json()
        print(f"成功获取搜索结果，共{len(results.get('results', []))}条记录")
        
        try:
            # 生成embedding（分块处理）
            print("----- 生成embedding（分块处理）-----")
            embedding_info = ""
            try:
                results_str = json.dumps(results, ensure_ascii=False)
                chunk_size = 3000  # 安全阈值，避免超过4096限制
                chunks = [results_str[i:i+chunk_size] for i in range(0, len(results_str), chunk_size)]
                
                all_embeddings = []
                for i, chunk in enumerate(chunks):
                    print(f"正在处理第{i+1}/{len(chunks)}块embedding...")
                    embedding_resp = client.embeddings.create(
                        model="doubao-embedding-large-text-240915",
                        input=[chunk],
                        encoding_format="float"
                    )
                    all_embeddings.extend(embedding_resp.data[0].embedding)
                
                embedding_info = f"\nEmbedding总维度: {len(all_embeddings)} (分{len(chunks)}块处理)"
            except Exception as e:
                print(f"生成embedding失败: {str(e)}")
                embedding_info = ""
            
            # 优化prompt生成，限制输入长度
            results_str = json.dumps(results, ensure_ascii=False)
            if len(results_str) > 3000:  # 预留空间给其他prompt内容
                # 只保留前10条结果
                limited_results = {"results": results.get("results", [])[:10]}
                results_str = json.dumps(limited_results, ensure_ascii=False)
                print(f"输入过长，已截断至前10条结果，当前长度: {len(results_str)}")
            
            # 调用doubao模型处理结果
            prompt = f"输出格式为先是书名, 然后是book_url,请从以下JSON数据中提取书名和链接:\n{results_str}{embedding_info}"
            print(f"调用doubao模型处理结果,prompt长度: {len(prompt)}")
            
            try:
                doubao_response = client.chat.completions.create(
                    model="doubao-1-5-thinking-pro-250415",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0,
                    timeout=60
                )
            except Exception as e:
                print(f"doubao模型处理失败: {str(e)}")
                # 模型调用失败时返回原始结果
                return {
                    "content": json.dumps([
                        {"title": item.get("title"), "book_url": item.get("book_url")} 
                        for item in results.get("results", [])
                    ], ensure_ascii=False),
                    "raw_results": results
                }
            
            # 评估结果
            if request and request.content_type == 'application/json':
                data = request.get_json()
                context = data.get('messages', [])
                evaluation = evaluate_tool_results(context, doubao_response.choices[0].message.content)
                return {
                    "content": evaluation,
                    "raw_results": results
                }
            
            return {
                "content": doubao_response.choices[0].message.content,
                "raw_results": results
            }
        except Exception as model_e:
            print(f"doubao模型处理失败: {str(model_e)}")
            # 模型调用失败时返回原始结果
            return {
                "content": json.dumps([
                    {"title": item.get("title"), "book_url": item.get("book_url")} 
                    for item in results.get("results", [])
                ], ensure_ascii=False),
                "raw_results": results
            }
            
    except requests.exceptions.RequestException as req_e:
        print(f"SearchController请求失败: {str(req_e)}")
        return {"error": f"搜索服务不可用: {str(req_e)}"}
    except Exception as e:
        print(f"处理zlib_search时发生未知错误: {str(e)}")
        return {"error": f"处理搜索请求时发生错误: {str(e)}"}

def process_google_cse(query: str, cx: str = "b7a4dfc41bb40428c", num: int = 5, request=None):
    """处理Google CSE搜索请求"""
    print(f"调用Google CSE API搜索: {query[:100]}...")
    try:
        # 调用Google CSE API
        response = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params={
                "q": query,
                "cx": cx,
                "key": "AIzaSyCa4mngFulV3OzlW3Dw2Y-4xAJ3DsupgMg",
                "num": num
            },
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        response.raise_for_status()
        results = response.json()
        # 打印原始JSON输出
        print("Google CSE原始JSON输出:")
        print(json.dumps(results, indent=2, ensure_ascii=False))
        print(f"成功获取Google CSE搜索结果，共{len(results.get('items', []))}条记录")
        
        # 调用豆包bot-20250506042211-5bscp获取搜索结果
        print(f"调用豆包bot-20250506042211-5bscp搜索: {query[:100]}...")
        doubao_response = bot_client.chat.completions.create(
            model="bot-20250506042211-5bscp",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的搜索引擎，请根据用户查询返回相关搜索结果"
                },
                {
                    "role": "user",
                    "content": query
                }
            ]
        )
        doubao_results = doubao_response.choices[0].message.content
        print(f"豆包搜索结果: {doubao_results[:200]}...")
        
        # 合并Google CSE和豆包搜索结果
        combined_results = {
            "google_cse": results,
            "doubao": doubao_results
        }

        # 如果是JSON请求，评估结果是否满足用户需求
        if request and request.content_type == 'application/json':
            data = request.get_json()
            context = data.get('messages', [])
            evaluation = evaluate_tool_results(context, json.dumps(combined_results, ensure_ascii=False))
            return {
                "content": evaluation,
                "raw_results": results
            }
        
        # 生成embedding（分块处理）
        print("----- 生成embedding（分块处理）-----")
        embedding_info = ""
        try:
            results_str = json.dumps(combined_results, ensure_ascii=False)
            chunk_size = 3000  # 安全阈值，避免超过4096限制
            chunks = [results_str[i:i+chunk_size] for i in range(0, len(results_str), chunk_size)]
            
            all_embeddings = []
            for i, chunk in enumerate(chunks):
                print(f"正在处理第{i+1}/{len(chunks)}块embedding...")
                embedding_resp = client.embeddings.create(
                    model="doubao-embedding-large-text-240915",
                    input=[chunk],
                    encoding_format="float"
                )
                all_embeddings.extend(embedding_resp.data[0].embedding)
            
            embedding_info = f"\nEmbedding总维度: {len(all_embeddings)} (分{len(chunks)}块处理)"
        except Exception as e:
            print(f"生成embedding失败: {str(e)}")
            embedding_info = ""
        
            # 调用doubao模型处理结果
            prompt = f"请总结以下Google和豆包搜索结果:\nGoogle CSE结果:\n{json.dumps(results, ensure_ascii=False)}\n豆包搜索结果:\n{doubao_results}{embedding_info}"
            print(f"调用doubao模型处理结果,prompt长度: {len(prompt)}")
            
            try:
                doubao_response = client.chat.completions.create(
                    model="doubao-1-5-lite-32k-250115",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0,
                    timeout=60
                )
                
                # 如果是JSON请求，评估结果是否满足用户需求
                if request and request.content_type == 'application/json':
                    data = request.get_json()
                    context = data.get('messages', [])
                    evaluation = evaluate_tool_results(context, doubao_response.choices[0].message.content)
                    return {
                        "content": evaluation,
                        "raw_results": results
                    }
                
                return {
                    "content": doubao_response.choices[0].message.content,
                    "raw_results": results
                }
            except Exception as e:
                print(f"doubao模型处理失败: {str(e)}")
                return {
                    "content": json.dumps([
                        {
                            "title": item.get("title"), 
                            "link": item.get("link"),
                            "snippet": item.get("snippet")
                        } 
                        for item in results.get("items", [])
                    ], ensure_ascii=False),
                    "raw_results": results
                }
    except requests.exceptions.RequestException as req_e:
        print(f"Google CSE API请求失败: {str(req_e)}")
        return {"error": f"Google搜索服务不可用: {str(req_e)}"}
    except Exception as e:
        print(f"处理google_cse时发生未知错误: {str(e)}")
        return {"error": f"处理Google搜索请求时发生错误: {str(e)}"}
