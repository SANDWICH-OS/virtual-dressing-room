from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database.connection import engine, Base
from app.services.redis_service import redis_service
from app.config import settings
import asyncio


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    print("🚀 Starting Virtual Try-On Bot...")
    
    # Подключение к Redis
    await redis_service.connect()
    print("✅ Redis connected")
    
    # Создание таблиц БД (для разработки)
    if settings.debug:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Database tables created")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")
    await redis_service.disconnect()
    print("✅ Redis disconnected")


app = FastAPI(
    title="Virtual Try-On Telegram Bot",
    description="API для телеграм бота виртуальной примерки одежды",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    return {"message": "Virtual Try-On Bot API", "status": "running"}


@app.get("/health")
async def health_check():
    """Проверка здоровья сервиса"""
    return {
        "status": "healthy",
        "redis": "connected" if redis_service.redis else "disconnected",
        "debug": settings.debug
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
