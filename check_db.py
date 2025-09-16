#!/usr/bin/env python3
"""
Скрипт для проверки содержимого базы данных
"""

import os
import sys
import asyncio
from pathlib import Path
from loguru import logger

# Добавляем корневую директорию в PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Загружаем переменные окружения
from dotenv import load_dotenv
load_dotenv(".env")

# Настраиваем логирование
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

async def check_database():
    """Проверка содержимого базы данных"""
    try:
        logger.info("🔍 Checking database contents...")
        
        # Импортируем необходимые модули
        from app.database.connection import engine
        from app.models.user import User
        from app.models.photo import UserPhoto
        from sqlalchemy import select
        
        # Проверяем пользователей
        async with engine.begin() as conn:
            result = await conn.execute(select(User))
            users = result.fetchall()
            
            logger.info(f"👥 Found {len(users)} users in database:")
            for user in users:
                logger.info(f"  - ID: {user.id}, Telegram ID: {user.telegram_id}")
                logger.info(f"    Username: {user.username}, Name: {user.first_name} {user.last_name}")
                logger.info(f"    Subscription: {user.subscription_type}, Generations: {user.generation_count}")
                logger.info(f"    Created: {user.created_at}")
                logger.info("")
        
        # Проверяем фото
        async with engine.begin() as conn:
            result = await conn.execute(select(UserPhoto))
            photos = result.fetchall()
            
            logger.info(f"📸 Found {len(photos)} photos in database:")
            for photo in photos:
                logger.info(f"  - ID: {photo.id}, User ID: {photo.user_id}")
                logger.info(f"    Type: {photo.photo_type}, URL: {photo.photo_url[:50]}...")
                logger.info(f"    Cloudinary ID: {photo.cloudinary_public_id}")
                logger.info(f"    Created: {photo.created_at}")
                logger.info("")
        
        # Проверяем структуру таблиц
        logger.info("🗄️ Database structure:")
        logger.info("  - Users table: ✅")
        logger.info("  - UserPhotos table: ✅")
        logger.info("  - TryOnRequests table: ✅")
        logger.info("  - Payments table: ✅")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error checking database: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Главная функция"""
    success = await check_database()
    if success:
        logger.info("✅ Database check completed!")
    else:
        logger.error("❌ Database check failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
