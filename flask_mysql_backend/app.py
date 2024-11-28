from flask import Flask, request, jsonify, render_template
from flask_restful import Api, Resource
import mysql.connector

app = Flask(__name__)
api = Api(app)

# 数据库连接配置
db_config = {
    'host': 'localhost',
    'port': 3306,
    'user': 'root',
    'password': '13380008373',
    'database': 'test_db'  # 替换为你的数据库名
}

# 数据库连接函数
def get_db_connection():
    connection = mysql.connector.connect(**db_config)
    return connection

# 示例资源
class Users(Resource):
    def get(self):
        """获取所有用户"""
        try:
            connection = get_db_connection()
            cursor = connection.cursor(dictionary=True)
            cursor.execute("SELECT * FROM users")  # 替换为你的表名
            result = cursor.fetchall()
            return jsonify(result)
        except Exception as e:
            return {'error': str(e)}, 500
        finally:
            cursor.close()
            connection.close()

    def post(self):
        """添加新用户"""
        try:
            data = request.get_json()
            username = data.get('username')
            email = data.get('email')

            connection = get_db_connection()
            cursor = connection.cursor()
            query = "INSERT INTO users (username, email) VALUES (%s, %s)"
            cursor.execute(query, (username, email))
            connection.commit()
            return {'message': 'User added successfully'}, 201
        except Exception as e:
            return {'error': str(e)}, 500
        finally:
            cursor.close()
            connection.close()

# 注册资源
api.add_resource(Users, '/users')

# 渲染前端页面
@app.route('/')
def index():
    return render_template('index.html')  # 确保 index.html 存在于 templates 文件夹中

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10803, debug=True)
