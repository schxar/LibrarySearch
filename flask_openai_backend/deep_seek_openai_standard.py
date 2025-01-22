from flask import Flask, request, jsonify, send_file
from openai import OpenAI
import hashlib
import pymysql
import os
import re
from datetime import datetime
from dotenv import load_dotenv
from functools import lru_cache

# 加载环境变量
load_dotenv()

deepseek_key_path = "flask_openai_backend/deepseek.txt"

try:
    # Open the file and read its content as a string
    with open(deepseek_key_path, "r") as file:
        DeepSeek_API_KEY = file.read().strip()  # Use .strip() to remove any leading/trailing whitespace or newlines

    # Print the API key or use it as needed
    print(f"API Key: {DeepSeek_API_KEY}")
except FileNotFoundError:
    print("Error: The file was not found.")
except IOError as e:
    print(f"Error reading the file: {e}")

app = Flask(__name__)

# 数据库配置（根据你的实际配置修改）
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '13380008373',
    'database': 'library',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# DeepSeek客户端配置
# DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
deepseek_client = OpenAI(
    api_key=DeepSeek_API_KEY,
    base_url="https://api.deepseek.com"
)

# 工具函数
def generate_hash(input_string):
    """生成SHA-256哈希值"""
    return hashlib.sha256(input_string.encode('utf-8')).hexdigest()

def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)

# 路由处理
@app.route('/download', methods=['POST'])
def handle_download():
    """处理文件下载请求"""
    data = request.get_json()
    if not data or 'user_email' not in data or 'filename' not in data:
        return jsonify({"error": "Invalid request data"}), 400

    user_email = data['user_email']
    filename = data['filename']
    email_hash = generate_hash(user_email)
    filename_hash = generate_hash(filename)

    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """INSERT INTO DownloadHistory 
                    (user_email, filename, email_hash, filename_hash)
                    VALUES (%s, %s, %s, %s)"""
            cursor.execute(sql, (user_email, filename, email_hash, filename_hash))
        connection.commit()
    except Exception as e:
        app.logger.error(f"Database Error: {str(e)}")
        return jsonify({"error": "Database operation failed"}), 500
    finally:
        connection.close()

    # 返回文件（示例实现）
    file_path = f"/downloads/{filename}"
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
        
    return send_file(file_path, as_attachment=True)

from flask import render_template

# 新增智能清洗函数
def clean_recommendations(raw_text):
    """智能清洗推荐结果"""
    try:
        # 保留中文、英文、数字及常用分隔符
        cleaned = re.sub(r'[^\u4e00-\u9fa5a-zA-Z0-9\-\s，,;；、]', '', raw_text)
        
        # 提取核心推荐部分（适配不同响应格式）
        if "：" in cleaned:
            cleaned = cleaned.split("：")[-1]
        elif ":" in cleaned:
            cleaned = cleaned.split(":")[-1]
            
        # 统一分隔符为中文逗号
        cleaned = re.sub(r'[,\s;；、]+', '，', cleaned)
        
        # 过滤空项并截取前10个保证备选
        terms = [term.strip() for term in cleaned.split('，') if term.strip()]
        return terms[:10]
    except Exception as e:
        app.logger.error(f"清洗异常: {str(e)}")
        return []

# 在现有代码基础上添加以下路由

# 修改后的表单处理路由
@app.route('/', methods=['GET', 'POST'])
def recommendation_form():
    """推荐查询表单页面"""
    if request.method == 'POST':
        # 获取表单数据
        user_email = request.form.get('user_email')
        if not user_email:
            return render_template('form.html', error="邮箱不能为空")

        # 查询下载历史
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

        # 构建提示词
        prompt = f"""根据以下文件下载记录（按时间倒序），分析用户兴趣并生成5个搜索关键词。
        要求：
        1. 用中文逗号分隔
        2. 每个关键词2-5个汉字
        3. 按相关性降序排列
        
        下载记录：
        {', '.join(history)}
        
        推荐关键词："""

        # 调用API生成推荐
        try:
            response = deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一个专业的用户行为分析师"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                stream=False
            )
            raw_recommendations = response.choices[0].message.content.strip()
            
            # 清洗推荐结果
            terms_pool = clean_recommendations(raw_recommendations)

            # 处理推荐词
            clean_terms = []
            for term in terms_pool:
                if re.search(r'[\u4e00-\u9fa5]', term):  # 中文处理
                    clean_term = re.sub(r'[^\u4e00-\u9fa5\-]', '', term)
                    if 2 <= len(clean_term) <= 10:
                        clean_terms.append(clean_term)
                else:  # 英文处理
                    clean_term = re.sub(r'[^a-zA-Z0-9\- ]', '', term).strip()
                    if len(clean_term.split()) >= 2:
                        clean_terms.append(clean_term)

            # 保底机制
            if len(clean_terms) < 3:
                fallback_terms = list(set([
                    re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]', '', f.split('__')[0].split('(')[0].strip())
                    for f in history
                ]))[:5]
                clean_terms += fallback_terms[:3-len(clean_terms)]

            final_terms = clean_terms[:5]

            return render_template('result.html',
                                 email=user_email,
                                 recommendations=final_terms,
                                 generated_at=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        except Exception as e:
            app.logger.error(str(e))
            return render_template('form.html', error="推荐生成失败，请稍后重试")

    return render_template('form.html')

# 创建 templates 目录并添加以下文件

@app.route('/recommend', methods=['POST'])
def generate_recommendations():
    """生成搜索推荐"""
    data = request.get_json()
    if not data or 'user_email' not in data:
        return jsonify({"error": "Missing user_email parameter"}), 400

    user_email = data['user_email']
    email_hash = generate_hash(user_email)

    # 查询下载历史
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """SELECT filename FROM DownloadHistory 
                    WHERE email_hash = %s 
                    ORDER BY download_date DESC LIMIT 50"""
            cursor.execute(sql, (email_hash,))
            history = [row['filename'] for row in cursor.fetchall()]
            
            if not history:
                return jsonify({"error": "No download history found"}), 404
    except Exception as e:
        app.logger.error(f"Database Query Error: {str(e)}")
        return jsonify({"error": "Failed to fetch history"}), 500
    finally:
        connection.close()

    # 构造提示词
    prompt = f"""根据以下文件下载记录（按时间倒序），分析用户兴趣并生成5个搜索关键词。
    要求：
    1. 用中文逗号分隔
    2. 每个关键词2-5个汉字
    3. 按相关性降序排列
    
    下载记录：
    {', '.join(history)}
    
    推荐关键词："""

    # 调用DeepSeek API
    try:
        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个专业的用户行为分析师"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            stream=False
        )
        raw_recommendations = response.choices[0].message.content.strip()
        
        # 数据清洗
        # 使用相同的清洗逻辑
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

        if len(clean_terms) < 3:
            fallback_terms = list(set([
                re.sub(r'[^a-zA-Z0-9\u4e00-\u9fa5]', '', f.split('__')[0].split('(')[0].strip())
                for f in history
            ]))[:5]
            clean_terms += fallback_terms[:3-len(clean_terms)]

        final_terms = clean_terms[:5]

    except Exception as e:
        app.logger.error(f"DeepSeek API Error: {str(e)}")
        return jsonify({"error": "Failed to generate recommendations"}), 500

    # 存储推荐结果
    try:
        connection = get_db_connection()
        with connection.cursor() as cursor:
            sql = """INSERT INTO SearchRecommendations 
                    (user_email, email_hash, search_terms)
                    VALUES (%s, %s, %s)"""
            cursor.execute(sql, (
                user_email, 
                email_hash, 
                ','.join(clean_terms)
            ))
        connection.commit()
        return jsonify({
            "user_email": user_email,
            "recommendations": clean_terms,
            "generated_at": datetime.utcnow().isoformat()
        })
    except Exception as e:
        app.logger.error(f"Recommendation Save Error: {str(e)}")
        return jsonify({"error": "Failed to save recommendations"}), 500
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10811, debug=os.getenv('FLASK_DEBUG', False))