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

# Используем production конфигурацию для Railway
import sys
sys.path.insert(0, str(project_root))
from app import config_prod

# Настраиваем логирование для production
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

async def main():
    """Главная функция запуска бота с webhook сервером"""
    try:
        logger.info("🚀 Starting Virtual Try-On Bot with Webhook Server (Railway Production) - v4...")
        
        # Логируем переменные окружения для отладки
        logger.info(f"BOT_TOKEN: {'✅ Set' if os.getenv('BOT_TOKEN') else '❌ Missing'}")
        logger.info(f"REDIS_URL: {os.getenv('REDIS_URL', 'Not set')}")
        logger.info(f"DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set')}")
        logger.info(f"RAILWAY_ENVIRONMENT: {os.getenv('RAILWAY_ENVIRONMENT', 'Not set')}")
        logger.info(f"FASHN_API_KEY: {'✅ Set' if os.getenv('FASHN_API_KEY') else '❌ Missing'}")
        logger.info(f"FASHN_WEBHOOK_URL: {os.getenv('FASHN_WEBHOOK_URL', 'Not set')}")
        
        # Импортируем FastAPI и webhook handlers
        from fastapi import FastAPI
        from app.bot.webhook_handlers import setup_webhook_routes
        import uvicorn
        
        # Создаем FastAPI приложение
        app = FastAPI(title="Virtual Try-On Bot with Webhooks")
        setup_webhook_routes(app)
        
        @app.get("/")
        async def root():
            return {"message": "Virtual Try-On Bot with Webhooks", "status": "running"}
        
        @app.get("/health")
        async def health():
            return {"status": "healthy", "service": "bot_with_webhooks"}
        
        # Запускаем Telegram бот в фоне
        async def start_bot_background():
            try:
                from app.bot.bot import start_bot
                logger.info("🤖 Starting Telegram bot in background...")
                await start_bot()
            except Exception as e:
                logger.error(f"❌ Error starting Telegram bot: {e}")
        
        # Запускаем бот в фоне
        asyncio.create_task(start_bot_background())
        
        # Запускаем webhook сервер
        port = int(os.getenv("PORT", 8080))
        logger.info(f"🚀 Starting webhook server on port {port}")
        
        config = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=port,
            log_level="info"
        )
        server = uvicorn.Server(config)
        await server.serve()
        
    except Exception as e:
        logger.error(f"❌ Error starting bot with webhooks: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
