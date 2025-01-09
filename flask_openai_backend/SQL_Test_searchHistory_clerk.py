from flask import Flask, request, jsonify, render_template
import mysql.connector

app = Flask(__name__)

# 数据库配置
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '13380008373',
    'database': 'library'
}

# 创建数据库连接
def get_db_connection():
    return mysql.connector.connect(**db_config)

# 创建 SearchHistory 表（如果不存在）
def create_search_history_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS SearchHistory (
            id INT AUTO_INCREMENT PRIMARY KEY,
            clerk_user_email VARCHAR(255) NOT NULL,
            search_query VARCHAR(255) NOT NULL,
            search_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

# 主页：显示表单和数据
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # 处理表单提交
        clerk_user_email = request.form.get('clerk_user_email')
        search_query = request.form.get('search_query')

        if not clerk_user_email or not search_query:
            return "Missing clerk_user_email or search_query", 400

        conn = get_db_connection()
        cursor = conn.cursor()

        # 插入数据到 SearchHistory 表
        sql = '''
            INSERT INTO SearchHistory (clerk_user_email, search_query)
            VALUES (%s, %s)
        '''
        cursor.execute(sql, (clerk_user_email, search_query))
        conn.commit()
        cursor.close()
        conn.close()

    # 查询数据库中的所有数据
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM SearchHistory ORDER BY search_timestamp DESC')
    search_history = cursor.fetchall()
    cursor.close()
    conn.close()

    # 渲染 HTML 页面
    return render_template('SQL.html', search_history=search_history)

if __name__ == '__main__':
    create_search_history_table()
    app.run(debug=True,host='0.0.0.0', port=10805)
