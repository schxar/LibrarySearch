from flask import Flask, render_template, request, jsonify, send_file, render_template_string, redirect, url_for, session
import os
import glob
from math import ceil
import mysql.connector
import hashlib
from datetime import datetime

app = Flask(__name__)

# 设置SECRET_KEY用于session
app.config['SECRET_KEY'] = 'your_secret_key'

# 自定义下载目录
download_directory = os.path.join(os.getcwd(), "C:\\Users\\PC\\eclipse-workspace\\LibrarySearch\\src\\main\\resources\\static\\books")
if not os.path.exists(download_directory):
    os.makedirs(download_directory)

# 数据库配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '13380008373',
    'database': 'library'
}

# 连接数据库
def get_db_connection():
    conn = mysql.connector.connect(**db_config)
    return conn

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

# 登录页面HTML模板
HTML_LOGIN = """
<!-- Updated login HTML template -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Flask Test with Clerk</title>
    <!-- Include Bootstrap CSS for styling -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Include jQuery -->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>

    <!-- Clerk SDK -->
    <script
        async
        crossorigin="anonymous"
        data-clerk-publishable-key="pk_test_bGFyZ2UtY3JheWZpc2gtMzIuY2xlcmsuYWNjb3VudHMuZGV2JA"
        src="https://intense-guppy-8.clerk.accounts.dev/npm/@clerk/clerk-js@latest/dist/clerk.browser.js"
        type="text/javascript"
    ></script>
</head>
<body class="container mt-5">
    <h1 class="mb-4">Flask Test with Clerk Authentication</h1>

    <!-- User Interface Placeholder -->
    <div id="app"></div>

    <!-- New Button for File Main Page (Hidden by default, shown after login) -->
    <div id="fileMainButton" class="mt-4" style="display: none;">
        <button class="btn btn-primary" onclick="window.location.href='/filemainpage'">Go to File Main Page</button>
    </div>

    <!-- New Button for NotebookLM -->
    <div class="mt-4 text-center">
        <a href="https://notebooklm.google.com/" target="_blank" class="btn btn-success">Go to NotebookLM</a>
    </div>

    <script>
        window.addEventListener('load', async function () {
            // Initialize Clerk
            await Clerk.load();

            // Check if the user is logged in
            if (Clerk.user) {
                // Show user button
                document.getElementById('app').innerHTML = '<div id="user-button"></div>';
                Clerk.mountUserButton(document.getElementById('user-button'));

                // Show the file main page button for logged-in users
                $("#fileMainButton").show();

    // Set session user_email
    $.ajax({
        url: '/set_user_session',
        type: 'POST',
        data: { email: Clerk.user.emailAddresses[0].emailAddress },
        success: function(response) {
            console.log('Session set:', response);
        },
        error: function(error) {
            console.error('Failed to set session:', error);
        }
    });
            } else {
                // Show sign-in button for non-logged-in users
                document.getElementById('app').innerHTML = '<div id="sign-in"></div>';
                Clerk.mountSignIn(document.getElementById('sign-in'));

                // Hide the file main page button for non-logged-in users
                $("#fileMainButton").hide();
            }
        });
    </script>
</body>
</html>
"""

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
    print(f"User downloaded " + filename + ": email = "+ user_email)
    file_path = os.path.join(download_directory, filename)
    if os.path.exists(file_path):
        return send_file(
            file_path,
            as_attachment=True,  # 强制浏览器下载
            download_name=filename  # 下载时的文件名
        )
    else:
        return jsonify({"error": "File not found"}), 404

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
    book_name = request.args.get('book_name')
    if not book_name:
        return jsonify({"error": "book_name is required"}), 400

    # 使用 glob 模糊匹配文件名
    pattern = os.path.join(download_directory, f"*{book_name}*")
    matching_files = glob.glob(pattern)

    if matching_files:
        # 生成带有下载链接的 HTML 内容
        file_links = [
            f'<li class="list-group-item"><span>{os.path.basename(f)}</span>'
            f'<a href="/download/{os.path.basename(f)}" class="btn btn-success btn-sm" target="_blank">Download</a>'
            f'<form method="POST" action="/submit_ticket" style="display:inline;">'
            f'<input type="hidden" name="book_title" value="{os.path.basename(f)}">'
            f'<input type="hidden" name="clerk_user_email" value="user@example.com">'
            f'<button type="submit" class="btn btn-warning btn-sm">Submit Ticket</button>'
            f'</form></li>'
            for f in matching_files
        ]
        return render_template_string(
            """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Search Results</title>
                <!-- Bootstrap CSS -->
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    body {
                        background-color: #f8f9fa;
                        padding: 20px;
                    }
                    .card {
                        margin-bottom: 20px;
                        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                    }
                    .card-header {
                        background-color: #007bff;
                        color: white;
                    }
                    .list-group-item {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                    }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1 class="text-center mb-4">Search Results</h1>
                    <div class="card">
                        <div class="card-header">
                            <h2 class="card-title mb-0">Matching Files</h2>
                        </div>
                        <div class="card-body">
                            <ul class="list-group">
                                {{ file_links | safe }}
                            </ul>
                        </div>
                    </div>
                </div>
                <!-- Bootstrap JS -->
                <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
            </body>
            </html>
            """,
            file_links="".join(file_links)
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
    cursor = conn.cursor(dictionary=True)
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

if __name__ == '__main__':
    create_table()
    app.run(host='0.0.0.0', port=10805)