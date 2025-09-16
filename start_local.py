#!/usr/bin/env python3
"""
Скрипт для быстрого запуска бота в локальном режиме
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
load_dotenv(".env")  # Загружаем .env файл

# Настраиваем логирование
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

async def main():
    """Главная функция запуска"""
    try:
        logger.info("🚀 Starting Virtual Try-On Bot (Local Mode)...")
        
        # Проверяем наличие BOT_TOKEN
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token or bot_token == "your_telegram_bot_token_here":
            logger.error("❌ BOT_TOKEN not set! Please:")
            logger.error("1. Get bot token from @BotFather")
            logger.error("2. Update BOT_TOKEN in .env file")
            return
        
        # Импортируем и запускаем бота
        from app.bot.bot import start_bot
        await start_bot()
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())