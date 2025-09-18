#!/usr/bin/env python3
"""
Railway production bot - новая структура с Фазой 4.1
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
load_dotenv()

# Настраиваем логирование для production
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

async def main():
    """Главная функция запуска бота"""
    try:
        logger.info("🚀 Starting Virtual Try-On Bot (Railway Production)...")
        
        # Импортируем и создаем бота
        from app.bot.bot import create_bot, start_bot
        
        # Создаем бота
        bot, dp = await create_bot()
        logger.info("✅ Bot created successfully!")
        
        # Запускаем бота
        await start_bot()
        
    except Exception as e:
        logger.error(f"❌ Error starting bot: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
