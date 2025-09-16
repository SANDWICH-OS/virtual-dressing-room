from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.config import settings
from app.services.redis_service import redis_service
from app.bot.middleware import LoggingMiddleware, UserRegistrationMiddleware
from app.bot.handlers import register_handlers
from loguru import logger


async def create_bot():
    """Создание и настройка бота"""
    # Подключаемся к Redis
    await redis_service.connect()
    
    # Создаем бота
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    
    # Создаем диспетчер с Redis storage
    storage = RedisStorage.from_url(settings.redis_url)
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
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        raise
    finally:
        await bot.session.close()
        await redis_service.disconnect()
