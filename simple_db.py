#!/usr/bin/env python3
"""
Простое создание таблиц в SQLite
"""

import sqlite3
from loguru import logger

def create_tables():
    """Создание таблиц в SQLite"""
    try:
        logger.info("🗄️ Creating database tables...")
        
        # Подключаемся к базе данных
        conn = sqlite3.connect('virtual_tryon.db')
        cursor = conn.cursor()
        
        # Создаем таблицу users
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER UNIQUE NOT NULL,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                subscription_type TEXT DEFAULT 'free',
                generation_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Создаем таблицу user_photos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_photos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                photo_url TEXT NOT NULL,
                photo_type TEXT NOT NULL,
                cloudinary_public_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Создаем таблицу tryon_requests
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tryon_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                user_photo_id INTEGER NOT NULL,
                clothing_photo_id INTEGER NOT NULL,
                result_photo_url TEXT,
                status TEXT DEFAULT 'pending',
                error_message TEXT,
                ai_model_used TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id),
                FOREIGN KEY (user_photo_id) REFERENCES user_photos (id),
                FOREIGN KEY (clothing_photo_id) REFERENCES user_photos (id)
            )
        ''')
        
        # Создаем таблицу payments
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                currency TEXT DEFAULT 'RUB',
                status TEXT DEFAULT 'pending',
                payment_type TEXT NOT NULL,
                yoomoney_payment_id TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # Сохраняем изменения
        conn.commit()
        
        # Проверяем созданные таблицы
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        logger.info(f"✅ Tables created successfully!")
        logger.info(f"📋 Created tables: {[table[0] for table in tables]}")
        
        # Закрываем соединение
        conn.close()
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        return False

def main():
    """Главная функция"""
    success = create_tables()
    if success:
        logger.info("✅ Database setup completed!")
    else:
        logger.error("❌ Database setup failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
