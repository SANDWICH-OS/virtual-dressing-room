from sqlalchemy.ext.asyncio import AsyncSession
from app.database.connection import async_session


def get_async_session():
    """Получить асинхронную сессию БД как context manager"""
    return async_session()
