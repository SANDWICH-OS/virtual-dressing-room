from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Telegram Bot
    bot_token: str = "test_token"  # Заглушка для тестов
    
    # Database
    database_url: str = "sqlite:///./virtual_tryon.db"  # SQLite по умолчанию
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # AI APIs
    replicate_api_token: Optional[str] = None
    openai_api_key: Optional[str] = None
    
    # Fashn AI API
    fashn_api_key: Optional[str] = None
    fashn_api_url: str = "https://api.fashn.ai"
    fashn_webhook_url: Optional[str] = None
    fashn_model_name: str = "tryon-v1.6"
    
    # Fashn API Optional Parameters
    fashn_category: str = "auto"
    fashn_segmentation_free: bool = True
    fashn_moderation_level: str = "permissive"
    fashn_garment_photo_type: str = "auto"
    fashn_mode: str = "balanced"
    fashn_seed: int = 42
    fashn_num_samples: int = 1
    fashn_output_format: str = "png"
    fashn_return_base64: bool = False
    
    # Payment Systems
    yoomoney_shop_id: Optional[str] = None
    yoomoney_secret_key: Optional[str] = None
    
    # File Storage
    cloudinary_cloud_name: Optional[str] = None
    cloudinary_api_key: Optional[str] = None
    cloudinary_api_secret: Optional[str] = None
    
    # App Settings
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
