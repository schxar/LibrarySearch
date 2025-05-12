import pymysql
import os

# 数据库配置
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '13380008373',
    'database': 'library',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

# 创建工单表
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 创建NotebookLMAudioRequests表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS NotebookLMAudioRequests (
            id INT AUTO_INCREMENT PRIMARY KEY,
            book_title VARCHAR(255) NOT NULL,
            book_hash VARCHAR(64) NOT NULL,
            request_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            clerk_user_email VARCHAR(255) NOT NULL,
            status ENUM('pending', 'processing', 'completed') DEFAULT 'pending'
        )
    ''')
    
    # 创建聊天会话表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            session_id VARCHAR(64) PRIMARY KEY,
            user_agent_hash VARCHAR(64) NOT NULL,
            title VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_user_agent (user_agent_hash)
        )
    ''')
    
    # 创建聊天消息表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id VARCHAR(64) NOT NULL,
            role ENUM('system', 'user', 'assistant') NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
            INDEX idx_session (session_id)
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()

# 登录页面HTML模板
HTML_LOGIN = """
<!-- Updated login HTML template -->
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Flask Test with Clerk</title>
    <!-- Include Bootstrap CSS for styling -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Include jQuery -->
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>

    <!-- Clerk SDK -->
    <script
        async
        crossorigin="anonymous"
        data-clerk-publishable-key="pk_test_bGFyZ2UtY3JheWZpc2gtMzIuY2xlcmsuYWNjb3VudHMuZGV2JA"
        src="https://intense-guppy-8.clerk.accounts.dev/npm/@clerk/clerk-js@latest/dist/clerk.browser.js"
        type="text/javascript"
    ></script>
</head>
<body class="container mt-5">
    <h1 class="mb-4">Flask Test with Clerk Authentication</h1>

    <!-- User Interface Placeholder -->
    <div id="app"></div>

    <!-- New Button for File Main Page (Hidden by default, shown after login) -->
    <div id="fileMainButton" class="mt-4" style="display: none;">
        <button class="btn btn-primary" onclick="window.location.href='/filemainpage'">Go to File Main Page</button>
    </div>

    <!-- Recommendation Buttons (Hidden by default, shown after login) -->
    <div id="recommendationButtons" class="mt-4" style="display: none;">
        <button class="btn btn-info me-2" onclick="window.location.href='/recommend'">Get Recommendations</button>
        <button class="btn btn-secondary" onclick="window.location.href='/view_recommendations'">View Recommendation History</button>
    </div>

    <!-- New Button for NotebookLM -->
    <div class="mt-4 text-center">
        <a href="https://schxar.picp.vip/doubao_chat" target="_blank" class="btn btn-success">Go to Chat</a>
        <a href="https://313m929k61.vicp.fun/" target="_blank" class="btn btn-info ms-2">Search Homepage</a>
        <a href="https://schxar.picp.vip/download_history" target="_blank" class="btn btn-info ms-2">Download history</a>
    </div>

    <script>
        window.addEventListener('load', async function () {
            // Initialize Clerk
            await Clerk.load();

            // Check if the user is logged in
            if (Clerk.user) {
                // Show user button
                document.getElementById('app').innerHTML = '<div id="user-button"></div>';
                Clerk.mountUserButton(document.getElementById('user-button'));

                // Show the buttons for logged-in users
                $("#fileMainButton").show();
                $("#recommendationButtons").show();

    // Set session user_email
    $.ajax({
        url: '/set_user_session',
        type: 'POST',
        data: { email: Clerk.user.emailAddresses[0].emailAddress },
        success: function(response) {
            console.log('Session set:', response);
            
            // 检查是否从搜索页面返回
            if(document.referrer.indexOf('/search') > -1) {
                // 显示已登录提示和返回按钮
                $("#app").append(`
                    <div class="alert alert-success mt-3">
                        您已成功登录，请<a href="${document.referrer}" class="alert-link">返回搜索页面</a>重试下载
                    </div>
                `);
            }
        },
        error: function(error) {
            console.error('Failed to set session:', error);
        }
    });
            } else {
                // Show sign-in button for non-logged-in users
                document.getElementById('app').innerHTML = '<div id="sign-in"></div>';
                Clerk.mountSignIn(document.getElementById('sign-in'));

                // Hide the file main page button for non-logged-in users
                $("#fileMainButton").hide();
            }
        });
    </script>
</body>
</html>
"""

def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)

def check_tables(conn):
    """检查表是否存在"""
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES LIKE 'NotebookLMAudioRequests'")
    if not cursor.fetchone():
        create_table()
    cursor.close()
