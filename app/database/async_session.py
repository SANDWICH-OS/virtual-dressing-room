from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import async_session


async def get_async_session() -> AsyncSession:
    """Получить асинхронную сессию БД"""
    async with async_session() as session:
        yield session
