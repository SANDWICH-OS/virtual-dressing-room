#!/usr/bin/env python3
"""
Функция для очистки данных пользователя
"""

import os
import sys
from pathlib import Path
from loguru import logger

# Добавляем корневую директорию в PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Загружаем переменные окружения
from dotenv import load_dotenv
load_dotenv()

def get_db_connection():
    """Получить соединение с БД"""
    db_url = os.getenv("DATABASE_URL", "sqlite:///./virtual_tryon.db")
    
    if db_url.startswith("postgres://") or db_url.startswith("postgresql://"):
        # PostgreSQL для production
        import psycopg2
        import urllib.parse as urlparse
        
        url = urlparse.urlparse(db_url)
        conn = psycopg2.connect(
            database=url.path[1:],
            user=url.username,
            password=url.password,
            host=url.hostname,
            port=url.port
        )
        return conn
    else:
        # SQLite для development
        return sqlite3.connect('virtual_tryon.db')

def clear_user_data(telegram_id):
    """Очистить все данные пользователя"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Находим пользователя
        if os.getenv("DATABASE_URL", "").startswith("postgres"):
            cursor.execute("SELECT id FROM users WHERE telegram_id = %s", (telegram_id,))
        else:
            cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (telegram_id,))
        user = cursor.fetchone()
        
        if not user:
            logger.warning(f"❌ User {telegram_id} not found")
            return False
        
        user_id = user[0]
        
        # Удаляем фото пользователя
        if os.getenv("DATABASE_URL", "").startswith("postgres"):
            cursor.execute("DELETE FROM user_photos WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM tryon_requests WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM payments WHERE user_id = %s", (user_id,))
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        else:
            cursor.execute("DELETE FROM user_photos WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM tryon_requests WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM payments WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        
        conn.commit()
        logger.info(f"✅ Cleared all data for user {telegram_id} (ID: {user_id})")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error clearing user data: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def main():
    """Тест функции очистки"""
    telegram_id = int(input("Enter Telegram ID to clear: "))
    success = clear_user_data(telegram_id)
    if success:
        print("✅ User data cleared successfully!")
    else:
        print("❌ Failed to clear user data!")

if __name__ == "__main__":
    main()
