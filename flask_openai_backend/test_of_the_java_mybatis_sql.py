from flask import Flask, render_template
import pymysql

app = Flask(__name__)

# 数据库配置（根据你的实际配置修改）
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '13380008373',
    'database': 'library',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

@app.route('/')
def show_history():
    try:
        # 连接数据库
        connection = pymysql.connect(**db_config)
        
        with connection.cursor() as cursor:
            # 执行查询
            sql = "SELECT * FROM search_history ORDER BY search_date DESC"
            cursor.execute(sql)
            results = cursor.fetchall()
            
        return render_template('javasql.html', history=results)
        
    except Exception as e:
        return f"数据库查询失败: {str(e)}"
    finally:
        if connection:
            connection.close()

if __name__ == '__main__':
    app.run(debug=True, port=10810)