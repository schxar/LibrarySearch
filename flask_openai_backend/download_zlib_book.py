from flask import Flask, request, jsonify, send_file, render_template_string
import os
import glob
from math import ceil

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
    <!-- Bootstrap CSS -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {
            background-color: #f8f9fa;
            padding: 20px;
        }
        .card {
            margin-bottom: 20px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        .card-header {
            background-color: #007bff;
            color: white;
        }
        .list-group-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .pagination {
            margin-top: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="text-center mb-4">Book Downloader</h1>

        <!-- Search Section -->
        <div class="card">
            <div class="card-header">
                <h2 class="card-title mb-0">Search Books by Keyword</h2>
            </div>
            <div class="card-body">
                <form method="GET" action="/search" class="d-flex">
                    <input type="text" id="bookName" name="book_name" class="form-control me-2" placeholder="Enter book name keyword" required>
                    <button type="submit" class="btn btn-primary">Search</button>
                </form>
            </div>
        </div>

        <!-- List Downloaded Files -->
        <div class="card">
            <div class="card-header">
                <h2 class="card-title mb-0">List Downloaded Files</h2>
            </div>
            <div class="card-body">
                <ul class="list-group">
                    {% for file in files %}
                    <li class="list-group-item">
                        <span>{{ file }}</span>
                        <a href="/download/{{ file }}" class="btn btn-success btn-sm" target="_blank">Download</a>
                    </li>
                    {% endfor %}
                </ul>

                <!-- Pagination -->
                <nav class="pagination justify-content-center">
                    <ul class="pagination">
                        {% if page > 1 %}
                        <li class="page-item">
                            <a class="page-link" href="/?page={{ page - 1 }}&per_page={{ per_page }}">Previous</a>
                        </li>
                        {% endif %}
                        <li class="page-item active">
                            <span class="page-link">Page {{ page }} of {{ total_pages }}</span>
                        </li>
                        {% if page < total_pages %}
                        <li class="page-item">
                            <a class="page-link" href="/?page={{ page + 1 }}&per_page={{ per_page }}">Next</a>
                        </li>
                        {% endif %}
                    </ul>
                </nav>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

@app.route('/')
def index():
    # 获取分页参数
    page = int(request.args.get('page', 1))  # 默认第1页
    per_page = int(request.args.get('per_page', 10))  # 默认每页10条

    # 获取所有文件
    files = os.listdir(download_directory)
    total_files = len(files)
    total_pages = ceil(total_files / per_page)

    # 分页逻辑
    start = (page - 1) * per_page
    end = start + per_page
    paginated_files = files[start:end]

    return render_template_string(
        HTML_TEMPLATE,
        files=paginated_files,
        page=page,
        per_page=per_page,
        total_pages=total_pages
    )

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
