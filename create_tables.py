#!/usr/bin/env python3
"""
Скрипт для создания таблиц в базе данных
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

# Импортируем все модели
from app.models.user import User
from app.models.photo import UserPhoto
from app.models.tryon import TryOnRequest
from app.models.payment import Payment

# Настраиваем логирование
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

async def create_tables():
    """Создание таблиц в базе данных"""
    try:
        logger.info("🗄️ Creating database tables...")
        
        # Импортируем необходимые модули
        from app.database.connection import engine, Base
        
        # Создаем все таблицы
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ Tables created successfully!")
        
        # Проверяем, что таблицы созданы
        async with engine.begin() as conn:
            result = await conn.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = result.fetchall()
            
            logger.info(f"📋 Created tables: {[table[0] for table in tables]}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error creating tables: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Главная функция"""
    success = await create_tables()
    if success:
        logger.info("✅ Database setup completed!")
    else:
        logger.error("❌ Database setup failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())