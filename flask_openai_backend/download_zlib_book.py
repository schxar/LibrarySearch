from flask import Flask, request, jsonify, send_from_directory, render_template_string
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os
import requests
import glob

app = Flask(__name__)

# 自定义下载目录
download_directory = os.path.join(os.getcwd(), "download")
if not os.path.exists(download_directory):
    os.makedirs(download_directory)

# 设置 ChromeDriver 配置
chrome_options = Options()
#chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 首页HTML模板
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Book Downloader</title>
</head>
<body>
    <h1>Book Downloader</h1>
    <form method="POST" action="/download">
        <label for="bookUrl">Book URL:</label>
        <input type="text" id="bookUrl" name="bookUrl" required>
        <button type="submit">Download</button>
    </form>

    <h2>Check if Book Exists</h2>
    <form method="GET" action="/check">
        <label for="bookId">Book ID:</label>
        <input type="text" id="bookId" name="book_id" required>
        <button type="submit">Check</button>
    </form>

    <h2>List Downloaded Files</h2>
    <form method="GET" action="/list">
        <button type="submit">List Files</button>
    </form>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/download', methods=['POST'])
def download_book():
    book_url = request.form.get('bookUrl')
    if not book_url:
        return jsonify({"error": "bookUrl is required"}), 400

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(book_url)

        # 提取初始下载链接
        download_link_element = driver.find_element(By.CSS_SELECTOR, "a.btn.btn-default.addDownloadedBook")
        initial_download_link = download_link_element.get_attribute("href")

        # 从 Selenium 会话中获取 cookies
        selenium_cookies = driver.get_cookies()
        cookies = {cookie['name']: cookie['value'] for cookie in selenium_cookies}

        # 获取最终的重定向下载链接
        session = requests.Session()
        for name, value in cookies.items():
            session.cookies.set(name, value)

        # 设置必要的 headers，模拟浏览器行为
        session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
        })

        # 通过 requests 获取最终重定向的下载链接
        response = session.head(initial_download_link, allow_redirects=True, timeout=30)
        if response.status_code != 200:
            return jsonify({"error": "Failed to resolve final download link"}), 500
        final_download_link = response.url

        # 下载文件
        file_extension = "pdf"  # 假设文件为 PDF
        book_id = initial_download_link.split('/')[-2]
        file_name = f"book_{book_id}.{file_extension}"
        file_path = os.path.join(download_directory, file_name)

        # 下载文件内容
        download_response = session.get(final_download_link, stream=True, timeout=60)
        download_response.raise_for_status()

        # 检查内容类型
        content_type = download_response.headers.get("Content-Type", "")
        if "application" not in content_type:
            return jsonify({"error": f"Invalid file type: {content_type}"}), 400

        # 写入文件
        with open(file_path, 'wb') as f:
            for chunk in download_response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        # 检查文件大小（可选）
        actual_file_size = os.path.getsize(file_path) / (1024 * 1024)
        if actual_file_size < 0.1:  # 设置最小大小检查，避免下载无效文件
            os.remove(file_path)
            return jsonify({"error": "Downloaded file size is too small, download failed."}), 400

        # 返回下载文件信息
        public_url = f"http://127.0.0.1:10805/download/{file_name}"
        return jsonify({
            "message": "Download successful",
            "file_url": public_url,
            "file_size": f"{actual_file_size:.2f} MB"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        driver.quit()   



# 检查文件是否存在
@app.route('/check', methods=['GET'])
def check_book():
    book_id = request.args.get('book_id')
    if not book_id:
        return jsonify({"error": "book_id is required"}), 400

    # 使用 glob 模糊匹配文件名
    pattern = os.path.join(download_directory, f"book_{book_id}.*")
    matching_files = glob.glob(pattern)

    if matching_files:
        return jsonify({"exists": 1, "files": [os.path.basename(f) for f in matching_files]}), 200
    else:
        return jsonify({"exists": 0}), 200

# 列出下载目录中的文件
@app.route('/list', methods=['GET'])
def list_files():
    files = os.listdir(download_directory)
    if files:
        return jsonify({"files": files}), 200
    else:
        return jsonify({"message": "No files found in the download directory"}), 200

from flask import send_file
# 自定义下载目录路由
@app.route('/download/<filename>', methods=['GET'])
def serve_file(filename):
    file_path = os.path.join(download_directory, filename)
    if os.path.exists(file_path):
        return send_file(
            file_path,
            as_attachment=True,  # 强制浏览器下载
            download_name=filename  # 下载时的文件名
        )
    else:
        return jsonify({"error": "File not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10805)
