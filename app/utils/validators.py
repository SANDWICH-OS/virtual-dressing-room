import httpx
from typing import Optional, Tuple
from PIL import Image
import io
from loguru import logger


class ImageValidator:
    """Валидатор для изображений"""
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    ALLOWED_FORMATS = {'JPEG', 'PNG', 'JPG'}
    MIN_DIMENSIONS = (100, 100)
    MAX_DIMENSIONS = (4000, 4000)
    
    @classmethod
    async def validate_image_url(cls, url: str) -> Tuple[bool, str]:
        """
        Валидирует изображение по URL
        
        Args:
            url: URL изображения
            
        Returns:
            Tuple[is_valid, error_message]
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.head(url, timeout=10.0)
                
                if response.status_code != 200:
                    return False, f"Изображение недоступно (код: {response.status_code})"
                
                content_type = response.headers.get("content-type", "")
                if not content_type.startswith("image/"):
                    return False, "Файл не является изображением"
                
                content_length = response.headers.get("content-length")
                if content_length and int(content_length) > cls.MAX_FILE_SIZE:
                    return False, f"Файл слишком большой (максимум {cls.MAX_FILE_SIZE // (1024*1024)}MB)"
                
                return True, ""
                
        except Exception as e:
            logger.error(f"Error validating image URL {url}: {e}")
            return False, "Ошибка при проверке изображения"
    
    @classmethod
    async def validate_image_content(cls, url: str) -> Tuple[bool, str]:
        """
        Валидирует содержимое изображения
        
        Args:
            url: URL изображения
            
        Returns:
            Tuple[is_valid, error_message]
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0)
                
                if response.status_code != 200:
                    return False, "Не удалось загрузить изображение"
                
                if len(response.content) > cls.MAX_FILE_SIZE:
                    return False, f"Файл слишком большой (максимум {cls.MAX_FILE_SIZE // (1024*1024)}MB)"
                
                # Проверяем содержимое изображения
                try:
                    image = Image.open(io.BytesIO(response.content))
                    
                    # Проверяем формат
                    if image.format not in cls.ALLOWED_FORMATS:
                        return False, f"Неподдерживаемый формат. Разрешены: {', '.join(cls.ALLOWED_FORMATS)}"
                    
                    # Проверяем размеры
                    width, height = image.size
                    if width < cls.MIN_DIMENSIONS[0] or height < cls.MIN_DIMENSIONS[1]:
                        return False, f"Изображение слишком маленькое (минимум {cls.MIN_DIMENSIONS[0]}x{cls.MIN_DIMENSIONS[1]}px)"
                    
                    if width > cls.MAX_DIMENSIONS[0] or height > cls.MAX_DIMENSIONS[1]:
                        return False, f"Изображение слишком большое (максимум {cls.MAX_DIMENSIONS[0]}x{cls.MAX_DIMENSIONS[1]}px)"
                    
                    return True, ""
                    
                except Exception as e:
                    logger.error(f"Error processing image content: {e}")
                    return False, "Поврежденное изображение"
                
        except Exception as e:
            logger.error(f"Error validating image content {url}: {e}")
            return False, "Ошибка при проверке содержимого изображения"
    
    @classmethod
    async def validate_user_photo(cls, url: str) -> Tuple[bool, str]:
        """
        Валидирует фото пользователя для try-on
        
        Args:
            url: URL фото пользователя
            
        Returns:
            Tuple[is_valid, error_message]
        """
        # Базовая валидация URL
        is_valid, error = await cls.validate_image_url(url)
        if not is_valid:
            return False, error
        
        # Валидация содержимого
        is_valid, error = await cls.validate_image_content(url)
        if not is_valid:
            return False, error
        
        # Дополнительные проверки для фото пользователя
        # (можно добавить проверку на наличие лица, позы и т.д.)
        
        return True, ""
    
    @classmethod
    async def validate_clothing_photo(cls, url: str) -> Tuple[bool, str]:
        """
        Валидирует фото одежды для try-on
        
        Args:
            url: URL фото одежды
            
        Returns:
            Tuple[is_valid, error_message]
        """
        # Базовая валидация URL
        is_valid, error = await cls.validate_image_url(url)
        if not is_valid:
            return False, error
        
        # Валидация содержимого
        is_valid, error = await cls.validate_image_content(url)
        if not is_valid:
            return False, error
        
        # Дополнительные проверки для фото одежды
        # (можно добавить проверку на белый фон, четкость и т.д.)
        
        return True, ""


# Глобальный экземпляр
image_validator = ImageValidator()
