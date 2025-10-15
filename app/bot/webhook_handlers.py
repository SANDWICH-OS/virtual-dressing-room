from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from typing import Dict, Any
import json
from loguru import logger
from app.services.fashn_service import fashn_service
from app.services.redis_service import redis_service
from aiogram import Bot
import os
from app.config import settings


class WebhookHandler:
    """Обработчик webhook'ов от Fashn AI"""
    
    def __init__(self):
        # Определяем, какая конфигурация использовать
        if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_PROJECT_ID"):
            from app import config_prod
            self.settings = config_prod.settings
        else:
            self.settings = settings
            
        self.bot = Bot(token=self.settings.bot_token)
    
    async def handle_fashn_webhook(self, request: Request) -> JSONResponse:
        """
        Обрабатывает webhook от Fashn AI
        
        Args:
            request: FastAPI Request объект
            
        Returns:
            JSONResponse: Ответ для Fashn AI
        """
        try:
            # Получаем данные webhook
            webhook_data = await request.json()
            logger.info(f"Received Fashn webhook: {webhook_data}")
            
            # Извлекаем prediction ID
            prediction_id = webhook_data.get("id")
            if not prediction_id:
                logger.error("No prediction ID in webhook data")
                return JSONResponse({"error": "No prediction ID"}, status_code=400)
            
            # Получаем контекст пользователя из Redis
            user_context = await redis_service.get_json(f"fashn_prediction:{prediction_id}")
            if not user_context:
                logger.warning(f"No user context found for prediction {prediction_id}")
                return JSONResponse({"error": "No user context"}, status_code=404)
            
            user_id = user_context.get("user_id")
            if not user_id:
                logger.error(f"No user_id in context for prediction {prediction_id}")
                return JSONResponse({"error": "No user_id in context"}, status_code=400)
            
            # Обрабатываем webhook через FashnService
            success, message = await fashn_service.process_webhook_callback(webhook_data)
            
            if success:
                # Отправляем результат пользователю
                await self._send_result_to_user(user_id, webhook_data, message)
            else:
                # Отправляем ошибку пользователю
                await self._send_error_to_user(user_id, message)
            
            # Очищаем контекст из Redis
            await redis_service.delete(f"fashn_prediction:{prediction_id}")
            
            return JSONResponse({"status": "processed"})
            
        except json.JSONDecodeError:
            logger.error("Invalid JSON in webhook data")
            return JSONResponse({"error": "Invalid JSON"}, status_code=400)
        except Exception as e:
            logger.error(f"Error processing Fashn webhook: {e}")
            return JSONResponse({"error": "Internal server error"}, status_code=500)
    
    async def _send_result_to_user(self, user_id: int, webhook_data: Dict[str, Any], message: str):
        """Отправляет результат пользователю"""
        try:
            output_urls = webhook_data.get("output", [])
            
            if output_urls:
                # Проверяем, является ли первый результат base64
                first_output = output_urls[0]
                if first_output.startswith("data:image/"):
                    # Это base64 - конвертируем в файл
                    import base64
                    import io
                    from aiogram.types import BufferedInputFile
                    
                    # Извлекаем base64 данные
                    header, data = first_output.split(",", 1)
                    image_data = base64.b64decode(data)
                    
                    # Создаем BufferedInputFile
                    photo_file = BufferedInputFile(image_data, filename="result.png")
                    
                    await self.bot.send_photo(
                        chat_id=user_id,
                        photo=photo_file,
                        caption=f"🎉 <b>Генерация завершена!</b>\n\n{message}"
                    )
                else:
                    # Это URL - отправляем как обычно
                    await self.bot.send_photo(
                        chat_id=user_id,
                        photo=first_output,
                        caption=f"🎉 <b>Генерация завершена!</b>\n\n{message}"
                    )
                
                # Если есть дополнительные изображения, отправляем их
                for i, url in enumerate(output_urls[1:], 2):
                    if url.startswith("data:image/"):
                        # Обрабатываем base64
                        header, data = url.split(",", 1)
                        image_data = base64.b64decode(data)
                        photo_file = BufferedInputFile(image_data, filename=f"result_{i}.png")
                        await self.bot.send_photo(
                            chat_id=user_id,
                            photo=photo_file,
                            caption=f"📸 <b>Дополнительный результат {i}</b>"
                        )
                    else:
                        # Обычный URL
                        await self.bot.send_photo(
                            chat_id=user_id,
                            photo=url,
                            caption=f"📸 <b>Дополнительный результат {i}</b>"
                        )
            else:
                await self.bot.send_message(
                    chat_id=user_id,
                    text=f"✅ <b>Генерация завершена</b>\n\n{message}"
                )
                
        except Exception as e:
            logger.error(f"Error sending result to user {user_id}: {e}")
            await self.bot.send_message(
                chat_id=user_id,
                text="❌ <b>Ошибка отправки результата</b>\n\nПопробуйте еще раз или обратитесь в поддержку."
            )
    
    async def _send_error_to_user(self, user_id: int, error_message: str):
        """Отправляет ошибку пользователю"""
        try:
            await self.bot.send_message(
                chat_id=user_id,
                text=f"❌ <b>Ошибка генерации</b>\n\n{error_message}\n\nПопробуйте еще раз или обратитесь в поддержку."
            )
        except Exception as e:
            logger.error(f"Error sending error to user {user_id}: {e}")


# Создаем экземпляр обработчика
webhook_handler = WebhookHandler()


def setup_webhook_routes(app: FastAPI):
    """Настраивает маршруты для webhook'ов"""
    
    @app.post("/webhook/fashn")
    async def fashn_webhook_endpoint(request: Request):
        """Endpoint для webhook'ов от Fashn AI"""
        return await webhook_handler.handle_fashn_webhook(request)
    
    @app.get("/webhook/fashn/health")
    async def webhook_health():
        """Health check для webhook endpoint"""
        return {"status": "ok", "service": "fashn_webhook"}
