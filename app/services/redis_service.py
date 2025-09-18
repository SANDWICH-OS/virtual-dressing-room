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


# Глобальный экземпляр
redis_service = RedisService()
