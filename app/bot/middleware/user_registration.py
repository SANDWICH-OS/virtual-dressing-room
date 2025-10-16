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
        
        try:
            # Получаем сессию БД
            async with get_async_session() as session:
                # Проверяем, зарегистрирован ли пользователь
                user = await self.get_or_create_user(session, event.from_user)
                
                # Добавляем пользователя в данные для обработчиков
                data["user"] = user
        except Exception as e:
            logger.error(f"❌ Database error in user registration middleware: {e}")
            # Создаем фиктивного пользователя для продолжения работы
            from app.models.user import User
            user = User(
                telegram_id=event.from_user.id,
                username=event.from_user.username,
                first_name=event.from_user.first_name,
                last_name=event.from_user.last_name
            )
            data["user"] = user
            logger.warning("⚠️ Using fallback user object without database")
        
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
            
            # Обновляем данные в Redis
            await self.save_user_to_redis(telegram_user.id, user)
            
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
        
        # Сохраняем/обновляем базовые данные в Redis
        await self.save_user_to_redis(telegram_user.id, user)
        
        return user
    
    async def save_user_to_redis(self, telegram_user_id: int, user: User):
        """Сохранить данные пользователя в Redis (НЕ перезаписывая существующие)"""
        try:
            from app.services.redis_service import redis_service
            
            # Получаем существующие данные из Redis
            existing_data = await redis_service.get_user_data(telegram_user_id) or {}
            logger.info(f"Existing Redis data for user {telegram_user_id}: {existing_data}")
            
            # Обновляем только базовые поля, сохраняя URL фото и другие данные
            updated_data = {
                "telegram_id": user.telegram_id,
                "username": user.username,
                "first_name": user.first_name,
                "subscription_type": user.subscription_type.value if user.subscription_type else "free",
            }
            
            # Объединяем существующие данные с новыми (существующие имеют приоритет)
            final_data = {**updated_data, **existing_data}
            logger.info(f"Final Redis data for user {telegram_user_id}: {final_data}")
            
            await redis_service.set_user_data(telegram_user_id, final_data)
            logger.info(f"User {telegram_user_id} data updated in Redis (preserving existing data)")
        except Exception as e:
            logger.error(f"Failed to save user {telegram_user_id} to Redis: {e}")
            # Не прерываем работу, если Redis недоступен
