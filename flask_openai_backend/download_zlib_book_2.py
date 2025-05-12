from flask import Flask, Response, render_template, request, jsonify, send_file, render_template_string, redirect, url_for, session, send_from_directory
import os
import json
import glob
import base64
import os
import glob
from math import ceil
import mysql.connector
import hashlib
from datetime import datetime
import pymysql
import re
import traceback
from dotenv import load_dotenv
from shared_utils import check_tables, create_table, HTML_LOGIN
from openai import OpenAI

# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')

# 豆包search客户端配置
try:
    with open("flask_openai_backend/doubao.txt", "r") as f:
        doubao_api_key = f.read().strip()
    
    doubao_client = OpenAI(
        api_key=doubao_api_key,
        base_url="https://ark.cn-beijing.volces.com/api/v3"
    )
except Exception as e:
    print(f"豆包search客户端初始化失败: {str(e)}")
    doubao_client = None



# 自定义下载目录
download_directory = os.path.join(os.getcwd(), "C:\\Users\\PC\\eclipse-workspace\\LibrarySearch\\src\\main\\resources\\static\\books")
if not os.path.exists(download_directory):
    os.makedirs(download_directory)

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '13380008373',
    'database': 'library',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

import atexit
def check_pid(pid):
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True

import re
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

# 工具函数
def generate_hash(input_string):
    """生成SHA-256哈希值"""
    return hashlib.sha256(input_string.encode('utf-8')).hexdigest()

def get_db_connection():
    """获取数据库连接并确保表存在"""
    conn = pymysql.connect(**DB_CONFIG)
    check_tables(conn)
    return conn

def clean_recommendations(raw_text):
    """智能清洗推荐结果"""
    try:
        cleaned = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\-\s，,;；、]', '', raw_text)
        
        if "：" in cleaned:
            cleaned = cleaned.split("：")[-1]
        elif ":" in cleaned:
            cleaned = cleaned.split(":")[-1]
            
        cleaned = re.sub(r'[,\s;；、]+', '，', cleaned)
        terms = [term.strip() for term in cleaned.split('，') if term.strip()]
        return terms[:10]
    except Exception as e:
        app.logger.error(f"清洗异常: {str(e)}")
        return []

# 保护路由的装饰器
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_LOGIN)

@app.route('/set_session', methods=['POST'])
def set_session():
    user_email = request.form.get('email')
    if user_email:
        session['user_email'] = user_email
        return jsonify({'success': True})
    else:
        return jsonify({'success': False}), 400

# 保护路由的装饰器
from functools import wraps


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# 保护原有路由
@app.route('/list', methods=['GET'])
@login_required
def list_files():
    user_email = session.get('user_email', 'Unknown')
    print(f"User email (list files): {user_email}")
    files = os.listdir(download_directory)
    if files:
        return jsonify({"files": files}), 200
    else:
        return jsonify({"message": "No files found in the download directory"}), 200

@app.route('/download/<filename>', methods=['GET'])
@login_required
def serve_file(filename):
    user_email = session.get('user_email', 'Unknown')
    
    # 记录下载日志到数据库
    try:
        # 分别计算哈希值
        email_hash = hashlib.sha256(user_email.encode('utf-8')).hexdigest()
        filename_hash = hashlib.sha256(filename.encode('utf-8')).hexdigest()
        
        print(f"User downloaded " + filename + ": email = "+ user_email)

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO DownloadHistory 
            (user_email, filename, email_hash, filename_hash)
            VALUES (%s, %s, %s, %s)
        ''', (user_email, filename, email_hash, filename_hash))
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error saving download record: {str(e)}")

    file_path = os.path.join(download_directory, filename)
    if os.path.exists(file_path):
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )
    else:
        return jsonify({"error": "File not found"}), 404
    
@app.route('/search_downloads', methods=['GET'])
def search_downloads():
    search_type = request.args.get('type')  # 'email' 或 'filename'
    search_value = request.args.get('value')

@app.route('/SearchBookByTitle', methods=['GET', 'POST'])
def SearchBookByTitle():
    if request.method == 'GET':
        return render_template('SearchBookByTitle.html')
        
    book_title = request.form['book_title'].strip()
    if not book_title:
        return render_template('SearchBookByTitle.html', message="Please enter a book title")
    
    books_data_dir = os.path.join(os.getcwd(), "src/main/resources/static/books_data")
    results = []
    
    # 1. 先按首字母搜索
    first_char = book_title[0].lower()
    if first_char.isalpha():
        search_dir = os.path.join(books_data_dir, first_char.upper())
        json_files = glob.glob(os.path.join(search_dir, '*.json'))
        
        for json_file in json_files:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if book_title.lower() in data['title'].lower():
                    results.append(data)
    
    # 2. 如果没有结果，搜索中文目录
    if not results and any('\u4e00' <= c <= '\u9fff' for c in book_title):
        first_char_cn = book_title[0]
        search_dir = os.path.join(books_data_dir, '中文', first_char_cn)
        json_files = glob.glob(os.path.join(search_dir, '*.json'))
        
        for json_file in json_files:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if book_title in data['title']:
                    results.append(data)
    
    if results:
        return render_template('SearchBookByTitle.html', search_results=results)
    else:
        return render_template('SearchBookByTitle.html', 
                            message=f"No records found for '{book_title}'")

    if not search_type or not search_value:
        return jsonify({"error": "Missing parameters"}), 400
    
    try:
        # 根据类型计算哈希
        if search_type == 'email':
            search_hash = hashlib.sha256(search_value.encode('utf-8')).hexdigest()
            sql_condition = "email_hash = %s"
        elif search_type == 'filename':
            search_hash = hashlib.sha256(search_value.encode('utf-8')).hexdigest()
            sql_condition = "filename_hash = %s"
        else:
            return jsonify({"error": "Invalid search type"}), 400

        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute(f'''
            SELECT * FROM DownloadHistory 
            WHERE {sql_condition}
            ORDER BY download_date DESC
        ''', (search_hash,))
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({"results": results}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/submit_ticket', methods=['POST'])
@login_required
def submit_ticket():
    book_title = request.form['book_title']
    clerk_user_email = session.get('user_email', 'user@example.com')
    
    # 计算书名的哈希值
    book_hash = hashlib.sha256(book_title.encode()).hexdigest()
    
    # 插入工单到数据库
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO NotebookLMAudioRequests (book_title, book_hash, clerk_user_email)
        VALUES (%s, %s, %s)
    ''', (book_title, book_hash, clerk_user_email))
    conn.commit()
    cursor.close()
    conn.close()
    
    return redirect(url_for('index'))

# 搜索文件夹中的关键词
@app.route('/search', methods=['GET'])
def search_books():
    from urllib.parse import unquote
    
    book_name = request.args.get('book_name')
    if not book_name:
        return jsonify({"error": "book_name is required"}), 400
        
    # 解码URL编码的特殊字符
    decoded_book_name = unquote(book_name)
    print(f"原始搜索词: {book_name}, 解码后: {decoded_book_name}")

    # 多级回退搜索策略
    search_terms = [
        decoded_book_name,  # 原始搜索词
        ' '.join(decoded_book_name.split()[:2]) if len(decoded_book_name.split()) > 2 else None,  # 前两个词
        decoded_book_name.split()[0] if len(decoded_book_name.split()) >= 1 else None,  # 第一个词
        decoded_book_name[:4] if len(decoded_book_name) >= 4 else None,  # 前四个字母
        decoded_book_name[:2] if len(decoded_book_name) >= 2 else None,  # 前两个字母
        decoded_book_name.split(' ')[0] if ' ' in decoded_book_name else None,  # 第一个词方法2
    ]
    
    # 移除None值
    search_terms = [term for term in search_terms if term is not None]
    
    matching_files = []
    seen_files = set()  # 用于去重
    
    for term in search_terms:
        # 不区分大小写的搜索
        pattern = os.path.join(download_directory, f"*{term}*")
        current_matches = [
            f for f in glob.glob(pattern, recursive=True) 
            if f.lower() not in seen_files
        ]
        
        if current_matches:
            seen_files.update(f.lower() for f in current_matches)
            matching_files.extend(current_matches)
            print(f"使用搜索词 '{term}' 找到 {len(current_matches)} 个匹配文件")
            break  # 找到匹配就停止

    if matching_files:
            # 生成带有下载链接的 HTML 内容
        file_links = [
                f'<li class="list-group-item"><span>{os.path.basename(f)}</span>'
                f'<a href="/download/{os.path.basename(f)}" class="btn btn-success btn-sm" target="_blank">Download</a>'
                f'<a href="https://313m929k61.vicp.fun/search/books?book_name={os.path.basename(f)}" class="btn btn-info btn-sm" target="_blank">查询该文件ID</a>'
                f'<a href="/doubao_chat?query={os.path.basename(f).replace("(Z-Library)","").rsplit(".", 1)[0]}" class="btn btn-primary btn-sm">Chat with Doubao</a>'
                
                f'<form method="POST" action="/submit_ticket" style="display:inline;">'
                f'<input type="hidden" name="book_title" value="{os.path.basename(f)}">'
                f'<input type="hidden" name="clerk_user_email" value="user@example.com">'
                f'<button type="submit" class="btn btn-warning btn-sm">Submit Ticket</button>'
                f'</form></li>'
                for f in matching_files
            ]
        # 渲染模板
        return render_template(
            'search_results.html',
            file_links=file_links
        )
    else:
        return jsonify({"message": "No matching files found"}), 200


@app.route('/filemainpage', methods=['GET'])
@login_required
def filemainpage():
    # Pagination parameters
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))

    # Fetch list of files
    files = os.listdir(download_directory)
    total_files = len(files)
    total_pages = ceil(total_files / per_page)

    # Paginate files
    start = (page - 1) * per_page
    end = start + per_page
    paginated_files = files[start:end]

    return render_template('filemainpage.html', files=paginated_files, page=page, per_page=per_page, total_pages=total_pages)

@app.route('/set_user_session', methods=['POST'])
def set_user_session():
    user_email = request.form.get('email')
    if user_email:
        session['user_email'] = user_email
        return jsonify({'success': True})
    else:
        return jsonify({'success': False}), 400
    
from functools import wraps

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_email' not in session:
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/tickets')
@login_required
def tickets():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM NotebookLMAudioRequests')
    tickets = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('tickets.html', tickets=tickets)

@app.route('/update_status/<int:ticket_id>/<status>')
@login_required
def update_status(ticket_id, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE NotebookLMAudioRequests
        SET status = %s
        WHERE id = %s
    ''', (status, ticket_id))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('tickets'))

@app.route('/api/chat/histories', methods=['GET'])
def forward_to_10806():
    """从10805转发请求到10806的/api/chat/histories"""
    try:
        import requests
        # 构建目标URL
        target_url = 'http://localhost:10806/api/chat/histories'
        
        # 设置请求头
        headers = {
            'Content-Type': 'application/json',
            'X-Forwarded-Port': '10805'
        }
        
        # 转发请求参数
        params = dict(request.args)
        
        # 发送请求（3秒超时）
        response = requests.get(
            target_url,
            headers=headers,
            params=params,
            timeout=3
        )
        
        # 返回响应
        return (response.content, 
                response.status_code,
                response.headers.items())
                
    except requests.Timeout:
        app.logger.error("转发到10806超时")
        return jsonify({'error': 'Service timeout'}), 504
    except requests.RequestException as e:
        app.logger.error(f"转发请求失败: {str(e)}")
        return jsonify({'error': 'Forwarding failed'}), 502
    except Exception as e:
        app.logger.error(f"转发异常: {str(e)}")
        return jsonify({'error': 'Internal error'}), 500

import subprocess

# 添加推荐服务路由
@app.route('/recommend', methods=['GET', 'POST'])
def recommendation_form():
    """推荐查询表单页面"""
    if request.method == 'POST':
        user_email = request.form.get('user_email')
        if not user_email:
            return render_template('form.html', error="邮箱不能为空")

        email_hash = generate_hash(user_email)
        try:
            connection = get_db_connection()
            with connection.cursor() as cursor:
                sql = """SELECT filename FROM DownloadHistory 
                        WHERE email_hash = %s 
                        ORDER BY download_date DESC LIMIT 50"""
                cursor.execute(sql, (email_hash,))
                history = [row['filename'] for row in cursor.fetchall()]
                
                if not history:
                    return render_template('form.html', error="没有找到下载记录")
        except Exception as e:
            app.logger.error(f"数据库查询失败: {str(e)}")
            return render_template('form.html', error="查询历史记录失败")
        finally:
            connection.close()

        prompt = f"""根据以下文件下载记录（按时间倒序），分析用户兴趣并生成5个搜索关键词：
        {', '.join(history)}
        推荐关键词："""

        try:
            if not doubao_client:
                raise Exception("豆包search客户端未初始化")
                
            response = doubao_client.chat.completions.create(
                model="bot-20250506042211-5bscp",
                messages=[
                    {"role": "system", "content": "你是一个专业的用户行为分析师"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            raw_recommendations = response.choices[0].message.content.strip()
            
            terms_pool = clean_recommendations(raw_recommendations)
            clean_terms = []
            for term in terms_pool:
                if re.search(r'[\u4e00-\u9fa5]', term):
                    clean_term = re.sub(r'[^\u4e00-\u9fa5\-]', '', term)
                    if 2 <= len(clean_term) <= 10:
                        clean_terms.append(clean_term)
                else:
                    clean_term = re.sub(r'[^a-zA-Z0-9\- ]', '', term).strip()
                    if len(clean_term.split()) >= 2:
                        clean_terms.append(clean_term)

            # 空值处理机制
            if not clean_terms:
                app.logger.warning("清洗后关键词为空，使用备选方案")
                clean_terms = ["学术论文", "研究报告", "技术文档"]
            elif len(clean_terms) < 3:
                fallback_terms = list(set([
                    re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]', '', f.split('__')[0].split('(')[0].strip())
                    for f in history
                ]))[:5]
                clean_terms += fallback_terms[:3-len(clean_terms)]

            final_terms = clean_terms[:5]

            # 写入数据库
            try:
                conn = get_db_connection()
                with conn.cursor() as cursor:
                    sql = """INSERT INTO SearchRecommendations 
                            (user_email, email_hash, search_terms)
                            VALUES (%s, %s, %s)"""
                    app.logger.debug(f"插入数据: {user_email}, {email_hash}, {final_terms}")
                    cursor.execute(sql, (
                        user_email, 
                        email_hash, 
                        ','.join(final_terms)
                    ))
                conn.commit()
                app.logger.info(f"成功存储推荐: {user_email}")
            except Exception as e:
                app.logger.error(f"数据库写入失败: {str(e)}")
                app.logger.error(traceback.format_exc())
            finally:
                conn.close()

            return render_template('result.html',
                                 email=user_email,
                                 recommendations=final_terms,
                                 generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        except Exception as e:
            app.logger.error(f"API调用失败: {str(e)}")
            return render_template('form.html', error="推荐生成失败，请稍后重试")

    return render_template('form.html')

@app.route('/view_recommendations')
def view_recommendations():
    """查看推荐记录"""
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """SELECT * FROM SearchRecommendations 
                    ORDER BY created_at DESC LIMIT 100"""
            cursor.execute(sql)
            records = cursor.fetchall()
            
        return render_template('view_recommendations.html',
                             recommendations=records)
    except Exception as e:
        app.logger.error(f"记录查询失败: {str(e)}")
        return render_template('error.html', error="无法获取推荐记录")
    finally:
        connection.close()

@app.route('/doubao_chat', methods=['GET'])
def handle_chat_page():
    """转发聊天页面请求到10806端口"""
    import requests
    response = requests.get(f'http://localhost:10806/?{request.query_string.decode()}')
    return response.content, response.status_code, response.headers.items()

@app.route('/api/doubao/chat', methods=['POST'])
def doubao_chat_api():
    """统一转发所有豆包API请求到10806端口"""
    try:
        import requests
        # 获取原始请求路径
        original_path = request.headers.get('X-Original-Path', '/api/doubao/chat')
        
        # 构建转发URL
        forward_url = f'http://localhost:10806{original_path}'
        
        # 处理multipart/form-data类型的请求
        if 'multipart/form-data' in request.content_type:
            files = {'file': (request.files['file'].filename, request.files['file'].stream, request.files['file'].mimetype)}
            data = request.form.to_dict()
            response = requests.post(
                forward_url,
                files=files,
                data=data
            )
        # 处理application/json类型的请求
        elif request.content_type == 'application/json':
            headers = {'Content-Type': request.content_type}
            response = requests.post(
                forward_url,
                json=request.get_json(),
                headers=headers
            )
        # 处理其他类型的请求
        else:
            headers = {'Content-Type': request.content_type}
            response = requests.post(
                forward_url,
                data=request.form.to_dict(),
                headers=headers
            )
        
        return jsonify(response.json()), response.status_code
        
    except Exception as e:
        return jsonify({
            'error': str(e),
            'message': 'Failed to forward request to Doubao service'
        }), 500

@app.route('/', methods=['GET'])
def forward_root():
    """转发根路径请求到/api/doubao/chat"""
    import requests
    request.headers['X-Original-Path'] = '/'
    return doubao_chat_api()

@app.route('/c/<chat_id>', methods=['GET'])
def forward_chat_page(chat_id):
    """转发聊天页面请求到/api/doubao/chat"""
    import requests
    request.headers['X-Original-Path'] = f'/c/{chat_id}'
    return doubao_chat_api()

@app.route('/api/doubao/websearch', methods=['POST'])
def forward_websearch():
    """转发web搜索请求到/api/doubao/chat"""
    request.headers['X-Original-Path'] = '/api/doubao/websearch'
    return doubao_chat_api()

@app.route('/api/doubao/url_parse', methods=['POST'])
def forward_url_parse():
    """转发URL解析请求到/api/doubao/chat"""
    request.headers['X-Original-Path'] = '/api/doubao/url_parse'
    return doubao_chat_api()

@app.route('/api/chat/histories', methods=['GET'])
def forward_chat_histories():
    """转发聊天历史列表请求到/api/doubao/chat"""
    new_headers = dict(request.headers)
    new_headers['X-Original-Path'] = '/api/chat/histories'
    request.environ['werkzeug.headers'] = new_headers
    return doubao_chat_api()

@app.route('/api/chat/histories/list', methods=['GET'])
def forward_chat_histories_list():
    """转发聊天历史列表(HTML)请求到/api/doubao/chat"""
    new_headers = dict(request.headers)
    new_headers['X-Original-Path'] = '/api/chat/histories/list'
    request.environ['werkzeug.headers'] = new_headers
    return doubao_chat_api()

@app.route('/api/chat/history/<history_id>', methods=['GET'])
def forward_get_chat_history(history_id):
    """转发获取聊天历史请求到/api/doubao/chat"""
    new_headers = dict(request.headers)
    new_headers['X-Original-Path'] = f'/api/chat/history/{history_id}'
    request.environ['werkzeug.headers'] = new_headers
    return doubao_chat_api()

@app.route('/api/chat/history', methods=['POST'])
def forward_save_chat_history():
    """转发保存聊天历史请求到/api/doubao/chat"""
    new_headers = dict(request.headers)
    new_headers['X-Original-Path'] = '/api/chat/history'
    request.environ['werkzeug.headers'] = new_headers
    return doubao_chat_api()

@app.route('/api/chat/history/<history_id>', methods=['DELETE'])
def forward_delete_chat_history(history_id):
    """转发删除聊天历史请求到/api/doubao/chat"""
    new_headers = dict(request.headers)
    new_headers['X-Original-Path'] = f'/api/chat/history/{history_id}'
    request.environ['werkzeug.headers'] = new_headers
    return doubao_chat_api()

@app.route('/download_history', methods=['GET', 'POST'])
def download_history():
    """查询下载记录"""
    if request.method == 'POST':
        user_email = request.form.get('user_email')
        if not user_email:
            return render_template('download_history_form.html', error="请输入邮箱地址")

        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                # 查询下载记录
                cursor.execute('''
                    SELECT filename, download_date 
                    FROM DownloadHistory 
                    WHERE user_email = %s 
                    ORDER BY download_date DESC
                ''', (user_email,))
                records = cursor.fetchall()
                
                if not records:
                    return render_template('download_history_form.html', 
                                        error="没有找到该邮箱的下载记录")
                
                return render_template('download_history_results.html',
                                    email=user_email,
                                    records=records)
        except Exception as e:
            app.logger.error(f"查询下载记录失败: {str(e)}")
            return render_template('download_history_form.html', 
                                error="查询失败，请稍后重试")
        finally:
            conn.close()
    
    return render_template('download_history_form.html')

# 清理重复文件
remove_duplicate_files(download_directory)




from threading import Thread
import time
import atexit
from flask import Flask

# 创建独立的应用实例避免冲突

doubao_app = Flask(__name__)
main_app = Flask(__name__)

def run_doubao_service():
    """运行豆包聊天服务(使用doubao_combined_service的实现)"""
    from doubao_combined_service import app
    app.run(host='0.0.0.0', port=10806, debug=False)

# 创建并启动服务线程
doubao_thread = Thread(target=run_doubao_service, daemon=True)
time.sleep(1)  # 间隔启动
doubao_thread.start()
time.sleep(1)  # 确保服务启动

# 注册退出清理
atexit.register(lambda: [t.join(timeout=1) for t in [doubao_thread]])
try:

# 启动主应用
    if __name__ == '__main__':
    # 创建并启动服务线程
        doubao_thread = Thread(target=run_doubao_service, daemon=True)
        doubao_thread.start()
        time.sleep(1)  # 确保服务启动
    
    # 启动主应用
        app.run(host='0.0.0.0', port=10805, debug=False)
finally:
    # 确保线程退出
    doubao_thread.join(timeout=1)

