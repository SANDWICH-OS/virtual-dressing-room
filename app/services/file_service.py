from app.utils.file_utils import file_utils
from app.utils.validators import image_validator
from app.models.photo import PhotoType
from app.database.async_session import get_async_session
from app.models.photo import UserPhoto
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from typing import Tuple, Optional


class FileService:
    """Сервис для работы с файлами"""
    
    @staticmethod
    async def upload_user_photo(
        photo_url: str,
        user_id: int,
        photo_type: PhotoType,
        folder_prefix: str = "users"
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Загрузить фото пользователя в Cloudinary
        
        Returns:
            Tuple[cloudinary_url, public_id, error_message]
        """
        try:
            # Валидируем фото
            if photo_type in [PhotoType.SELFIE, PhotoType.FULL_BODY]:
                is_valid, error = await image_validator.validate_user_photo(photo_url)
            else:
                is_valid, error = await image_validator.validate_clothing_photo(photo_url)
            
            if not is_valid:
                return None, None, error
            
            # Загружаем в Cloudinary
            folder = f"{folder_prefix}/{user_id}/{photo_type.value}"
            result = await file_utils.upload_from_url(photo_url, folder=folder)
            
            if not result:
                return None, None, "Ошибка при загрузке в Cloudinary"
            
            cloudinary_url, public_id = result
            logger.info(f"Uploaded {photo_type} photo for user {user_id}")
            
            return cloudinary_url, public_id, None
            
        except Exception as e:
            logger.error(f"Error uploading photo for user {user_id}: {e}")
            return None, None, f"Ошибка загрузки: {str(e)}"
    
    @staticmethod
    async def save_photo_to_database(
        session: AsyncSession,
        user_id: int,
        photo_url: str,
        photo_type: PhotoType,
        cloudinary_public_id: str
    ) -> UserPhoto:
        """Сохранить фото в базу данных"""
        # Удаляем старое фото того же типа
        from sqlalchemy import select, and_
        result = await session.execute(
            select(UserPhoto).where(
                and_(UserPhoto.user_id == user_id, UserPhoto.photo_type == photo_type)
            )
        )
        old_photo = result.scalar_one_or_none()
        
        if old_photo:
            # Удаляем старое фото из Cloudinary
            await file_utils.delete_photo(old_photo.cloudinary_public_id)
            await session.delete(old_photo)
        
        # Создаем новое фото
        user_photo = UserPhoto(
            user_id=user_id,
            photo_url=photo_url,
            photo_type=photo_type,
            cloudinary_public_id=cloudinary_public_id
        )
        
        session.add(user_photo)
        await session.commit()
        await session.refresh(user_photo)
        
        logger.info(f"Saved {photo_type} photo to database for user {user_id}")
        return user_photo
    
    @staticmethod
    async def delete_user_photo(
        session: AsyncSession,
        user_id: int,
        photo_type: PhotoType
    ) -> bool:
        """Удалить фото пользователя"""
        from sqlalchemy import select, and_
        
        result = await session.execute(
            select(UserPhoto).where(
                and_(UserPhoto.user_id == user_id, UserPhoto.photo_type == photo_type)
            )
        )
        photo = result.scalar_one_or_none()
        
        if photo:
            # Удаляем из Cloudinary
            if photo.cloudinary_public_id:
                await file_utils.delete_photo(photo.cloudinary_public_id)
            
            # Удаляем из БД
            await session.delete(photo)
            await session.commit()
            
            logger.info(f"Deleted {photo_type} photo for user {user_id}")
            return True
        
        return False
    
    @staticmethod
    async def get_photo_info(public_id: str) -> Optional[dict]:
        """Получить информацию о фото"""
        return await file_utils.get_photo_info(public_id)
    
    @staticmethod
    async def process_telegram_photo(
        bot,
        photo,
        user_id: int,
        photo_type: PhotoType
    ) -> Tuple[Optional[str], Optional[str], Optional[str]]:
        """
        Обработать фото из Telegram
        
        Returns:
            Tuple[cloudinary_url, public_id, error_message]
        """
        try:
            # Получаем файл
            file = await bot.get_file(photo.file_id)
            photo_url = f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"
            
            # Загружаем в Cloudinary
            return await FileService.upload_user_photo(
                photo_url, user_id, photo_type
            )
            
        except Exception as e:
            logger.error(f"Error processing Telegram photo: {e}")
            return None, None, f"Ошибка обработки фото: {str(e)}"


# Глобальный экземпляр
file_service = FileService()
