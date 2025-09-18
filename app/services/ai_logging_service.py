from datetime import datetime
from typing import Dict, Any
from loguru import logger
import json


class AILoggingService:
    """Сервис для логирования запросов к ИИ сервисам"""
    
    @staticmethod
    async def log_ai_request(
        user_id: int,
        service_name: str,
        request_data: Dict[str, Any],
        start_time: datetime
    ):
        """Логирование запроса к ИИ сервису"""
        log_data = {
            "user_id": user_id,
            "service_name": service_name,
            "request_data": request_data,
            "start_time": start_time.isoformat(),
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"AI Request: {json.dumps(log_data, ensure_ascii=False)}")
    
    @staticmethod
    async def log_ai_response(
        user_id: int,
        service_name: str,
        response_data: Dict[str, Any],
        processing_time: float,
        success: bool = True,
        error_message: str = None
    ):
        """Логирование ответа от ИИ сервиса"""
        log_data = {
            "user_id": user_id,
            "service_name": service_name,
            "response_data": response_data,
            "processing_time_seconds": processing_time,
            "success": success,
            "error_message": error_message,
            "timestamp": datetime.now().isoformat()
        }
        
        if success:
            logger.info(f"AI Response: {json.dumps(log_data, ensure_ascii=False)}")
        else:
            logger.error(f"AI Error: {json.dumps(log_data, ensure_ascii=False)}")
    
    @staticmethod
    async def log_ai_quality_metrics(
        user_id: int,
        service_name: str,
        quality_score: int,
        processing_time: float,
        user_feedback: str = None
    ):
        """Логирование метрик качества ИИ сервиса"""
        log_data = {
            "user_id": user_id,
            "service_name": service_name,
            "quality_score": quality_score,
            "processing_time_seconds": processing_time,
            "user_feedback": user_feedback,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"AI Quality Metrics: {json.dumps(log_data, ensure_ascii=False)}")


# Создаем экземпляр сервиса
ai_logging_service = AILoggingService()
