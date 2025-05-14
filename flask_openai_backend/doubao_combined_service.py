import traceback
from flask import Flask, redirect, request, jsonify, session, render_template, url_for
import os
import flask
import hashlib
import pymysql
import time
from functools import wraps
from datetime import datetime
import json
import base64
from flask_cors import CORS
from openai import OpenAI
import re
from dotenv import load_dotenv
from requests import Response
import requests
from tools import tools, client, bot_client  # 导入工具定义
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

def process_message(messages: list):
    """处理用户消息，自动判断是否使用工具"""
    print(f"处理消息数量: {len(messages)}")
    print(f"最后一条消息内容: {messages}")
    
    # 首先尝试使用工具模型
    try:
        response = client.chat.completions.create(
            model="doubao-1-5-lite-32k-250115",
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        
        # 打印token使用情况
        if hasattr(response, 'usage'):
            usage = response.usage
            print(f"Token使用情况 - 输入: {usage.prompt_tokens} | 输出: {usage.completion_tokens} | 总计: {usage.total_tokens}")
        
        # 如果没有工具调用，则使用深度思考模型
        if not response.choices[0].message.tool_calls:
            print("未检测到工具调用，转入深度思考模型")
            response = client.chat.completions.create(
                model="doubao-1-5-thinking-pro-250415",
                messages=messages,
                base_url="https://ark.cn-beijing.volces.com/api/v3"
            )
            # 打印token使用情况
            if hasattr(response, 'usage'):
                usage = response.usage
                print(f"Token使用情况 - 输入: {usage.prompt_tokens} | 输出: {usage.completion_tokens} | 总计: {usage.total_tokens}")
            
        return response
        
    except Exception as e:
        print(f"工具模型调用失败: {str(e)}，尝试使用深度思考模型")
        response = client.chat.completions.create(
            model="doubao-1-5-thinking-pro-250415",
            messages=messages,
            base_url="https://ark.cn-beijing.volces.com/api/v3"
        )
        # 打印token使用情况
        if hasattr(response, 'usage'):
            usage = response.usage
            print(f"Token使用情况 - 输入: {usage.prompt_tokens} | 输出: {usage.completion_tokens} | 总计: {usage.total_tokens}")
        return response

def process_url(url: str):
    """处理URL分析请求"""
    print(f"调用模型: bot-20250506034902-4psdn, 分析URL: {url[:100]}...")
    return bot_client.chat.completions.create(
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

def process_search(query: str):
    """处理搜索请求"""
    print(f"调用模型: bot-20250506042211-5bscp, 搜索内容: {query[:100]}...")
    response = bot_client.chat.completions.create(
        model="bot-20250506042211-5bscp",
        messages=[
            {"role": "system", "content": "你是豆包，是由字节跳动开发的 AI 人工智能助手"},
            {"role": "user", "content": f"请搜索: {query}"}
        ],
        tools=tools,
        tool_choice={"type": "function", "function": {"name": "web_search"}}
    )
    # 打印原始JSON输出
    print("豆包搜索原始JSON输出:")
    print(json.dumps(response, indent=2, ensure_ascii=False, default=str))
    
    # 生成embedding（分块处理）
    print("----- 生成embedding（分块处理）-----")
    embedding_info = ""
    try:
        content_str = response.choices[0].message.content if response.choices[0].message.content else ""
        chunk_size = 3000  # 安全阈值，避免超过4096限制
        chunks = [content_str[i:i+chunk_size] for i in range(0, len(content_str), chunk_size)]
        
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
    
    # 调用thinking-pro模型处理结果
    prompt = f"请总结以下搜索结果:\n{content_str}{embedding_info}"
    print(f"调用doubao-1-5-thinking-pro-250415处理结果,prompt长度: {len(prompt)}")
    
    try:
        thinking_response = client.chat.completions.create(
            model="doubao-1-5-thinking-pro-250415",
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            timeout=60
        )
        return {
            "content": thinking_response.choices[0].message.content,
            "raw_response": json.loads(json.dumps(response, default=str))
        }
    except Exception as e:
        print(f"thinking-pro模型处理失败: {str(e)}")
        return {
            "content": content_str,
            "raw_response": json.loads(json.dumps(response, default=str))
        }

def process_image_data(image_data: str, task: str = "describe"):
    """处理图片分析请求"""
    print(f"调用VLM服务分析图片，任务类型: {task}")
    return vlm_service.analyze_image(image_data, task)

def process_dlink_request(book_url: str):
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

def process_google_cse(query: str, cx: str = "b7a4dfc41bb40428c", num: int = 5):
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
        
        # 调用doubao模型处理结果
        prompt = f"请总结以下Google搜索结果:\n{json.dumps(results, ensure_ascii=False)}{embedding_info}"
        print(f"调用doubao模型处理结果,prompt长度: {len(prompt)}")
        
        try:
            doubao_response = client.chat.completions.create(
                model="doubao-1-5-thinking-pro-250415",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                timeout=60
            )
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

def process_zlib_search(query: str, result_type: str = "summary"):
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
            
            # 返回原始结果和模型处理后的结果
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



app = Flask(__name__)
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='None',  # 允许跨站请求
    SECRET_KEY=os.environ.get('FLASK_SECRET_KEY', 'default-secret-key')
)

CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "supports_credentials": True  # 允许跨域携带cookie
    }
})

# 加载环境变量
load_dotenv()

def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET'])
def handle_chat_page():
    """处理主聊天页面请求"""
    query = request.args.get('query', '')
    return render_template('doubao_chat3.html', query=query)

@app.route('/c/<chat_id>', methods=['GET'])
def load_chat_history(chat_id):
    """加载聊天历史并继续对话"""
    # 验证历史记录是否存在
    filepath = os.path.join(CHAT_HISTORY_DIR, f'{chat_id}.json')
    if not os.path.exists(filepath):
        return render_template('doubao_chat.html', error='Chat history not found')
    
    return render_template('doubao_chat.html', chat_id=chat_id)

@app.route('/api/doubao/chat', methods=['POST'])
def doubao_chat_api():
    """统一的聊天API，支持文本和图片"""
    try:
        # 优先从环境变量获取API Key
        api_key = os.environ.get("ARK_API_KEY")
        if not api_key:
            # 环境变量不存在则从文件读取
            with open(os.path.join(os.path.dirname(__file__), 'templates', 'doubao.txt'), 'r') as f:
                api_key = f.read().strip()
        
        if not api_key:
            return jsonify({'error': 'API Key未配置'}), 500
            
        # 初始化客户端
        client = OpenAI(
            api_key=api_key,
            base_url="https://ark.cn-beijing.volces.com/api/v3/bots"
        )

        # 处理multipart/form-data类型的图片上传
        if 'multipart/form-data' in request.content_type:
            file = request.files.get('file')
            if not file:
                return jsonify({'error': 'No file uploaded'}), 400
                
            # 验证并处理图片上传
            try:
                # 验证文件类型
                if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    return jsonify({'error': '仅支持PNG/JPG/JPEG/GIF格式的图片'}), 400
                
                # 读取并验证图片大小(不超过5MB)
                file.seek(0, os.SEEK_END)
                file_size = file.tell()
                if file_size > 5 * 1024 * 1024:
                    return jsonify({'error': '图片大小不能超过5MB'}), 400
                file.seek(0)
                
                # 编码图片并验证
                image_base64 = base64.b64encode(file.read()).decode('utf-8')
                if not image_base64 or len(image_base64) < 100:
                    return jsonify({'error': '图片编码失败'}), 400
                
                question = request.form.get('question', '请描述这张图片的内容')
                if not question or len(question) > 500:
                    question = '请描述这张图片的内容'
                
                # 调用VLM服务分析图片并直接返回结果
                vlm_response = vlm_service.analyze_image(
                    image_data=f"data:{file.content_type};base64,{image_base64}",
                    prompt=question
                )
                
                if "error" in vlm_response:
                    return jsonify(vlm_response), 500
                
                # 直接返回VLM处理结果
                return jsonify({
                    'content': vlm_response["content"],
                    'is_image_response': True,
                    'is_direct_vlm_response': True
                })
                
            except Exception as e:
                error_detail = {
                    'error': '图片处理失败',
                    'message': str(e),
                    'traceback': traceback.format_exc(),
                    'suggestion': '请检查图片格式和大小，或稍后再试'
                }
                app.logger.error(f"图片处理失败: {error_detail}")
                return jsonify(error_detail), 500
            
        else:
            # 处理JSON或表单数据
            if request.content_type == 'application/json':
                data = request.get_json()
            else:
                data = request.form.to_dict()
            
            if not data or 'messages' not in data:
                return jsonify({'error': '缺少必要参数'}), 400
            
            # 统一消息处理入口
            print("开始处理消息请求...")
            print(f"收到消息数量: {len(data['messages'])}")
            response = process_message(
                messages=data['messages']
            )
            print(f"模型返回结果: {response.choices[0].message.content[:200]}...")
            
            # 处理工具调用
            print("检查是否需要处理工具调用...")
            if response.choices[0].message.tool_calls:
                print(f"检测到工具调用: {response.choices[0].message.tool_calls[0].function.name}")
                # 这里添加工具调用处理逻辑
                tool_call = response.choices[0].message.tool_calls[0]
                if tool_call.function.name == "web_search":
                    search_args = json.loads(tool_call.function.arguments)
                    print(f"检测到工具调用: web_search, 搜索内容: {search_args['query']}")
                    search_result = process_search(**search_args)
                    print(f"web_search返回结果: {search_result.choices[0].message.content[:200]}...")
                    
                    # 检查web_search是否返回有效结果
                    if "没有找到" in search_result.choices[0].message.content or "未找到" in search_result.choices[0].message.content:
                        print("web_search未找到结果，自动切换到Google CSE搜索")
                        cse_result = process_google_cse(query=search_args['query'])
                        if "error" in cse_result:
                            return jsonify({
                                'content': f"web_search未找到结果，且Google CSE搜索失败: {cse_result['error']}",
                                'is_search_result': True
                            })
                        return jsonify({
                            'content': f"web_search未找到结果，以下是Google CSE搜索结果:\n{cse_result['content']}",
                            'is_search_result': True,
                            'is_cse_fallback': True
                        })
                    
                    return jsonify({
                        'content': search_result.choices[0].message.content,
                        'is_search_result': True
                    })
                elif tool_call.function.name == "url_analysis":
                    url_result = process_url(**json.loads(tool_call.function.arguments))
                    return jsonify({
                        'content': url_result.choices[0].message.content,
                        'is_url_response': True
                    })
                elif tool_call.function.name == "image_analysis":
                    image_result = process_image_data(**json.loads(tool_call.function.arguments))
                    return jsonify({
                        'content': image_result.choices[0].message.content,
                        'is_image_response': True
                    })
                elif tool_call.function.name == "zlib_search":
                    zlib_result = process_zlib_search(**json.loads(tool_call.function.arguments))
                    if "error" in zlib_result:
                        return jsonify({"error": zlib_result["error"]}), 500
                    return jsonify({
                        'content': zlib_result["content"],
                        'is_zlib_response': True
                    })
                elif tool_call.function.name == "google_cse_search":
                    cse_args = json.loads(tool_call.function.arguments)
                    print(f"检测到工具调用: google_cse_search, 搜索内容: {cse_args['query']}")
                    cse_result = process_google_cse(**cse_args)
                    if "error" in cse_result:
                        return jsonify({"error": cse_result["error"]}), 500
                    return jsonify({
                        'content': cse_result["content"],
                        'is_cse_response': True
                    })
                elif tool_call.function.name == "get_dlink":
                    dlink_result = process_dlink_request(**json.loads(tool_call.function.arguments))
                    if "error" in dlink_result:
                        return jsonify({"error": dlink_result["error"]}), 500
                    return jsonify({
                        'content': dlink_result["content"],
                        'is_dlink_response': True
                    })
                
                if data.get('stream', False):
                    # 流式响应
                    print("使用流式响应...")
                    def generate():
                        for chunk in response:
                            if chunk.choices and chunk.choices[0].delta.content:
                                print(f"流式响应内容: {chunk.choices[0].delta.content[:100]}...")
                                yield chunk.choices[0].delta.content
                    
                    return Response(generate(), mimetype='text/plain')
                else:
                    # 标准响应
                    print("使用标准响应...")
                    result = {
                        'content': response.choices[0].message.content
                    }
                    print(f"响应内容长度: {len(result['content'])}")
                
                if hasattr(response, "references"):
                    result['references'] = response.references
                        
                return jsonify(result)
                
    except Exception as e:
        error_msg = '聊天服务返回错误，请稍后再试'
        if 'Failed to fetch' in str(e):
            error_msg = '无法连接到聊天服务，请检查网络连接'
        elif 'HTTP error' in str(e):
            error_msg = '聊天服务返回错误，请稍后再试'
            
        return jsonify({
            'error': error_msg,
            'message': str(e)
        }), 500

@app.route('/api/doubao/websearch', methods=['POST'])
def doubao_websearch():
    """豆包web搜索API接口"""
    data = request.get_json()
    if not data or not data.get('query'):
        return jsonify({"error": "请求体必须包含query参数"}), 400
    
    try:
        response = process_search(
            query=data['query'],
            result_type="detailed"
        )
        try:
            parsed_result = json.loads(response['content'])
            return jsonify(parsed_result)
        except json.JSONDecodeError:
            return jsonify({"content": response['content']})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/doubao/url_parse', methods=['POST'])
def doubao_url_parse():
    """URL解析API接口"""
    data = request.get_json()
    if not data or not data.get('url'):
        return jsonify({"error": "请求体必须包含url参数"}), 400
    
    try:
        # 调用豆包API解析URL内容
        response = bot_client.chat.completions.create(
            model="bot-20250506034902-4psdn",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的URL内容解析器，请解析用户提供的URL内容，返回标题和主要内容"
                },
                {
                    "role": "user",
                    "content": f"请解析以下URL内容并返回标题和主要内容：{data['url']}"
                }
            ]
        )
        
        # 获取解析结果
        parsed_content = response.choices[0].message.content
        
        # 将解析结果传入search流程
        search_response = bot_client.chat.completions.create(
            model="bot-20250506042211-5bscp",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个搜索引擎，请根据以下内容返回相关信息"
                },
                {
                    "role": "user",
                    "content": parsed_content
                }
            ]
        )
        
        result = search_response.choices[0].message.content
        try:
            parsed_result = json.loads(result)
            return jsonify({
                "original_url": data['url'],
                "parsed_content": parsed_content,
                "search_results": parsed_result
            })
        except json.JSONDecodeError:
            return jsonify({
                "original_url": data['url'],
                "parsed_content": parsed_content,
                "search_results": result
            })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

import os
from datetime import datetime

# 确保ChatHistory目录存在
CHAT_HISTORY_DIR = os.path.join(os.path.dirname(__file__), 'ChatHistory')
os.makedirs(CHAT_HISTORY_DIR, exist_ok=True)

@app.route('/api/chat/histories', methods=['GET'])
def list_chat_histories():
    """获取所有聊天历史记录列表"""
    try:
        files = [f for f in os.listdir(CHAT_HISTORY_DIR) if f.endswith('.json')]
        histories = []
        
        for filename in files:
            try:
                with open(os.path.join(CHAT_HISTORY_DIR, filename), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    histories.append({
                        'id': filename[:-5],  # 去掉.json后缀
                        'title': data.get('title', 'Untitled Chat'),
                        'timestamp': os.path.getmtime(os.path.join(CHAT_HISTORY_DIR, filename))
                    })
            except Exception as e:
                continue
                
        # 按时间倒序排序
        histories.sort(key=lambda x: x['timestamp'], reverse=True)
        
        return jsonify({
            'histories': histories,
            'message': 'Successfully retrieved chat histories'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/histories/list', methods=['GET'])
def list_chat_histories_html():
    """获取所有聊天历史记录列表(HTML格式)"""
    try:
        files = [f for f in os.listdir(CHAT_HISTORY_DIR) if f.endswith('.json')]
        histories = []
        
        for filename in files:
            try:
                with open(os.path.join(CHAT_HISTORY_DIR, filename), 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    histories.append({
                        'id': filename[:-5],  # 去掉.json后缀
                        'title': data.get('title', 'Untitled Chat'),
                        'timestamp': os.path.getmtime(os.path.join(CHAT_HISTORY_DIR, filename))
                    })
            except Exception as e:
                continue
                
        # 按时间倒序排序
        histories.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # 转换时间戳为可读格式
        for history in histories:
            history['timestamp'] = datetime.fromtimestamp(history['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
        
        return render_template('chat_history_list.html', histories=histories)
        
    except Exception as e:
        return f"<h1>Error</h1><p>{str(e)}</p>", 500

@app.route('/api/chat/history/<history_id>', methods=['GET'])
def get_chat_history(history_id):
    """获取特定聊天历史记录"""
    try:
        filepath = os.path.join(CHAT_HISTORY_DIR, f'{history_id}.json')
        if not os.path.exists(filepath):
            return jsonify({'error': 'History not found'}), 404
            
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # 确保图片数据正确加载
        messages = []
        for msg in data.get('messages', []):
            if isinstance(msg, dict) and msg.get('is_image'):
                messages.append({
                    'role': msg['role'],
                    'content': msg['content'],
                    'image_data': msg['image_data']
                })
            else:
                messages.append(msg)
                
        # 添加可共享的URL信息
        result = {
            'id': history_id,
            'messages': messages,
            'title': data.get('title', 'Untitled Chat'),
            'share_url': f"/?context={history_id}"
        }
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/history', methods=['POST'])
def save_chat_history():
    """保存当前聊天历史记录"""
    try:
        data = request.get_json()
        if not data or 'messages' not in data:
            return jsonify({'error': 'Invalid data'}), 400
            
        # 生成或使用现有ID
        history_id = data.get('id', f'chat-{int(time.time())}')
        
        # 设置默认标题
        title = data.get('title', '')
        if not title and data['messages'] and len(data['messages']) > 0:
            # 如果是图片消息，使用"Image Analysis"作为标题
            if isinstance(data['messages'][0], dict) and 'image_data' in data['messages'][0]:
                title = "Image Analysis"
            else:
                title = data['messages'][0]['content'][:30]
            
        # 处理消息中的图片数据
        processed_messages = []
        for msg in data['messages']:
            if isinstance(msg, dict) and 'image_data' in msg:
                # 如果是图片消息，保留base64数据
                processed_msg = {
                    'role': msg['role'],
                    'content': msg.get('content', 'Analyze this image:'),
                    'image_data': msg['image_data'],
                    'is_image': True
                }
                processed_messages.append(processed_msg)
            else:
                processed_messages.append(msg)
        
        # 保存数据
        save_data = {
            'id': history_id,
            'title': title,
            'messages': processed_messages,
            'created_at': datetime.now().isoformat()
        }
        
        filepath = os.path.join(CHAT_HISTORY_DIR, f'{history_id}.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
            
        return jsonify({
            'id': history_id,
            'message': 'Chat history saved successfully'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/chat/history/<history_id>', methods=['DELETE'])
def delete_chat_history(history_id):
    """删除特定聊天历史记录"""
    try:
        filepath = os.path.join(CHAT_HISTORY_DIR, f'{history_id}.json')
        if not os.path.exists(filepath):
            return jsonify({'error': 'History not found'}), 404
            
        os.remove(filepath)
        return jsonify({
            'message': 'Chat history deleted successfully'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


app.run(host='0.0.0.0', port=10806, debug=False)
