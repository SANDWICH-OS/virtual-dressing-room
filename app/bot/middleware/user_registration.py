from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable, Union
from app.database.async_session import get_async_session
from app.models.user import User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger


class UserRegistrationMiddleware(BaseMiddleware):
    """Middleware для автоматической регистрации пользователей"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Union[Message, CallbackQuery],
        data: Dict[str, Any]
    ) -> Any:
        """Обработка события с проверкой регистрации пользователя"""
        
        user_id = event.from_user.id
        
        # Получаем сессию БД
        async with get_async_session() as session:
            # Проверяем, зарегистрирован ли пользователь
            user = await self.get_or_create_user(session, event.from_user)
            
            # Добавляем пользователя в данные для обработчиков
            data["user"] = user
        
        # Выполняем обработчик
        return await handler(event, data)
    
    async def get_or_create_user(
        self, 
        session: AsyncSession, 
        telegram_user
    ) -> User:
        """Получить или создать пользователя"""
        
        # Ищем пользователя в БД
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_user.id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            # Пользователь найден, обновляем данные
            user.username = telegram_user.username
            user.first_name = telegram_user.first_name
            user.last_name = telegram_user.last_name
            await session.commit()
            logger.info(f"User {telegram_user.id} updated in database")
            return user
        
        # Создаем нового пользователя
        user = User(
            telegram_id=telegram_user.id,
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name
        )
        
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        logger.info(f"New user {telegram_user.id} registered in database")
        return user
