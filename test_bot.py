#!/usr/bin/env python3
"""
Простой тест бота без сложных зависимостей
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

async def test_bot():
    """Простой тест бота"""
    try:
        logger.info("🚀 Testing Virtual Try-On Bot...")
        
        # Проверяем наличие BOT_TOKEN
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token or bot_token == "your_telegram_bot_token_here":
            logger.error("❌ BOT_TOKEN not set!")
            return False
        
        logger.info(f"✅ BOT_TOKEN found: {bot_token[:10]}...")
        
        # Проверяем базу данных
        db_file = Path("virtual_tryon.db")
        if db_file.exists():
            logger.info("✅ Database file exists")
        else:
            logger.error("❌ Database file not found")
            return False
        
        # Проверяем конфигурацию
        from app.config import settings
        logger.info(f"✅ Database URL: {settings.database_url}")
        logger.info(f"✅ Redis URL: {settings.redis_url}")
        logger.info(f"✅ Debug mode: {settings.debug}")
        
        logger.info("🎉 Basic bot configuration is working!")
        logger.info("")
        logger.info("📋 Next steps:")
        logger.info("1. Get real bot token from @BotFather")
        logger.info("2. Update BOT_TOKEN in .env file")
        logger.info("3. Test with real bot")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

async def main():
    """Главная функция"""
    success = await test_bot()
    if success:
        logger.info("✅ Bot test completed successfully!")
    else:
        logger.error("❌ Bot test failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
