from flask import Flask, request, jsonify, send_from_directory
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os
import requests

app = Flask(__name__)

# 自定义下载目录
download_directory = os.path.join(os.getcwd(), "download")
if not os.path.exists(download_directory):
    os.makedirs(download_directory)

# 设置 ChromeDriver 配置
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

@app.route('/download', methods=['POST'])
def download_book():
    data = request.json
    if 'bookUrl' not in data:
        return jsonify({"error": "bookUrl is required"}), 400

    book_url = data['bookUrl']
    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.get(book_url)

        # 下载链接选择器
        download_link_element = driver.find_element(By.CSS_SELECTOR, "a.btn.btn-default.addDownloadedBook")
        download_link = download_link_element.get_attribute("href")
        file_extension = download_link_element.find_element(By.CLASS_NAME, "book-property__extension").text
        file_size = download_link_element.text.split('(')[-1].replace(')', '').strip()

        if download_link:
            # 文件名使用书籍 ID 生成
            book_id = download_link.split('/')[-2]
            file_name = f"book_{book_id}.{file_extension}"
            file_path = os.path.join(download_directory, file_name)

            # 下载文件
            response = requests.get(download_link, stream=True)
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        f.write(chunk)

                # 返回可访问的文件路径
                public_url = f"http://127.0.0.1:10805/download/{file_name}"
                return jsonify({
                    "message": "Download successful",
                    "file_url": public_url,
                    "file_size": file_size
                }), 200
            else:
                return jsonify({"error": "Failed to download the file"}), 500

        return jsonify({"error": "Download link not found"}), 404

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        driver.quit()

# 自定义下载目录路由
@app.route('/download/<filename>', methods=['GET'])
def serve_file(filename):
    return send_from_directory(download_directory, filename)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10805)
