from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.enums import ParseMode
import os
from app.config import settings
from app.services.redis_service import redis_service
from app.bot.middleware import LoggingMiddleware, UserRegistrationMiddleware
from app.bot.handlers import register_handlers
from app.database.base import Base
from app.database.connection import engine
from loguru import logger

# Определяем, какая конфигурация использовать
def get_settings():
    """Получить настройки в зависимости от окружения"""
    if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_PROJECT_ID"):
        # В Railway используем production конфигурацию
        from app import config_prod
        return config_prod.settings
    else:
        # Локально используем обычную конфигурацию
        return settings


async def init_database():
    """Инициализация базы данных - создание таблиц"""
    try:
        # Создаем все таблицы
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("✅ Database tables created successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        logger.warning("⚠️ Bot will continue without database functionality")


async def create_bot():
    """Создание и настройка бота"""
    # Получаем настройки в зависимости от окружения
    current_settings = get_settings()
    
    # Инициализируем базу данных
    await init_database()
    
    # Получаем Redis URL из переменных окружения для Railway
    redis_url = os.getenv("REDIS_URL", current_settings.redis_url)
    
    # Проверяем, есть ли Redis URL и не localhost ли это
    if not redis_url or "localhost" in redis_url or "127.0.0.1" in redis_url:
        logger.warning("⚠️ Redis URL not configured or points to localhost, using MemoryStorage")
        from aiogram.fsm.storage.memory import MemoryStorage
        storage = MemoryStorage()
    else:
        # Пытаемся подключиться к Redis
        try:
            await redis_service.connect()
            logger.info(f"✅ Connected to Redis: {redis_url}")
            storage = RedisStorage.from_url(redis_url)
        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            # В случае ошибки Redis, используем MemoryStorage как fallback
            from aiogram.fsm.storage.memory import MemoryStorage
            storage = MemoryStorage()
            logger.warning("⚠️ Using MemoryStorage as fallback")
    
    # Создаем бота
    bot = Bot(
        token=current_settings.bot_token,
        parse_mode=ParseMode.HTML
    )
    
    # Создаем диспетчер
    dp = Dispatcher(storage=storage)
    
    # Добавляем middleware
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())
    dp.message.middleware(UserRegistrationMiddleware())
    dp.callback_query.middleware(UserRegistrationMiddleware())
    
    # Регистрируем обработчики
    register_handlers(dp)
    
    logger.info("Bot created successfully with all handlers and middleware")
    return bot, dp


# Создаем экземпляры бота и диспетчера
bot, dp = None, None


async def get_bot():
    """Получить экземпляр бота"""
    global bot, dp
    if bot is None or dp is None:
        bot, dp = await create_bot()
    return bot, dp


async def start_bot():
    """Запуск бота"""
    bot, dp = await get_bot()
    
    try:
        logger.info("Starting bot...")
        
        # Обработка конфликта Telegram API
        try:
            await dp.start_polling(bot)
        except Exception as telegram_error:
            if "Conflict: terminated by other getUpdates request" in str(telegram_error):
                logger.error("❌ Telegram API Conflict: Another bot instance is running")
                logger.info("🔄 Waiting 5 seconds before retry...")
                import asyncio
                await asyncio.sleep(5)
                logger.info("🔄 Retrying bot start...")
                await dp.start_polling(bot)
            else:
                raise telegram_error
                
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise
    finally:
        await bot.session.close()
        await redis_service.disconnect()