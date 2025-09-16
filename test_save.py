#!/usr/bin/env python3
"""
Тест сохранения данных в БД
"""

import sqlite3
from loguru import logger

def test_save():
    """Тест сохранения данных"""
    try:
        logger.info("🧪 Testing database save...")
        
        # Подключаемся к БД
        conn = sqlite3.connect('virtual_tryon.db')
        cursor = conn.cursor()
        
        # Тестовые данные
        test_user = {
            'telegram_id': 123456789,
            'username': 'test_user',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        # Сохраняем тестового пользователя
        cursor.execute("""
            INSERT OR IGNORE INTO users (telegram_id, username, first_name, last_name, subscription_type)
            VALUES (?, ?, ?, ?, ?)
        """, (
            test_user['telegram_id'],
            test_user['username'],
            test_user['first_name'],
            test_user['last_name'],
            'free'
        ))
        
        # Получаем ID пользователя
        cursor.execute("SELECT id FROM users WHERE telegram_id = ?", (test_user['telegram_id'],))
        user = cursor.fetchone()
        
        if user:
            user_id = user[0]
            logger.info(f"✅ Test user created/found: ID {user_id}")
            
            # Сохраняем тестовое фото
            cursor.execute("""
                INSERT INTO user_photos (user_id, photo_url, photo_type)
                VALUES (?, ?, ?)
            """, (user_id, "https://example.com/test_photo.jpg", "selfie"))
            
            conn.commit()
            logger.info("✅ Test photo saved")
            
            # Проверяем сохраненные данные
            cursor.execute("""
                SELECT u.telegram_id, u.username, p.photo_type, p.photo_url
                FROM users u
                LEFT JOIN user_photos p ON u.id = p.user_id
                WHERE u.telegram_id = ?
            """, (test_user['telegram_id'],))
            
            results = cursor.fetchall()
            logger.info(f"📊 Saved data: {results}")
            
        else:
            logger.error("❌ Failed to create/find test user")
        
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

def main():
    """Главная функция"""
    success = test_save()
    if success:
        logger.info("✅ Database save test completed!")
    else:
        logger.error("❌ Database save test failed!")

if __name__ == "__main__":
    main()
