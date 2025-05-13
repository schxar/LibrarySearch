from flask import Flask, Response, render_template, request, jsonify, send_file, render_template_string, redirect, url_for, session, send_from_directory
from flask_caching import Cache
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
from openai import OpenAI
import pymysql
import re
import traceback
from dotenv import load_dotenv

from doubao_vlm_service import vlm_upload as doubao_vlm_upload, chat as doubao_chat


# 加载环境变量
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'your_secret_key')
app.config['CACHE_TYPE'] = 'SimpleCache'
cache = Cache(app)

# DeepSeek客户端配置
try:
    with open("flask_openai_backend/deepseek.txt", "r") as f:
        DeepSeek_API_KEY = f.read().strip()
    
    deepseek_client = OpenAI(
        api_key=DeepSeek_API_KEY,
        base_url="https://api.deepseek.com"
    )
except Exception as e:
    print(f"DeepSeek初始化失败: {str(e)}")
    deepseek_client = None



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

# 创建工单表
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS NotebookLMAudioRequests (
            id INT AUTO_INCREMENT PRIMARY KEY,
            book_title VARCHAR(255) NOT NULL,
            book_hash VARCHAR(64) NOT NULL,
            request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            clerk_user_email VARCHAR(255) NOT NULL,
            status ENUM('pending', 'processing', 'completed') DEFAULT 'pending'
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

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
    return render_template('login.html')

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
                f'<a href="{DOUBAO_SERVICE_URL}/doubao_chat?query={os.path.basename(f).replace("(Z-Library)","").rsplit(".", 1)[0]}" class="btn btn-primary btn-sm">Chat with Doubao</a>'
                
                f'<form method="POST" action="/submit_ticket" style="display:inline;">'
                f'<input type="hidden" name="book_title" value="{os.path.basename(f)}">'
                f'<input type="hidden" name="clerk_user_email" value="user@example.com">'
                f'<button type="submit" class="btn btn-warning btn-sm">Submit Ticket</button>'
                f'</form></li>'
                for f in matching_files
            ]
        # 添加缓存键
        cache_key = f"search:{book_name}"
        
        # 尝试从缓存获取
        cached_result = app.extensions['cache'].get(cache_key)
        if cached_result is not None:
            return cached_result
            
        # 渲染模板
        result = render_template(
            'search_results.html',
            file_links=file_links
        )
        
        # 设置缓存，有效期5分钟
        cache.set(cache_key, result, timeout=300)
        return result
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
    return render_template_string(
        """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Tickets</title>
            <!-- Bootstrap CSS -->
            <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            <div class="container">
                <h1 class="text-center mb-4">Tickets</h1>
                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Book Title</th>
                            <th>Book Hash</th>
                            <th>Request Date</th>
                            <th>Clerk User Email</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for ticket in tickets %}
                        <tr>
                            <td>{{ ticket.id }}</td>
                            <td>{{ ticket.book_title }}</td>
                            <td>{{ ticket.book_hash }}</td>
                            <td>{{ ticket.request_date }}</td>
                            <td>{{ ticket.clerk_user_email }}</td>
                            <td>{{ ticket.status }}</td>
                            <td>
                                <a href="/update_status/{{ ticket.id }}/pending" class="btn btn-warning btn-sm">Pending</a>
                                <a href="/update_status/{{ ticket.id }}/processing" class="btn btn-info btn-sm">Processing</a>
                                <a href="/update_status/{{ ticket.id }}/completed" class="btn btn-success btn-sm">Completed</a>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            <!-- Bootstrap JS -->
            <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        </body>
        </html>
        """,
        tickets=tickets
    )

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
            if not deepseek_client:
                raise Exception("DeepSeek客户端未初始化")
                
            response = deepseek_client.chat.completions.create(
                model="deepseek-chat",
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

@app.route('/chat', methods=['GET'])
def handle_chat_page():
    """处理聊天页面请求"""
    query = request.args.get('query', '')
    return render_template('doubao_chat.html', query=query)

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







    # 启动豆包VLM服务
#doubao_vlm_process = subprocess.Popen(
#    ['python', 'flask_openai_backend\\doubao_vlm_service.py'],
#    cwd=os.getcwd()  # 确保工作目录正确
#    )
    
    # 启动主应用
#try:
app.run(host='0.0.0.0', port=10805, debug=True)
#finally:
        # 确保主应用退出时终止子进程
#    doubao_vlm_process.terminate()