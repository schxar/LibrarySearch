"""工具定义模块，包含所有API工具的定义"""

# 初始化豆包客户端
import os
import pymysql
from openai import OpenAI
import requests
import urllib
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
            "description": "使用Google Custom Search Engine API执行搜索,解析URL内容并提取关键信息,支持搜索url和各种网页",
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
            model="doubao-1-5-thinking-vision-pro-250428",
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
            model="doubao-1-5-thinking-vision-pro-250428",
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
                    model="doubao-1-5-thinking-vision-pro-250428",
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

def evaluate_tools_for_url(query, cse_results=None, doubao_results=None, url_analysis=None, page_analysis=None):
    """评估各工具对特定URL的价值"""
    print(f"评估URL: {query}")
    
    evaluations = []
    
    # 评估CSE搜索
    cse_eval_prompt = f"""
    基于以下Google CSE搜索结果，评估对URL {query} 使用Google CSE搜索是否有价值？
    搜索结果: {json.dumps(cse_results, ensure_ascii=False)[:2000] if cse_results else "无结果"}
    请根据搜索结果的相关性和质量判断，只需回答1(有价值)或0(无价值)
    """
    cse_evaluation = client.chat.completions.create(
        model="doubao-1-5-lite-32k-250115",
        messages=[{"role": "user", "content": cse_eval_prompt}],
        temperature=0
    )
    cse_result = cse_evaluation.choices[0].message.content.strip()
    evaluations.append('1' if cse_result not in ['0', '1'] else cse_result)
    
    # 评估豆包搜索
    doubao_eval_prompt = f"""
    基于以下豆包搜索结果，评估对URL {query} 使用豆包搜索是否有价值？
    搜索结果: {doubao_results[:2000] if doubao_results else "无结果"}
    请根据搜索结果的相关性和质量判断，只需回答1(有价值)或0(无价值)
    """
    doubao_evaluation = client.chat.completions.create(
        model="doubao-1-5-lite-32k-250115",
        messages=[{"role": "user", "content": doubao_eval_prompt}],
        temperature=0
    )
    doubao_result = doubao_evaluation.choices[0].message.content.strip()
    evaluations.append('1' if doubao_result not in ['0', '1'] else doubao_result)
    
    # 评估URL分析
    url_eval_prompt = f"""
    基于以下URL分析结果，评估对URL {query} 使用豆包URL分析是否有价值？
    分析结果: {url_analysis[:2000] if url_analysis else "无结果"}
    请根据分析结果的深度和有用性判断，只需回答1(有价值)或0(无价值)
    """
    url_evaluation = client.chat.completions.create(
        model="doubao-1-5-lite-32k-250115",
        messages=[{"role": "user", "content": url_eval_prompt}],
        temperature=0
    )
    url_result = url_evaluation.choices[0].message.content.strip()
    evaluations.append('1' if url_result not in ['0', '1'] else url_result)
    
    # 评估页面分析
    page_eval_prompt = f"""
    基于以下页面分析结果，评估对URL {query} 使用selenium页面分析是否有价值？
    分析结果: {page_analysis[:2000] if page_analysis else "无结果"}
    请根据分析结果的深度和有用性判断，只需回答1(有价值)或0(无价值)
    """
    page_evaluation = client.chat.completions.create(
        model="doubao-1-5-lite-32k-250115",
        messages=[{"role": "user", "content": page_eval_prompt}],
        temperature=0
    )
    page_result = page_evaluation.choices[0].message.content.strip()
    evaluations.append('1' if page_result not in ['0', '1'] else page_result)
    
    result = " ".join(evaluations)
    print(f"评估结果: {result}")
    return result

def load_cse_config():
    """加载CSE配置"""
    config_path = os.path.join(os.path.dirname(__file__), 'CseConfig.txt')
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            return json.load(f)
    return {}

def save_cse_config(config):
    """保存CSE配置"""
    config_path = os.path.join(os.path.dirname(__file__), 'CseConfig.txt')
    with open(config_path, 'w') as f:
        json.dump(config, f)

def is_url(input_str):
    """检查输入是否为URL"""
    try:
        result = urllib.parse.urlparse(input_str)
        return all([result.scheme, result.netloc])
    except:
        return False

def get_main_domain(url):
    """提取主域名(包含scheme)"""
    try:
        parsed = urllib.parse.urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            return url
        return f"{parsed.scheme}://{parsed.netloc}"
    except:
        return url

def process_google_cse(query: str, cx: str = "b7a4dfc41bb40428c", num: int = 5, request=None, 
                      config: str = None):
    """处理Google CSE搜索请求
    Args:
        query: 搜索关键词或URL
        cx: 搜索引擎ID
        num: 返回结果数量
        request: 请求对象
        config: 配置选项，格式为"是否使用豆包搜索 是否使用CSE搜索 是否使用豆包URL分析 是否使用selenium分析"
                (0表示不使用，1表示使用)
    """
    print(f"调用Google CSE API搜索: {query[:100]}...")
    
    # 解析配置选项
    use_doubao_search = 1
    use_cse_search = 1
    use_doubao_url_analysis = 1
    use_selenium_analysis = 1
    
    # 如果是URL，检查是否有配置
    if is_url(query):
        main_domain = get_main_domain(query)
        cse_config = load_cse_config()
        if main_domain in cse_config:
            config = cse_config[main_domain]
            if config:
                try:
                    config_parts = config.split()
                    if len(config_parts) >= 4:
                        use_doubao_search = int(config_parts[0])
                        use_cse_search = int(config_parts[1])
                        use_doubao_url_analysis = int(config_parts[2])
                        use_selenium_analysis = int(config_parts[3])
                except Exception as e:
                    print(f"解析配置选项失败: {str(e)}, 使用默认配置")
        try:
            config_parts = config.split()
            if len(config_parts) >= 4:
                use_doubao_search = int(config_parts[0])
                use_cse_search = int(config_parts[1])
                use_doubao_url_analysis = int(config_parts[2])
                use_selenium_analysis = int(config_parts[3])
        except Exception as e:
            print(f"解析配置选项失败: {str(e)}, 使用默认配置")
    
    # 处理Google CSE搜索
    results = {}
    if use_cse_search:
        try:
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
            print("Google CSE原始JSON输出:")
            print(json.dumps(results, indent=2, ensure_ascii=False))
            print(f"成功获取Google CSE搜索结果，共{len(results.get('items', []))}条记录")
        except requests.exceptions.RequestException as req_e:
            print(f"Google CSE API请求失败: {str(req_e)}")
            if not use_doubao_search:
                return {"error": f"Google搜索服务不可用: {str(req_e)}"}
    
    # 处理豆包搜索
    doubao_results = None
    if use_doubao_search:
        try:
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
        except Exception as e:
            print(f"豆包搜索失败: {str(e)}")
    
    # 检查query是否是URL
    url_analysis = None
    page_analysis = None
    try:
        parsed = urllib.parse.urlparse(query)
        if all([parsed.scheme, parsed.netloc]):
            # URL分析
            if use_doubao_url_analysis:
                try:
                    print("检测到URL输入，调用bot进行URL解析...")
                    url_response = bot_client.chat.completions.create(
                        model="bot-20250506042211-5bscp",
                        messages=[
                            {
                                "role": "system",
                                "content": "你是一个专业的URL内容解析器，请解析用户提供的URL内容"
                            },
                            {
                                "role": "user",
                                "content": f"请分析以下URL: {query}"
                            }
                        ]
                    )
                    url_analysis = url_response.choices[0].message.content
                    print(f"URL解析结果: {url_analysis[:200]}...")
                except Exception as e:
                    print(f"URL分析失败: {str(e)}")
            
            # Selenium分析
            if use_selenium_analysis:
                try:
                    print("启动selenium获取网页内容...")
                    from selenium import webdriver
                    from selenium.webdriver.chrome.options import Options
                    
                    profile_dir = os.path.join(os.path.dirname(__file__), "chrome-profiles", "GetDLinkImpl")
                    os.makedirs(profile_dir, exist_ok=True)
                    
                    options = Options()
                    options.add_argument(f"user-data-dir={profile_dir}")
                    options.add_argument("--headless")
                    options.add_argument("--disable-gpu")
                    options.add_argument("--no-sandbox")
                    
                    driver = webdriver.Chrome(options=options)
                    try:
                        driver.get(query)
                        
                        # 添加显式等待，确保页面完全加载
                        from selenium.webdriver.support.ui import WebDriverWait
                        from selenium.webdriver.support import expected_conditions as EC
                        
                        # 等待页面标题不为空（基本加载完成）
                        WebDriverWait(driver, 30).until(
                            lambda d: d.title != ""
                        )
                        
                        # 等待主要DOM元素加载完成
                        WebDriverWait(driver, 30).until(
                            EC.presence_of_element_located(("xpath", "//body"))
                        )
                        
                        # 等待jQuery/AJAX请求完成（如果页面使用jQuery）
                        try:
                            WebDriverWait(driver, 30).until(
                                lambda d: d.execute_script("return jQuery.active == 0")
                            )
                        except:
                            pass  # 页面未使用jQuery则忽略
                            
                        # 等待页面完全加载
                        WebDriverWait(driver, 30).until(
                            lambda d: d.execute_script("return document.readyState == 'complete'")
                        )
                        
                        page_content = driver.page_source
                        print(f"获取到网页内容，长度: {len(page_content)}字符")
                        
                        if page_content and use_doubao_url_analysis:
                            print("调用doubao模型分析网页内容...")
                            page_analysis_resp = client.chat.completions.create(
                                model="doubao-1-5-lite-32k-250115",
                                messages=[
                                    {
                                        "role": "system",
                                        "content": "你是一个专业的网页内容分析器，请分析以下网页内容"
                                    },
                                    {
                                        "role": "user",
                                        "content": f"请分析以下网页内容:\n{page_content[:10000]}"
                                    }
                                ],
                                temperature=0,
                                timeout=60
                            )
                            page_analysis = page_analysis_resp.choices[0].message.content
                            print(f"网页内容分析结果: {page_analysis[:200]}...")
                    finally:
                        driver.quit()
                except Exception as e:
                    print(f"Selenium分析失败: {str(e)}")
    except Exception as e:
        print(f"URL处理时发生错误: {str(e)}")
    
    # 合并结果
    combined_results = {
        "google_cse": results if use_cse_search else "N/A",
        "doubao": doubao_results if use_doubao_search else "N/A",
        "url_analysis": url_analysis if use_doubao_url_analysis else "N/A",
        "page_analysis": page_analysis if use_selenium_analysis and use_doubao_url_analysis else "N/A"
    }

    # 如果是新URL且没有配置，则在生成结果后自动配置
    if is_url(query) and main_domain not in cse_config:
        print(f"检测到新URL主域名: {main_domain}, 开始自动配置...")
        # 测试工具组合
        test_configs = [
            "1 1 1 1",  # 全部启用
        ]
        best_config = None
        
        for test_config in test_configs:
            config_parts = test_config.split()
            temp_use_doubao_search = int(config_parts[0])
            temp_use_cse_search = int(config_parts[1])
            temp_use_doubao_url_analysis = int(config_parts[2])
            temp_use_selenium_analysis = int(config_parts[3])
            
            best_config = evaluate_tools_for_url(
                query,
                cse_results=results,
                doubao_results=doubao_results,
                url_analysis=url_analysis,
                page_analysis=page_analysis
            )
            print(f"测试配置 {test_config} 评估结果: {best_config}")
            
            # 保存最佳配置(使用主域名作为键)
            cse_config[main_domain] = best_config
            save_cse_config(cse_config)
            break

    # 如果是JSON请求，评估结果是否满足用户需求
    if request and request.content_type == 'application/json':
        data = request.get_json()
        context = data.get('messages', [])
        evaluation = evaluate_tool_results(context, json.dumps(combined_results, ensure_ascii=False))
        return {
            "content": evaluation,
            "raw_results": results
        }
    
    # 生成最终响应
    try:
        prompt = "搜索结果总结:\n"
        if use_cse_search and results.get('items'):
            prompt += f"Google CSE结果({len(results['items'])}条):\n"
            for i, item in enumerate(results['items'][:3]):
                prompt += f"{i+1}. {item.get('title')}\n{item.get('link')}\n\n"
        
        if use_doubao_search and doubao_results:
            prompt += f"\n豆包搜索结果:\n{doubao_results}\n"
        
        if use_doubao_url_analysis and url_analysis:
            prompt += f"\nURL分析结果:\n{url_analysis}\n"
        
        if use_selenium_analysis and use_doubao_url_analysis and page_analysis:
            prompt += f"\n网页内容分析:\n{page_analysis}\n"
        
        return {
            "content": prompt,
            "raw_results": results
        }
    except Exception as e:
        print(f"生成最终响应失败: {str(e)}")
        return {
            "content": json.dumps(combined_results, ensure_ascii=False),
            "raw_results": results
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
