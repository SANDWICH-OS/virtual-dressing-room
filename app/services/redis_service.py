import redis.asyncio as redis
from typing import Optional, Any
import json
import os
from app.config import settings


class RedisService:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
    
    async def connect(self):
        """Подключение к Redis"""
        # Определяем, какая конфигурация использовать
        if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_PROJECT_ID"):
            # В Railway используем production конфигурацию
            from app import config_prod
            current_settings = config_prod.settings
        else:
            # Локально используем обычную конфигурацию
            current_settings = settings
            
        # Используем переменную окружения REDIS_URL для Railway
        redis_url = os.getenv("REDIS_URL", current_settings.redis_url)
        
        # Проверяем, что Redis URL не localhost
        if not redis_url or "localhost" in redis_url or "127.0.0.1" in redis_url:
            raise ConnectionError("Redis URL not configured or points to localhost")
            
        self.redis = redis.from_url(redis_url, decode_responses=True)
    
    async def disconnect(self):
        """Отключение от Redis"""
        if self.redis:
            await self.redis.close()
    
    async def set(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Установить значение"""
        if not self.redis:
            await self.connect()
        
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        
        return await self.redis.set(key, value, ex=expire)
    
    async def get(self, key: str) -> Optional[str]:
        """Получить значение"""
        if not self.redis:
            await self.connect()
        
        return await self.redis.get(key)
    
    async def get_json(self, key: str) -> Optional[Any]:
        """Получить JSON значение"""
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None
    
    async def set_json(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """Установить JSON значение"""
        from loguru import logger
        logger.info(f"set_json called: key={key}, value={value}, expire={expire}")
        
        if not self.redis:
            logger.info("Redis not connected, attempting to connect...")
            await self.connect()
        
        try:
            json_value = json.dumps(value)
            logger.info(f"JSON serialized: {json_value}")
            result = await self.redis.set(key, json_value, ex=expire)
            logger.info(f"Redis SET result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in set_json: {e}")
            raise
    
    async def delete(self, key: str) -> bool:
        """Удалить ключ"""
        if not self.redis:
            await self.connect()
        
        return bool(await self.redis.delete(key))
    
    async def exists(self, key: str) -> bool:
        """Проверить существование ключа"""
        if not self.redis:
            await self.connect()
        
        return bool(await self.redis.exists(key))
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """Увеличить значение на amount"""
        if not self.redis:
            await self.connect()
        
        return await self.redis.incrby(key, amount)
    
    async def set_user_generation_count(self, user_id: int, count: int):
        """Установить количество генераций пользователя"""
        key = f"user:{user_id}:generations"
        await self.set(key, count, expire=86400)  # 24 часа
    
    async def get_user_generation_count(self, user_id: int) -> int:
        """Получить количество генераций пользователя"""
        key = f"user:{user_id}:generations"
        count = await self.get(key)
        return int(count) if count else 0
    
    async def increment_user_generation(self, user_id: int) -> int:
        """Увеличить количество генераций пользователя"""
        key = f"user:{user_id}:generations"
        return await self.increment(key, 1)
    
    async def get_user_data(self, user_id: int) -> Optional[dict]:
        """
        Получить все данные пользователя из Redis
        
        Args:
            user_id: Telegram ID пользователя
            
        Returns:
            dict: Данные пользователя или None если не найдены
        """
        key = f"user:{user_id}:data"
        return await self.get_json(key)

    async def set_user_data(self, user_id: int, data: dict, expire: Optional[int] = None) -> bool:
        """
        Сохранить данные пользователя в Redis
        
        Args:
            user_id: Telegram ID пользователя
            data: Словарь с данными пользователя
            expire: Время жизни в секундах (None = постоянно)
            
        Returns:
            bool: True если успешно сохранено
        """
        from loguru import logger
        key = f"user:{user_id}:data"
        logger.info(f"set_user_data called: key={key}, data={data}, expire={expire}")
        
        try:
            result = await self.set_json(key, data, expire=expire)
            logger.info(f"set_json result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in set_user_data: {e}")
            raise

    async def update_user_field(self, user_id: int, field: str, value: Any) -> bool:
        """Обновить конкретное поле пользователя"""
        from loguru import logger
        logger.info(f"update_user_field called: user_id={user_id}, field={field}, value={value}")
        
        try:
            user_data = await self.get_user_data(user_id) or {}
            logger.info(f"Current user data: {user_data}")
            
            user_data[field] = value
            logger.info(f"Updated user data: {user_data}")
            
            result = await self.set_user_data(user_id, user_data)
            logger.info(f"set_user_data result: {result}")
            return result
        except Exception as e:
            logger.error(f"Error in update_user_field: {e}")
            raise

    async def get_user_field(self, user_id: int, field: str, default: Any = None) -> Any:
        """Получить конкретное поле пользователя"""
        user_data = await self.get_user_data(user_id)
        if user_data:
            return user_data.get(field, default)
        return default

    async def clear_user_data(self, user_id: int) -> bool:
        """Полная очистка всех данных пользователя из Redis"""
        keys_to_delete = [
            f"user:{user_id}:data",
            f"user:{user_id}:generations",  # старый ключ, если был
        ]
        
        deleted_count = 0
        for key in keys_to_delete:
            if await self.exists(key):
                await self.delete(key)
                deleted_count += 1
        
        from loguru import logger
        logger.info(f"Cleared {deleted_count} Redis keys for user {user_id}")
        return deleted_count > 0


# Глобальный экземпляр
redis_service = RedisService()
