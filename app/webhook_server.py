"""
FastAPI сервер для обработки webhook'ов от Fashn AI
"""

import os
import sys
import asyncio
from pathlib import Path
from fastapi import FastAPI
from loguru import logger

# Добавляем корневую директорию в PYTHONPATH
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Загружаем переменные окружения
from dotenv import load_dotenv
load_dotenv()

# Импортируем webhook handlers
from app.bot.webhook_handlers import setup_webhook_routes

# Импортируем Telegram бот
from app.bot.bot import start_bot

# Создаем FastAPI приложение
app = FastAPI(
    title="Virtual Try-On Bot Webhooks",
    description="Webhook server for Fashn AI integration",
    version="1.0.0"
)

# Настраиваем маршруты для webhook'ов
setup_webhook_routes(app)

@app.get("/")
async def root():
    """Главная страница"""
    return {
        "message": "Virtual Try-On Bot Webhook Server",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "webhook_server"
    }

async def startup():
    """Запуск Telegram бота в фоне"""
    try:
        logger.info("🤖 Starting Telegram bot in background...")
        await start_bot()
    except Exception as e:
        logger.error(f"❌ Error starting Telegram bot: {e}")

@app.on_event("startup")
async def startup_event():
    """Запускаем Telegram бот при старте FastAPI"""
    asyncio.create_task(startup())

if __name__ == "__main__":
    import uvicorn
    
    # Получаем настройки
    if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_PROJECT_ID"):
        from app import config_prod
        settings = config_prod.settings
    else:
        from app.config import settings
    
    # Запускаем сервер
    # В Railway используем порт из переменной окружения или стандартный 8080
    port = int(os.getenv("PORT", 8080))
    
    logger.info(f"🚀 Starting webhook server on port {port}")
    
    uvicorn.run(
        "app.webhook_server:app",
        host="0.0.0.0",
        port=port,
        reload=settings.debug,
        log_level="info"
    )
