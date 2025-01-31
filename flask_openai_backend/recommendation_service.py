from flask import Flask, request, jsonify, send_file, render_template
from openai import OpenAI
import hashlib
import pymysql
import os
import re
import traceback
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '13380008373',  # 请确认密码是否正确
    'database': 'library',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# DeepSeek客户端配置
try:
    with open("flask_openai_backend/deepseek.txt", "r") as f:
        DeepSeek_API_KEY = f.read().strip()
    
    deepseek_client = OpenAI(
        api_key=DeepSeek_API_KEY,
        base_url="https://api.deepseek.com"
    )
except Exception as e:
    print(f"初始化失败: {str(e)}")
    exit(1)

# 工具函数
def generate_hash(input_string):
    """生成SHA-256哈希值"""
    return hashlib.sha256(input_string.encode('utf-8')).hexdigest()

def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)

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

# 路由定义
@app.route('/', methods=['GET', 'POST'])
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

@app.route('/download', methods=['POST'])
def handle_download():
    """处理下载请求"""
    data = request.get_json()
    if not data or 'user_email' not in data or 'filename' not in data:
        return jsonify({"error": "Invalid request"}), 400

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = """INSERT INTO DownloadHistory 
                    (user_email, filename, email_hash, filename_hash)
                    VALUES (%s, %s, %s, %s)"""
            cursor.execute(sql, (
                data['user_email'],
                data['filename'],
                generate_hash(data['user_email']),
                generate_hash(data['filename'])
            ))
        conn.commit()
    except Exception as e:
        app.logger.error(f"下载记录失败: {str(e)}")
        return jsonify({"error": "Database error"}), 500
    finally:
        conn.close()

    return send_file(f"/downloads/{data['filename']}", as_attachment=True)

if __name__ == '__main__':
    # 启动前检查表结构
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # 自动创建表（生产环境建议手动执行）
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS SearchRecommendations (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_email VARCHAR(255) NOT NULL,
                    email_hash VARCHAR(64) NOT NULL,
                    search_terms TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) CHARSET=utf8mb4;
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS DownloadHistory (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_email VARCHAR(255) NOT NULL,
                    filename VARCHAR(255) NOT NULL,
                    email_hash VARCHAR(64) NOT NULL,
                    filename_hash VARCHAR(64) NOT NULL,
                    download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                ) CHARSET=utf8mb4;
            """)
        conn.commit()
        print("表结构验证完成")
    except Exception as e:
        print(f"表结构验证失败: {str(e)}")
        exit(1)
    finally:
        conn.close()

    app.run(host='0.0.0.0', port=10811, debug=False)  # 关闭debug模式