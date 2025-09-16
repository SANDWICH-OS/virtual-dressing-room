from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from loguru import logger
from typing import Callable, Dict, Any, Awaitable


class LoggingMiddleware(BaseMiddleware):
    """Middleware для логирования действий пользователей"""
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        """Обработка события с логированием"""
        
        user_id = event.from_user.id
        username = event.from_user.username or "Unknown"
        first_name = event.from_user.first_name or "Unknown"
        
        if isinstance(event, Message):
            # Логируем сообщения
            if event.text:
                logger.info(
                    f"User {user_id} ({username}, {first_name}) sent message: {event.text[:100]}"
                )
            elif event.photo:
                logger.info(
                    f"User {user_id} ({username}, {first_name}) sent photo"
                )
            elif event.document:
                logger.info(
                    f"User {user_id} ({username}, {first_name}) sent document: {event.document.file_name}"
                )
            else:
                logger.info(
                    f"User {user_id} ({username}, {first_name}) sent {event.content_type}"
                )
        
        elif isinstance(event, CallbackQuery):
            # Логируем нажатия кнопок
            logger.info(
                f"User {user_id} ({username}, {first_name}) pressed button: {event.data}"
            )
        
        try:
            # Выполняем обработчик
            result = await handler(event, data)
            logger.debug(f"Handler completed successfully for user {user_id}")
            return result
            
        except Exception as e:
            # Логируем ошибки
            logger.error(
                f"Error processing event for user {user_id} ({username}): {e}",
                exc_info=True
            )
            raise
