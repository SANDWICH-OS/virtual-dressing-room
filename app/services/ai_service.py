import httpx
import asyncio
from typing import Optional, Dict, Any
from app.config import settings
from loguru import logger


class AIService:
    def __init__(self):
        self.replicate_token = settings.replicate_api_token
        self.openai_key = settings.openai_api_key
    
    async def generate_tryon(
        self, 
        user_photo_url: str, 
        clothing_photo_url: str,
        model: str = "fashn-ai/try-on"
    ) -> Optional[str]:
        """
        Генерирует try-on изображение используя Replicate API
        
        Args:
            user_photo_url: URL фото пользователя
            clothing_photo_url: URL фото одежды
            model: Модель для генерации
            
        Returns:
            URL сгенерированного изображения или None при ошибке
        """
        if not self.replicate_token:
            logger.error("Replicate API token not configured")
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                # Запускаем генерацию
                response = await client.post(
                    "https://api.replicate.com/v1/predictions",
                    headers={
                        "Authorization": f"Token {self.replicate_token}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "version": "latest",
                        "input": {
                            "person_image": user_photo_url,
                            "garment_image": clothing_photo_url,
                            "garment_category": "upperbody"  # Можно сделать настраиваемым
                        }
                    },
                    timeout=30.0
                )
                
                if response.status_code != 201:
                    logger.error(f"Replicate API error: {response.status_code} - {response.text}")
                    return None
                
                prediction = response.json()
                prediction_id = prediction["id"]
                
                # Ждем завершения генерации
                result_url = await self._wait_for_completion(client, prediction_id)
                return result_url
                
        except Exception as e:
            logger.error(f"Error generating try-on: {e}")
            return None
    
    async def _wait_for_completion(
        self, 
        client: httpx.AsyncClient, 
        prediction_id: str,
        max_wait_time: int = 300  # 5 минут максимум
    ) -> Optional[str]:
        """Ждет завершения генерации"""
        start_time = asyncio.get_event_loop().time()
        
        while True:
            # Проверяем таймаут
            if asyncio.get_event_loop().time() - start_time > max_wait_time:
                logger.error("Try-on generation timeout")
                return None
            
            try:
                response = await client.get(
                    f"https://api.replicate.com/v1/predictions/{prediction_id}",
                    headers={"Authorization": f"Token {self.replicate_token}"},
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    logger.error(f"Error checking prediction status: {response.status_code}")
                    return None
                
                prediction = response.json()
                status = prediction["status"]
                
                if status == "succeeded":
                    output = prediction.get("output")
                    if output and len(output) > 0:
                        return output[0]  # Возвращаем первый URL
                    else:
                        logger.error("No output from successful prediction")
                        return None
                
                elif status == "failed":
                    error = prediction.get("error", "Unknown error")
                    logger.error(f"Prediction failed: {error}")
                    return None
                
                elif status in ["starting", "processing"]:
                    # Ждем еще немного
                    await asyncio.sleep(5)
                    continue
                
                else:
                    logger.error(f"Unknown prediction status: {status}")
                    return None
                    
            except Exception as e:
                logger.error(f"Error checking prediction: {e}")
                return None
    
    async def validate_image(self, image_url: str) -> bool:
        """Проверяет, что изображение доступно и корректно"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.head(image_url, timeout=10.0)
                return response.status_code == 200
        except Exception as e:
            logger.error(f"Error validating image {image_url}: {e}")
            return False
    
    async def get_image_info(self, image_url: str) -> Optional[Dict[str, Any]]:
        """Получает информацию об изображении"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.head(image_url, timeout=10.0)
                if response.status_code == 200:
                    return {
                        "content_type": response.headers.get("content-type"),
                        "content_length": response.headers.get("content-length"),
                        "status_code": response.status_code
                    }
        except Exception as e:
            logger.error(f"Error getting image info for {image_url}: {e}")
        
        return None


# Глобальный экземпляр
ai_service = AIService()
