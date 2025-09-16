#!/usr/bin/env python3
"""
Скрипт для запуска телеграм бота
"""

import asyncio
import sys
from loguru import logger
from app.bot.bot import start_bot


async def main():
    """Главная функция запуска бота"""
    try:
        logger.info("🚀 Starting Virtual Try-On Bot...")
        await start_bot()
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
