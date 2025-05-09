from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import hashlib
from datetime import datetime

app = Flask(__name__)

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

# 首页路由
@app.route('/')
def index():
    return render_template('submit.html')

# 提交工单路由
@app.route('/submit', methods=['POST'])
def submit():
    book_title = request.form['book_title']
    clerk_user_email = request.form['clerk_user_email']
    
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

# 查看工单路由
@app.route('/tickets')
def tickets():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM NotebookLMAudioRequests')
    tickets = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('tickets.html', tickets=tickets)

# 更新工单状态路由
@app.route('/update_status/<int:ticket_id>/<status>')
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
    app.run(debug=True, host='0.0.0.0', port=10806)