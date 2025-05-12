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

def get_db_connection():
    """获取数据库连接"""
    return pymysql.connect(**DB_CONFIG)

def create_table():
    """创建数据库表"""
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

def check_tables(conn):
    """检查表是否存在"""
    cursor = conn.cursor()
    cursor.execute("SHOW TABLES LIKE 'NotebookLMAudioRequests'")
    if not cursor.fetchone():
        create_table()
    cursor.close()
