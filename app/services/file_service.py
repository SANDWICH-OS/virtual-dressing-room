# file_utils удален, используем прямую интеграцию с Cloudinary
import cloudinary
import cloudinary.uploader
from app.utils.validators import image_validator
from app.models.photo import PhotoType
from app.database.async_session import get_async_session
from app.models.photo import UserPhoto
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
from typing import Tuple, Optional
import time
from app.config import settings


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
            if photo_type == PhotoType.USER_PHOTO:
                is_valid, error = await image_validator.validate_user_photo(photo_url)
            else:
                is_valid, error = await image_validator.validate_clothing_photo(photo_url)
            
            if not is_valid:
                return None, None, error
            
            # Проверяем, настроен ли Cloudinary
            from app.config import settings
            if not settings.cloudinary_cloud_name or not settings.cloudinary_api_key:
                logger.warning("Cloudinary not configured, using fallback mode")
                # Fallback режим - используем оригинальный URL от Telegram
                public_id = f"telegram_{user_id}_{photo_type.value}_{int(time.time())}"
                return photo_url, public_id, None
            
            # Настраиваем Cloudinary
            cloudinary.config(
                cloud_name=settings.cloudinary_cloud_name,
                api_key=settings.cloudinary_api_key,
                api_secret=settings.cloudinary_api_secret
            )
            
            # Загружаем в Cloudinary
            folder = f"{folder_prefix}/{user_id}/{photo_type.value}"
            try:
                result = cloudinary.uploader.upload(
                    photo_url,
                    folder=folder,
                    resource_type="image",
                    quality="auto",
                    fetch_format="auto"
                )
                cloudinary_url = result["secure_url"]
                public_id = result["public_id"]
            except Exception as e:
                logger.warning(f"Cloudinary upload failed: {e}, using fallback mode")
                # Fallback режим - используем оригинальный URL от Telegram
                public_id = f"telegram_{user_id}_{photo_type.value}_{int(time.time())}"
                return photo_url, public_id, None
            logger.info(f"Uploaded {photo_type} photo for user {user_id}")
            
            return cloudinary_url, public_id, None
            
        except Exception as e:
            logger.error(f"Error uploading photo for user {user_id}: {e}")
            # Fallback режим при любой ошибке
            logger.warning("Using fallback mode due to error")
            import time
            public_id = f"telegram_{user_id}_{photo_type.value}_{int(time.time())}"
            return photo_url, public_id, None
    
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
            try:
                cloudinary.uploader.destroy(old_photo.cloudinary_public_id)
            except Exception as e:
                logger.warning(f"Failed to delete old photo from Cloudinary: {e}")
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
                try:
                    cloudinary.uploader.destroy(photo.cloudinary_public_id)
                except Exception as e:
                    logger.warning(f"Failed to delete photo from Cloudinary: {e}")
            
            # Удаляем из БД
            await session.delete(photo)
            await session.commit()
            
            logger.info(f"Deleted {photo_type} photo for user {user_id}")
            return True
        
        return False
    
    @staticmethod
    async def get_photo_info(public_id: str) -> Optional[dict]:
        """Получить информацию о фото"""
        try:
            result = cloudinary.api.resource(public_id)
            return {
                "url": result["secure_url"],
                "width": result["width"],
                "height": result["height"],
                "format": result["format"],
                "bytes": result["bytes"],
                "created_at": result["created_at"]
            }
        except Exception as e:
            logger.error(f"Error getting photo info from Cloudinary: {e}")
            return None
    
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
            
            logger.info(f"Processing Telegram photo: {photo_url}")
            logger.info(f"File path: {file.file_path}")
            logger.info(f"File size: {photo.file_size}")
            
            # Загружаем в Cloudinary
            return await FileService.upload_user_photo(
                photo_url, user_id, photo_type
            )
            
        except Exception as e:
            logger.error(f"Error processing Telegram photo: {e}")
            return None, None, f"Ошибка обработки фото: {str(e)}"


# Глобальный экземпляр
file_service = FileService()
