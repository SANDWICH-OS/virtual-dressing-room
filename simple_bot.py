#!/usr/bin/env python3
"""
Упрощенная версия бота для тестирования с Python 3.9
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

async def simple_bot():
    """Упрощенный бот для тестирования"""
    try:
        logger.info("🚀 Starting Simple Virtual Try-On Bot...")
        
        # Проверяем токен
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token or bot_token == "your_telegram_bot_token_here":
            logger.error("❌ BOT_TOKEN not set!")
            return False
        
        logger.info(f"✅ BOT_TOKEN found: {bot_token[:10]}...")
        
        # Импортируем aiogram напрямую
        from aiogram import Bot, Dispatcher
        from aiogram.types import Message
        from aiogram.filters import Command
        from aiogram.enums import ParseMode
        
        # Создаем бота
        bot = Bot(token=bot_token, parse_mode=ParseMode.HTML)
        dp = Dispatcher()
        
        # Простой обработчик команды /start
        @dp.message(Command("start"))
        async def start_handler(message: Message):
            await message.answer(
                "👋 <b>Добро пожаловать в Virtual Try-On Bot!</b>\n\n"
                "Я помогу тебе примерить одежду виртуально с помощью ИИ.\n\n"
                "🎯 <b>Что я умею:</b>\n"
                "• Создавать твой виртуальный профиль\n"
                "• Генерировать фото в новой одежде\n"
                "• Сохранять результаты примерки\n\n"
                "🚀 <b>Начнем?</b>\n"
                "Отправь мне свое фото для создания профиля!"
            )
            logger.info(f"User {message.from_user.id} started bot")
        
        # Простой обработчик команды /help
        @dp.message(Command("help"))
        async def help_handler(message: Message):
            await message.answer(
                "❓ <b>Помощь по использованию бота</b>\n\n"
                "🎯 <b>Основные команды:</b>\n"
                "/start - Начать работу с ботом\n"
                "/help - Показать эту справку\n\n"
                "📸 <b>Как создать try-on:</b>\n"
                "1. Загрузи свое селфи\n"
                "2. Загрузи фото в полный рост\n"
                "3. Загрузи фото одежды\n"
                "4. Получи результат!\n\n"
                "💡 <b>Советы для лучшего результата:</b>\n"
                "• Используй качественные фото\n"
                "• Селфи делай анфас с хорошим освещением\n"
                "• Фото в полный рост - в нейтральной позе\n"
                "• Одежду фотографируй на белом фоне"
            )
            logger.info(f"User {message.from_user.id} requested help")
        
        # Простой обработчик фото
        @dp.message(lambda m: m.photo is not None)
        async def photo_handler(message: Message):
            await message.answer(
                "📸 <b>Фото получено!</b>\n\n"
                "Спасибо за фото! В полной версии бота здесь будет:\n"
                "• Валидация качества фото\n"
                "• Загрузка в Cloudinary\n"
                "• Сохранение в базу данных\n"
                "• AI генерация try-on\n\n"
                "Пока что это демо-версия! 🎭"
            )
            logger.info(f"User {message.from_user.id} sent photo")
        
        # Обработчик всех остальных сообщений
        @dp.message()
        async def echo_handler(message: Message):
            await message.answer(
                "🤖 <b>Бот работает!</b>\n\n"
                "Используй команды:\n"
                "/start - Начать работу\n"
                "/help - Помощь\n\n"
                "Или отправь фото для тестирования!"
            )
            logger.info(f"User {message.from_user.id} sent: {message.text}")
        
        logger.info("✅ Bot handlers registered")
        logger.info("🚀 Starting bot polling...")
        
        # Запускаем бота
        await dp.start_polling(bot)
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if 'bot' in locals():
            await bot.session.close()
    
    return True

async def main():
    """Главная функция"""
    success = await simple_bot()
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
