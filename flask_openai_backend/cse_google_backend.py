from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
from bs4 import BeautifulSoup
import hashlib
import datetime

app = Flask(__name__)

CACHE_DIR = "search_cache"  # 缓存目录

# 创建缓存目录（如果不存在）
if not os.path.exists(CACHE_DIR):
    os.makedirs(CACHE_DIR)

# 设置 Selenium 浏览器选项
def create_webdriver():
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # 无头模式
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    return driver

def calculate_cache_filename(query):
    """
    根据搜索词计算缓存文件名（使用 MD5 哈希保证唯一性），并加上时间戳。
    """
    # 计算当前时间戳
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    # 使用 MD5 哈希计算唯一文件名
    hash_query = hashlib.md5(query.encode('utf-8')).hexdigest()
    # 拼接缓存的文件路径
    filename = f"{timestamp}_{hash_query}.html"
    full_path = os.path.join(CACHE_DIR, filename)
    return full_path

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')  # 从请求参数中获取搜索词
    if not query:
        return jsonify({"error": "Missing 'q' query parameter"}), 400

    # 拼接 URL
    url = f"https://cse.google.com/cse?cx=b7a4dfc41bb40428c&key=AIzaSyCa4mngFulV3OzlW3Dw2Y-4xAJ3DsupgMg&q={query}"

    # 计算缓存对应文件名
    cache_file = calculate_cache_filename(query)

    # 如果缓存文件存在，直接读取缓存
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as file:
            html_content = file.read()
    else:
        # 启动 Selenium 浏览器
        driver = create_webdriver()
        try:
            # 访问目标 URL
            driver.get(url)
            time.sleep(2)  # 等待页面加载

            # 保存 HTML 到缓存文件
            html_content = driver.page_source
            with open(cache_file, "w", encoding="utf-8") as file:
                file.write(html_content)
        except Exception as e:
            return jsonify({"error": str(e)}), 500
        finally:
            driver.quit()

    # 解析 HTML 文件
    soup = BeautifulSoup(html_content, 'html.parser')
    results = []

    for element in soup.select('.gs-title > a.gs-title'):
        results.append({
            "html": str(element),  # 完整 HTML
            "text": element.get_text(strip=True),  # 提取链接文本
            "href": element.get('href'),  # 提取链接
            "target": element.get('target'),  # 提取目标属性
            "data-cturl": element.get('data-cturl'),  # 提取 data-cturl 属性
            "data-ctorig": element.get('data-ctorig')  # 提取 data-ctorig 属性
        })

    return jsonify({"results": results})

if __name__ == '__main__':
    app.run(debug=True, port=10804)