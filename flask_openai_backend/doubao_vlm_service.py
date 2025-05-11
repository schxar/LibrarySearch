
import json
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import os
import base64
import mysql.connector
import pymysql
import re
import traceback
from dotenv import load_dotenv
from requests import Response

download_directory = os.path.join(os.getcwd(), "C:\\Users\\PC\\eclipse-workspace\\LibrarySearch\\src\\main\\resources\\static\\books")

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '13380008373',
    'database': 'library',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})  # 启用CORS支持并配置详细规则

# 初始化豆包客户端
with open(os.path.join(os.path.dirname(__file__), 'templates', 'doubao.txt'), 'r') as f:
    api_key = f.read().strip()

# VLM客户端配置
vlm_client = OpenAI(
    api_key=api_key,
    base_url="https://ark.cn-beijing.volces.com/api/v3"
)

# 文字搜索客户端配置
text_client = OpenAI(
    api_key=api_key,
    base_url="https://ark.cn-beijing.volces.com/api/v3/bots"
)

# 删除 DeepSeek 客户端配置

@app.route('/api/doubao/vlm_upload', methods=['POST'])
def vlm_upload():
    """处理图片上传并调用VLM API"""
    if 'file' not in request.files:
        return jsonify({'error': '未上传文件'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '未选择文件'}), 400
    
    # 验证文件类型
    allowed_extensions = {'png', 'jpg', 'jpeg', 'gif'}
    if '.' not in file.filename or file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
        return jsonify({'error': '无效的文件类型'}), 400
    
    try:
        # 读取图片为base64
        image_base64 = base64.b64encode(file.read()).decode('utf-8')
        question = request.form.get('question', '请描述这张图片的内容')
        
        response = vlm_client.chat.completions.create(
            model="doubao-1.5-vision-pro-250328",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            },
                        },
                        {"type": "text", "text": question},
                    ],
                }
            ],
        )
        
        return jsonify({
            'content': response.choices[0].message.content
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/doubao/chat', methods=['POST'])
def chat():
    """处理聊天请求，支持文字和图片"""
    if request.content_type == 'application/json':
        # 处理文字聊天
        data = request.get_json()
        if not data or 'messages' not in data:
            return jsonify({'error': '缺少必要参数'}), 400
        
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

            # 检查最后一条用户消息是否包含URL
            last_message = data['messages'][-1]['content']
            url_pattern = re.compile(
                r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            )
            url_match = url_pattern.search(last_message)
            
            if url_match:
                # 如果包含URL，调用专门的URL解析模型
                url = url_match.group()
                response = client.chat.completions.create(
                    model="bot-20250506034902-4psdn",
                    messages=[
                        {
                            "role": "system", 
                            "content": "你是一个专业的URL内容解析器，请解析用户提供的URL内容，返回标题和主要内容"
                        },
                        {
                            "role": "user",
                            "content": f"请解析以下URL内容并返回标题和主要内容：{url}"
                        }
                    ]
                )
                
                result = {
                    'content': response.choices[0].message.content,
                    'is_url_response': True
                }
                
                if hasattr(response, "references"):
                    result['references'] = response.references
                    
                return jsonify(result)
            else:
                # 普通聊天处理
                response = client.chat.completions.create(
                    model="bot-20250506042211-5bscp",
                    messages=[
                        {"role": "system", "content": "你是豆包，是由字节跳动开发的 AI 人工智能助手"},
                        *data['messages']
                    ],
                    stream=data.get('stream', False)
                )
                
                if data.get('stream', False):
                    # 流式响应
                    def generate():
                        for chunk in response:
                            if chunk.choices and chunk.choices[0].delta.content:
                                yield chunk.choices[0].delta.content
                    
                    return Response(generate(), mimetype='text/plain')
                else:
                    # 标准响应
                    result = {
                        'content': response.choices[0].message.content
                    }
                    
                    if hasattr(response, "references"):
                        result['references'] = response.references
                        
                    return jsonify(result)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
            
    elif request.content_type.startswith('multipart/form-data'):
        # 处理图片上传
        return vlm_upload()
        
    else:
        return jsonify({'error': '不支持的Content-Type'}), 400

@app.route('/api/doubao/search', methods=['POST'])
def doubao_search():
    """豆包搜索API接口"""
    if not text_client:
        return jsonify({"error": "豆包客户端未初始化"}), 500
        
    data = request.get_json()
    if not data:
        return jsonify({"error": "请求体必须为JSON格式"}), 400
    
    model = data.get('model', 'bot-20250506042211-5bscp')
    messages = data.get('messages', [])
    stream = data.get('stream', False)
    
    if not messages:
        return jsonify({"error": "messages参数不能为空"}), 400
    
    try:
        if stream:
            # 流式响应
            def generate():
                stream = text_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    stream=True
                )
                for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            
            return Response(generate(), mimetype='text/plain')
        else:
            # 标准响应
            response = text_client.chat.completions.create(
                model=model,
                messages=messages
            )
            result = {
                "content": response.choices[0].message.content,
                "references": getattr(response, "references", None)
            }
            return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/doubao/websearch', methods=['POST'])
def doubao_websearch():
    """豆包web搜索API接口"""
    if not text_client:
        return jsonify({"error": "豆包客户端未初始化"}), 500
        
    data = request.get_json()
    if not data or not data.get('query'):
        return jsonify({"error": "请求体必须包含query参数"}), 400
    
    try:
        response = text_client.chat.completions.create(
            model="bot-20250506042211-5bscp",
            messages=[
                {
                    "role": "user",
                    "content": f"请帮我搜索关于'{data['query']}'的信息，返回格式为JSON数组，每个结果包含title和url字段"
                }
            ]
        )
        
        result = response.choices[0].message.content
        try:
            parsed_result = json.loads(result)
            return jsonify(parsed_result)
        except json.JSONDecodeError:
            return jsonify({"content": result})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/doubao/url_parse', methods=['POST'])
def doubao_url_parse():
    """URL解析API接口"""
    if not text_client:
        return jsonify({"error": "豆包客户端未初始化"}), 500
        
    data = request.get_json()
    if not data or not data.get('url'):
        return jsonify({"error": "请求体必须包含url参数"}), 400
    
    try:
        # 调用豆包API解析URL内容
        response = text_client.chat.completions.create(
            model="bot-20250506042211-5bscp",
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
        search_response = text_client.chat.completions.create(
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

@app.route('/vlm_upload', methods=['GET'])
def vlm_upload_page():
    """VLM图片上传页面"""
    return render_template('vlm_upload.html')

@app.route('/', methods=['GET'])
def doubao_chat_page():
    """豆包聊天页面"""
    query = request.args.get('query', '')
    return render_template('doubao_chat.html', query=query)

from collections import defaultdict

def remove_duplicate_files(directory):
    """删除重复的带编号文件，保留无编号或最新文件"""
    pattern = re.compile(r'^(.*?)( \(\d+\))?(\.[^.]+)$')
    file_groups = defaultdict(list)

    # 分组文件
    for filename in os.listdir(directory):
        match = pattern.match(filename)
        if match:
            base, suffix, ext = match.groups()
            clean_name = f"{base}{ext}"
            file_groups[clean_name].append(filename)

    # 处理每组文件
    for clean_name, files in file_groups.items():
        if len(files) <= 1:
            continue  # 无重复

        # 分离无编号和有编号文件
        non_numbered = []
        numbered = []
        for f in files:
            match = pattern.match(f)
            if match.group(2):
                numbered.append(f)
            else:
                non_numbered.append(f)

        # 保留无编号文件，删除有编号的
        if non_numbered:
            keep_file = non_numbered[0]
            for f in numbered:
                os.remove(os.path.join(directory, f))
                print(f"已删除重复文件: {f}")
        else:
            # 按修改时间保留最新文件
            files_with_mtime = []
            for f in files:
                path = os.path.join(directory, f)
                mtime = os.path.getmtime(path)
                files_with_mtime.append((mtime, f))
            # 按时间排序，保留最新
            files_sorted = sorted(files_with_mtime, key=lambda x: x[0], reverse=True)
            for mtime, f in files_sorted[1:]:  # 删除旧文件
                os.remove(os.path.join(directory, f))
                print(f"已删除旧文件: {f}")

def check_tables(conn):
    """检查所有需要的表是否存在，不存在则创建"""
    with conn.cursor() as cursor:
        # 检查并创建DownloadHistory表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS DownloadHistory (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_email VARCHAR(255) NOT NULL,
                filename VARCHAR(255) NOT NULL,
                email_hash VARCHAR(64) NOT NULL,
                filename_hash VARCHAR(64) NOT NULL,
                download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) CHARSET=utf8mb4;
        ''')
        
        # 检查并创建SearchRecommendations表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS SearchRecommendations (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_email VARCHAR(255) NOT NULL,
                email_hash VARCHAR(64) NOT NULL,
                search_terms TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) CHARSET=utf8mb4;
        ''')
        
        # 检查并创建NotebookLMAudioRequests表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS NotebookLMAudioRequests (
                id INT AUTO_INCREMENT PRIMARY KEY,
                book_title VARCHAR(255) NOT NULL,
                book_hash VARCHAR(64) NOT NULL,
                request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                clerk_user_email VARCHAR(255) NOT NULL,
                status ENUM('pending', 'processing', 'completed') DEFAULT 'pending'
            ) CHARSET=utf8mb4;
        ''')
        conn.commit()

def get_db_connection():
    """获取数据库连接并确保表存在"""
    conn = pymysql.connect(**DB_CONFIG)
    check_tables(conn)
    return conn

if __name__ == '__main__':
    # 创建所有需要的表
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 创建下载历史表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS DownloadHistory (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_email VARCHAR(255) NOT NULL,
                    filename VARCHAR(255) NOT NULL,
                    email_hash VARCHAR(64) NOT NULL,
                    filename_hash VARCHAR(64) NOT NULL,
                    download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) CHARSET=utf8mb4;
            ''')
            
            # 创建推荐记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS SearchRecommendations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_email VARCHAR(255) NOT NULL,
                    email_hash VARCHAR(64) NOT NULL,
                    search_terms TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) CHARSET=utf8mb4;
            ''')
            
            # 创建NotebookLM请求表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS NotebookLMAudioRequests (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    book_title VARCHAR(255) NOT NULL,
                    book_hash VARCHAR(64) NOT NULL,
                    request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    clerk_user_email VARCHAR(255) NOT NULL,
                    status ENUM('pending', 'processing', 'completed') DEFAULT 'pending'
                ) CHARSET=utf8mb4;
            ''')
        conn.commit()
        print("所有表结构验证完成")
    except Exception as e:
        print(f"表结构验证失败: {str(e)}")
        exit(1)
    finally:
        conn.close()

    # 清理重复文件
    remove_duplicate_files(download_directory)

    app.run(host='0.0.0.0', port=10807, debug=True)
