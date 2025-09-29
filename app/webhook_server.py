"""
FastAPI сервер для обработки webhook'ов от Fashn AI
"""

import os
import sys
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

if __name__ == "__main__":
    import uvicorn
    
    # Получаем настройки
    if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_PROJECT_ID"):
        from app import config_prod
        settings = config_prod.settings
    else:
        from app.config import settings
    
    # Запускаем сервер
    uvicorn.run(
        "app.webhook_server:app",
        host=settings.host,
        port=settings.port + 1,  # Используем другой порт для webhook сервера
        reload=settings.debug,
        log_level="info"
    )
