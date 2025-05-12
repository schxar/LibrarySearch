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

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# 加载环境变量
load_dotenv()

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

# VLM客户端配置 (用于图片处理)
vlm_client = OpenAI(
    api_key=api_key,
    base_url="https://ark.cn-beijing.volces.com/api/v3"
)

# 文本模型客户端配置 (用于普通聊天和搜索)
text_client = OpenAI(
    api_key=api_key,
    base_url="https://ark.cn-beijing.volces.com/api/v3/bots"
)

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
    return render_template('doubao_chat.html', query=query)

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
                
            # 处理图片上传
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
            
        else:
            # 处理JSON或表单数据
            if request.content_type == 'application/json':
                data = request.get_json()
            else:
                data = request.form.to_dict()
            
            if not data or 'messages' not in data:
                return jsonify({'error': '缺少必要参数'}), 400
            
            # 检查最后一条用户消息是否包含URL
            last_message = data['messages'][-1]['content']
            url_pattern = re.compile(
                r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            )
            url_match = url_pattern.search(last_message)
            
            if url_match:
                # 如果包含URL，调用专门的URL解析模型
                url = url_match.group()
                response = text_client.chat.completions.create(
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
                # 处理普通聊天
                response = text_client.chat.completions.create(
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
    data = request.get_json()
    if not data or not data.get('url'):
        return jsonify({"error": "请求体必须包含url参数"}), 400
    
    try:
        # 调用豆包API解析URL内容
        response = text_client.chat.completions.create(
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10806, debug=False)
