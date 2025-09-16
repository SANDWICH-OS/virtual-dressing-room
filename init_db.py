#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных
"""

import os
import sys
import asyncio
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Загружаем переменные окружения
from dotenv import load_dotenv
load_dotenv("env.local")

from app.database.connection import engine, Base
from app.models import *  # Импортируем все модели
from loguru import logger

async def init_database():
    """Инициализация базы данных"""
    try:
        logger.info("🗄️ Initializing database...")
        
        # Создаем все таблицы
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ Database initialized successfully!")
        logger.info(f"📁 Database file: {os.path.abspath('virtual_tryon.db')}")
        
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        raise

async def main():
    """Главная функция"""
    try:
        await init_database()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

