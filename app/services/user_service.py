from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.models.user import User, SubscriptionType
from app.models.photo import UserPhoto, PhotoType
from app.services.redis_service import redis_service
from loguru import logger
from typing import List, Optional


class UserService:
    """Сервис для работы с пользователями"""
    
    @staticmethod
    async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> Optional[User]:
        """Получить пользователя по Telegram ID"""
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_user(
        session: AsyncSession, 
        telegram_id: int, 
        username: str = None, 
        first_name: str = None, 
        last_name: str = None
    ) -> User:
        """Создать нового пользователя"""
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            subscription_type=SubscriptionType.FREE
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        logger.info(f"Created new user: {telegram_id}")
        return user
    
    @staticmethod
    async def get_user_photos(
        session: AsyncSession, 
        user_id: int, 
        photo_type: PhotoType = None
    ) -> List[UserPhoto]:
        """Получить фото пользователя"""
        query = select(UserPhoto).where(UserPhoto.user_id == user_id)
        
        if photo_type:
            query = query.where(UserPhoto.photo_type == photo_type)
        
        result = await session.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def add_user_photo(
        session: AsyncSession,
        user_id: int,
        photo_url: str,
        photo_type: PhotoType,
        cloudinary_public_id: str = None
    ) -> UserPhoto:
        """Добавить фото пользователя"""
        # Удаляем старое фото того же типа
        await session.execute(
            select(UserPhoto).where(
                and_(UserPhoto.user_id == user_id, UserPhoto.photo_type == photo_type)
            )
        )
        
        user_photo = UserPhoto(
            user_id=user_id,
            photo_url=photo_url,
            photo_type=photo_type,
            cloudinary_public_id=cloudinary_public_id
        )
        
        session.add(user_photo)
        await session.commit()
        await session.refresh(user_photo)
        
        logger.info(f"Added {photo_type} photo for user {user_id}")
        return user_photo
    
    @staticmethod
    async def delete_user_photo(
        session: AsyncSession, 
        user_id: int, 
        photo_type: PhotoType
    ) -> bool:
        """Удалить фото пользователя"""
        result = await session.execute(
            select(UserPhoto).where(
                and_(UserPhoto.user_id == user_id, UserPhoto.photo_type == photo_type)
            )
        )
        photo = result.scalar_one_or_none()
        
        if photo:
            await session.delete(photo)
            await session.commit()
            logger.info(f"Deleted {photo_type} photo for user {user_id}")
            return True
        
        return False
    
    @staticmethod
    async def get_user_generation_count(user_id: int) -> int:
        """Получить количество генераций пользователя"""
        return await redis_service.get_user_generation_count(user_id)
    
    @staticmethod
    async def increment_user_generation(user_id: int) -> int:
        """Увеличить количество генераций пользователя"""
        return await redis_service.increment_user_generation(user_id)
    
    @staticmethod
    async def check_generation_limit(user_id: int, subscription_type: SubscriptionType) -> bool:
        """Проверить лимит генераций"""
        current_count = await UserService.get_user_generation_count(user_id)
        
        if subscription_type == SubscriptionType.FREE:
            return current_count < 1  # Бесплатно только 1 генерация
        elif subscription_type == SubscriptionType.PREMIUM:
            return current_count < 5  # Premium: 5 генераций в месяц
        
        return False
    
    @staticmethod
    async def get_user_profile_info(session: AsyncSession, user_id: int) -> dict:
        """Получить информацию о профиле пользователя"""
        user = await UserService.get_user_by_telegram_id(session, user_id)
        if not user:
            return {}
        
        photos = await UserService.get_user_photos(session, user_id)
        generation_count = await UserService.get_user_generation_count(user_id)
        
        has_selfie = any(photo.photo_type == PhotoType.SELFIE for photo in photos)
        has_fullbody = any(photo.photo_type == PhotoType.FULL_BODY for photo in photos)
        
        return {
            "user": user,
            "has_selfie": has_selfie,
            "has_fullbody": has_fullbody,
            "generation_count": generation_count,
            "photos_count": len(photos)
        }


# Глобальный экземпляр
user_service = UserService()
