
import pymysql
from datetime import datetime
import hashlib

def apply_migration(conn):
    cursor = conn.cursor()
    
    # 创建聊天会话表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_sessions (
            session_id VARCHAR(64) PRIMARY KEY,
            user_agent_hash VARCHAR(64) NOT NULL,
            title VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_user_agent (user_agent_hash)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    ''')
    
    # 创建聊天消息表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_messages (
            message_id BIGINT AUTO_INCREMENT PRIMARY KEY,
            session_id VARCHAR(64) NOT NULL,
            role ENUM('user', 'assistant', 'system') NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES chat_sessions(session_id) ON DELETE CASCADE,
            INDEX idx_session (session_id)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
    ''')
    
    conn.commit()

if __name__ == '__main__':
    # 本地测试用配置
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'root',
        'password': '13380008373',
        'database': 'library',
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }
    
    conn = pymysql.connect(**DB_CONFIG)
    try:
        apply_migration(conn)
        print("Migration applied successfully")
    finally:
        conn.close()
