import cloudinary
import cloudinary.uploader
from typing import Optional, Tuple
from app.config import settings
from loguru import logger


class FileUtils:
    def __init__(self):
        # Настройка Cloudinary
        cloudinary.config(
            cloud_name=settings.cloudinary_cloud_name,
            api_key=settings.cloudinary_api_key,
            api_secret=settings.cloudinary_api_secret
        )
    
    async def upload_photo(
        self, 
        file_path: str, 
        folder: str = "virtual_tryon",
        public_id: Optional[str] = None
    ) -> Optional[Tuple[str, str]]:
        """
        Загружает фото в Cloudinary
        
        Args:
            file_path: Путь к файлу
            folder: Папка в Cloudinary
            public_id: Публичный ID (если не указан, генерируется автоматически)
            
        Returns:
            Tuple[url, public_id] или None при ошибке
        """
        try:
            result = cloudinary.uploader.upload(
                file_path,
                folder=folder,
                public_id=public_id,
                resource_type="image",
                quality="auto",
                fetch_format="auto"
            )
            
            return result["secure_url"], result["public_id"]
            
        except Exception as e:
            logger.error(f"Error uploading photo to Cloudinary: {e}")
            return None
    
    async def upload_from_url(
        self, 
        url: str, 
        folder: str = "virtual_tryon",
        public_id: Optional[str] = None
    ) -> Optional[Tuple[str, str]]:
        """
        Загружает фото в Cloudinary по URL
        
        Args:
            url: URL изображения
            folder: Папка в Cloudinary
            public_id: Публичный ID
            
        Returns:
            Tuple[url, public_id] или None при ошибке
        """
        try:
            result = cloudinary.uploader.upload(
                url,
                folder=folder,
                public_id=public_id,
                resource_type="image",
                quality="auto",
                fetch_format="auto"
            )
            
            return result["secure_url"], result["public_id"]
            
        except Exception as e:
            logger.error(f"Error uploading photo from URL to Cloudinary: {e}")
            return None
    
    async def delete_photo(self, public_id: str) -> bool:
        """
        Удаляет фото из Cloudinary
        
        Args:
            public_id: Публичный ID фото
            
        Returns:
            True если успешно удалено, False иначе
        """
        try:
            result = cloudinary.uploader.destroy(public_id)
            return result.get("result") == "ok"
            
        except Exception as e:
            logger.error(f"Error deleting photo from Cloudinary: {e}")
            return False
    
    async def get_photo_info(self, public_id: str) -> Optional[dict]:
        """
        Получает информацию о фото из Cloudinary
        
        Args:
            public_id: Публичный ID фото
            
        Returns:
            Словарь с информацией о фото или None
        """
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


# Глобальный экземпляр
file_utils = FileUtils()
