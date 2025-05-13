
from flask import Flask, request, jsonify, session, render_template
import os
import hashlib
import pymysql
import time
from functools import wraps
from datetime import datetime
import json
from shared_utils import create_table, check_tables
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '13380008373',
    'database': 'library',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}


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
    """处理聊天页面请求"""
    query = request.args.get('query', '')
    return render_template('doubao_chat.html', query=query)

@app.route('/api/doubao/chat', methods=['POST'])
def doubao_chat_api():
    """处理豆包聊天API请求"""
    try:
        # 处理multipart/form-data类型的图片上传
        if 'multipart/form-data' in request.content_type:
            file = request.files.get('file')
            if not file:
                return jsonify({'error': 'No file uploaded'}), 400
                
            # 处理文件上传逻辑
            # ... (保留原有文件处理逻辑)
            
        else:
            # 处理JSON或表单数据
            if request.content_type == 'application/json':
                data = request.get_json()
            else:
                data = request.form.to_dict()
            
            # 处理聊天逻辑
            # ... (保留原有聊天逻辑)
        
        # 返回响应
        return jsonify({"message": "Chat processed"}), 200
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to process chat request'
        }), 500

# 聊天记录相关路由
@app.route('/api/chat/histories', methods=['GET'])
def list_chat_histories():
    """获取所有聊天历史记录列表"""
    try:
        # 确保表存在
        create_table()
        
        user_agent = request.headers.get('User-Agent', '')
        if not user_agent:
            return jsonify({'error': 'User-Agent header is required'}), 400
            
        user_agent_hash = hashlib.sha256(user_agent.encode()).hexdigest()
        
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 检查表是否存在
            cursor.execute("SHOW TABLES LIKE 'chat_sessions'")
            if not cursor.fetchone():
                return jsonify({'error': 'Chat sessions table not found'}), 500
                
            cursor.execute('''
                SELECT session_id as id, title, UNIX_TIMESTAMP(updated_at) as timestamp
                FROM chat_sessions
                WHERE user_agent_hash = %s
                ORDER BY updated_at DESC
            ''', (user_agent_hash,))
            
            histories = cursor.fetchall()
            return jsonify({
                'histories': histories,
                'message': 'Successfully retrieved chat histories'
            }), 200
            
    except pymysql.Error as e:
        app.logger.error(f"Database error: {str(e)}")
        return jsonify({
            'error': 'Database operation failed',
            'details': str(e)
        }), 500
    except Exception as e:
        app.logger.error(f"Unexpected error: {str(e)}")
        return jsonify({
            'error': 'An unexpected error occurred',
            'details': str(e)
        }), 500
    finally:
        if 'conn' in locals() and conn:
            conn.close()

@app.route('/api/chat/history/<history_id>', methods=['GET'])
def get_chat_history(history_id):
    """获取特定聊天历史记录"""
    try:
        user_agent = request.headers.get('User-Agent', '')
        user_agent_hash = hashlib.sha256(user_agent.encode()).hexdigest()
        
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 验证会话属于当前用户
            cursor.execute('''
                SELECT 1 FROM chat_sessions
                WHERE session_id = %s AND user_agent_hash = %s
            ''', (history_id, user_agent_hash))
            
            if not cursor.fetchone():
                return jsonify({'error': 'History not found or access denied'}), 404
            
            # 获取消息
            cursor.execute('''
                SELECT role, content
                FROM chat_messages
                WHERE session_id = %s
                ORDER BY created_at
            ''', (history_id,))
            
            messages = [{'role': row['role'], 'content': row['content']} 
                       for row in cursor.fetchall()]
            
            return jsonify({
                'id': history_id,
                'messages': messages,
                'title': messages[0]['content'][:30] if messages else 'Untitled Chat'
            }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/chat/history', methods=['POST'])
def save_chat_history():
    """保存当前聊天历史记录"""
    try:
        data = request.get_json()
        if not data or 'messages' not in data:
            return jsonify({'error': 'Invalid data'}), 400
            
        user_agent = request.headers.get('User-Agent', '')
        user_agent_hash = hashlib.sha256(user_agent.encode()).hexdigest()
        
        # 生成或使用现有ID
        history_id = f'chat-{int(time.time())}'
        if 'id' in data and data['id']:
            history_id = data['id']
            
        # 设置默认标题
        title = data.get('title', '')
        if not title and data['messages'] and len(data['messages']) > 0:
            title = data['messages'][0]['content'][:30]
            
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 创建或更新会话
            cursor.execute('''
                INSERT INTO chat_sessions (session_id, user_agent_hash, title)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE 
                title = VALUES(title),
                updated_at = CURRENT_TIMESTAMP
            ''', (history_id, user_agent_hash, title))
            
            # 保存消息
            for message in data['messages']:
                cursor.execute('''
                    INSERT INTO chat_messages (session_id, role, content)
                    VALUES (%s, %s, %s)
                ''', (history_id, message['role'], message['content']))
                
            conn.commit()
            
            return jsonify({
                'id': history_id,
                'message': 'Chat history saved successfully'
            }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/chat/history/<history_id>', methods=['DELETE'])
def delete_chat_history(history_id):
    """删除特定聊天历史记录"""
    try:
        user_agent = request.headers.get('User-Agent', '')
        user_agent_hash = hashlib.sha256(user_agent.encode()).hexdigest()
        
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 验证会话属于当前用户
            cursor.execute('''
                DELETE FROM chat_sessions
                WHERE session_id = %s AND user_agent_hash = %s
            ''', (history_id, user_agent_hash))
            
            # 级联删除消息
            cursor.execute('''
                DELETE FROM chat_messages
                WHERE session_id = %s
            ''', (history_id,))
            
            conn.commit()
            
            if cursor.rowcount == 0:
                return jsonify({'error': 'History not found or access denied'}), 404
                
            return jsonify({
                'message': 'Chat history deleted successfully'
            }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()



app.run(host='0.0.0.0', port=10806, debug=False)
