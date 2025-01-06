from flask import Flask, request, jsonify, send_file, render_template_string
import os
import glob

app = Flask(__name__)

# 自定义下载目录
download_directory = os.path.join(os.getcwd(), "C:\\Users\\PC\\eclipse-workspace\\LibrarySearch\\src\\main\\resources\\static\\books")
if not os.path.exists(download_directory):
    os.makedirs(download_directory)

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

    <h2>Search Books by Keyword</h2>
    <form method="GET" action="/search">
        <label for="bookName">Book Name Keyword:</label>
        <input type="text" id="bookName" name="book_name" required>
        <button type="submit">Search</button>
    </form>

    <h2>List Downloaded Files</h2>
    <ul>
        {% for file in files %}
        <li><a href="/download/{{ file }}" target="_blank">{{ file }}</a></li>
        {% endfor %}
    </ul>
</body>
</html>
"""

@app.route('/')
def index():
    files = os.listdir(download_directory)
    return render_template_string(HTML_TEMPLATE, files=files)

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
        return jsonify({"files": [os.path.basename(f) for f in matching_files]}), 200
    else:
        return jsonify({"message": "No matching files found"}), 200

# 列出下载目录中的文件
@app.route('/list', methods=['GET'])
def list_files():
    files = os.listdir(download_directory)
    if files:
        return jsonify({"files": files}), 200
    else:
        return jsonify({"message": "No files found in the download directory"}), 200

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
