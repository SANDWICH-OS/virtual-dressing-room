#!/usr/bin/env python3
"""
Скрипт для проверки подключения к Redis
"""

import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv("env.local")

from app.services.redis_service import redis_service
from loguru import logger

async def check_redis():
    """Проверка подключения к Redis"""
    try:
        logger.info("🔄 Checking Redis connection...")
        
        await redis_service.connect()
        
        # Тестируем базовые операции
        await redis_service.set("test_key", "test_value", expire=10)
        value = await redis_service.get("test_key")
        
        if value == "test_value":
            logger.info("✅ Redis connection successful!")
            return True
        else:
            logger.error("❌ Redis test failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Redis connection failed: {e}")
        logger.info("💡 Redis is optional for basic testing")
        return False
    finally:
        await redis_service.disconnect()

async def main():
    """Главная функция"""
    success = await check_redis()
    if success:
        logger.info("🚀 Redis is ready for bot operation")
    else:
        logger.info("⚠️ Bot will work without Redis (with limited functionality)")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

