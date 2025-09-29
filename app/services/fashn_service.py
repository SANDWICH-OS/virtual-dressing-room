import aiohttp
import asyncio
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
from loguru import logger
import os
from app.config import settings
from app.services.ai_logging_service import ai_logging_service


class FashnService:
    """Сервис для интеграции с Fashn AI API"""
    
    def __init__(self):
        # Определяем, какая конфигурация использовать
        if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_PROJECT_ID"):
            from app import config_prod
            self.settings = config_prod.settings
        else:
            self.settings = settings
            
        self.api_key = self.settings.fashn_api_key
        self.api_url = self.settings.fashn_api_url
        self.webhook_url = self.settings.fashn_webhook_url
        self.model_name = self.settings.fashn_model_name
        
        if not self.api_key:
            logger.warning("⚠️ FASHN_API_KEY not configured")
    
    async def submit_tryon_request(
        self, 
        user_photo_url: str, 
        clothing_photo_url: str,
        user_id: int
    ) -> Tuple[bool, str, Optional[str]]:
        """
        Отправляет запрос на генерацию try-on в Fashn AI
        
        Args:
            user_photo_url: URL фото пользователя
            clothing_photo_url: URL фото одежды
            user_id: ID пользователя для логирования
            
        Returns:
            Tuple[success, message, prediction_id]
        """
        if not self.api_key:
            return False, "❌ Fashn API ключ не настроен", None
            
        if not self.webhook_url:
            return False, "❌ Webhook URL не настроен", None
        
        start_time = datetime.now()
        
        # Логируем запрос
        await ai_logging_service.log_ai_request(
            user_id=user_id,
            service_name="Fashn",
            request_data={
                "type": "try_on_generation",
                "user_photo_url": user_photo_url,
                "clothing_photo_url": clothing_photo_url,
                "model_name": self.model_name
            },
            start_time=start_time
        )
        
        try:
            async with aiohttp.ClientSession() as session:
                # Подготавливаем данные запроса
                payload = {
                    "model_name": self.model_name,
                    "inputs": {
                        "model_image": user_photo_url,
                        "garment_image": clothing_photo_url
                    }
                }
                
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                # Добавляем webhook URL к запросу
                webhook_url = f"{self.api_url}/v1/run?webhook_url={self.webhook_url}"
                
                logger.info(f"Submitting Fashn request for user {user_id}")
                
                async with session.post(webhook_url, json=payload, headers=headers) as response:
                    response_data = await response.json()
                    
                    if response.status == 200:
                        prediction_id = response_data.get("id")
                        if prediction_id:
                            logger.info(f"Fashn request submitted successfully. Prediction ID: {prediction_id}")
                            return True, f"✅ Запрос отправлен в Fashn AI. ID: {prediction_id}", prediction_id
                        else:
                            error_msg = response_data.get("error", "Неизвестная ошибка")
                            return False, f"❌ Ошибка Fashn API: {error_msg}", None
                    else:
                        # Обработка API-level ошибок
                        error_data = response_data.get("error", "Неизвестная ошибка")
                        error_message = response_data.get("message", str(error_data))
                        
                        if response.status == 400:
                            return False, f"❌ Неверный запрос: {error_message}", None
                        elif response.status == 401:
                            return False, "❌ Неверный API ключ Fashn", None
                        elif response.status == 404:
                            return False, "❌ Ресурс не найден", None
                        elif response.status == 429:
                            if "OutOfCredits" in str(error_data):
                                return False, "❌ Недостаточно кредитов в Fashn", None
                            else:
                                return False, "❌ Превышен лимит запросов. Попробуйте позже", None
                        elif response.status == 500:
                            return False, "❌ Внутренняя ошибка сервера Fashn", None
                        else:
                            return False, f"❌ Ошибка Fashn API ({response.status}): {error_message}", None
                            
        except aiohttp.ClientError as e:
            logger.error(f"Network error during Fashn request: {e}")
            return False, "❌ Ошибка сети при обращении к Fashn API", None
        except Exception as e:
            logger.error(f"Unexpected error during Fashn request: {e}")
            return False, f"❌ Неожиданная ошибка: {str(e)}", None
    
    async def process_webhook_callback(self, webhook_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Обрабатывает webhook callback от Fashn AI
        
        Args:
            webhook_data: Данные webhook от Fashn AI
            
        Returns:
            Tuple[success, message]
        """
        try:
            prediction_id = webhook_data.get("id")
            status = webhook_data.get("status")
            error = webhook_data.get("error")
            
            logger.info(f"Processing Fashn webhook: {prediction_id}, status: {status}")
            
            if status == "completed":
                output_urls = webhook_data.get("output", [])
                if output_urls:
                    # Логируем успешный ответ
                    await ai_logging_service.log_ai_response(
                        user_id=0,  # TODO: Получить user_id из контекста
                        service_name="Fashn",
                        response_data={"output_urls": output_urls},
                        processing_time=0,  # TODO: Вычислить время обработки
                        success=True
                    )
                    
                    return True, f"✅ Генерация завершена! Результат: {output_urls[0]}"
                else:
                    return False, "❌ Генерация завершена, но результат не получен"
                    
            elif status == "failed":
                error_name = error.get("name", "Unknown error") if error else "Unknown error"
                error_message = error.get("message", "Неизвестная ошибка") if error else "Неизвестная ошибка"
                
                # Логируем ошибку
                await ai_logging_service.log_ai_response(
                    user_id=0,  # TODO: Получить user_id из контекста
                    service_name="Fashn",
                    response_data={"error": error_name, "message": error_message},
                    processing_time=0,
                    success=False,
                    error_message=error_message
                )
                
                # Обработка различных типов ошибок
                if error_name == "ImageLoadError":
                    return False, "❌ Ошибка загрузки изображения. Проверьте URL фото"
                elif error_name == "ContentModerationError":
                    return False, "❌ Контент не прошел модерацию"
                elif error_name == "PoseError":
                    return False, "❌ Не удалось определить позу человека на фото"
                elif error_name == "PipelineError":
                    return False, "❌ Ошибка обработки. Попробуйте еще раз"
                elif error_name == "ThirdPartyError":
                    return False, "❌ Временная ошибка сервиса. Попробуйте позже"
                else:
                    return False, f"❌ Ошибка генерации: {error_message}"
            else:
                # Статусы starting, in_queue, processing
                return True, f"⏳ Статус: {status}"
                
        except Exception as e:
            logger.error(f"Error processing Fashn webhook: {e}")
            return False, f"❌ Ошибка обработки webhook: {str(e)}"
    
    async def get_credits_balance(self) -> Tuple[bool, str, Optional[int]]:
        """
        Получает баланс кредитов Fashn AI
        
        Returns:
            Tuple[success, message, credits_count]
        """
        if not self.api_key:
            return False, "❌ Fashn API ключ не настроен", None
            
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                async with session.get(f"{self.api_url}/v1/credits", headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        credits = data.get("credits", 0)
                        return True, f"✅ Кредитов: {credits}", credits
                    else:
                        return False, f"❌ Ошибка получения баланса: {response.status}", None
                        
        except Exception as e:
            logger.error(f"Error getting Fashn credits: {e}")
            return False, f"❌ Ошибка получения баланса: {str(e)}", None


# Создаем экземпляр сервиса
fashn_service = FashnService()
