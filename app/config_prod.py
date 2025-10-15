"""
Production configuration for Railway deployment
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional

class ProductionSettings(BaseSettings):
    """Production settings for Railway deployment"""
    
    # Bot configuration
    bot_token: str = os.getenv("BOT_TOKEN", "")
    
    # Database configuration - Railway PostgreSQL
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./virtual_tryon.db")
    
    # Redis configuration - Railway Redis
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Bot token validation
    if not bot_token:
        raise ValueError("BOT_TOKEN environment variable is required for production")
    
    # AI/ML APIs (placeholders for now)
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    replicate_api_token: Optional[str] = os.getenv("REPLICATE_API_TOKEN")
    
    # Fashn AI API
    fashn_api_key: Optional[str] = os.getenv("FASHN_API_KEY")
    fashn_api_url: str = "https://api.fashn.ai"
    fashn_webhook_url: Optional[str] = os.getenv("FASHN_WEBHOOK_URL")
    fashn_model_name: str = "tryon-v1.6"
    
    # Fashn API Optional Parameters
    fashn_category: str = os.getenv("FASHN_CATEGORY", "auto")
    fashn_segmentation_free: bool = os.getenv("FASHN_SEGMENTATION_FREE", "true").lower() == "true"
    fashn_moderation_level: str = os.getenv("FASHN_MODERATION_LEVEL", "permissive")
    fashn_garment_photo_type: str = os.getenv("FASHN_GARMENT_PHOTO_TYPE", "auto")
    fashn_mode: str = os.getenv("FASHN_MODE", "balanced")
    fashn_seed: int = int(os.getenv("FASHN_SEED", "42"))
    fashn_num_samples: int = int(os.getenv("FASHN_NUM_SAMPLES", "1"))
    fashn_output_format: str = os.getenv("FASHN_OUTPUT_FORMAT", "png")
    fashn_return_base64: bool = os.getenv("FASHN_RETURN_BASE64", "false").lower() == "true"
    
    # Payment systems (placeholders for now)
    yoomoney_shop_id: Optional[str] = os.getenv("YOOMONEY_SHOP_ID")
    yoomoney_secret_key: Optional[str] = os.getenv("YOOMONEY_SECRET_KEY")
    sberpay_merchant_id: Optional[str] = os.getenv("SBERPAY_MERCHANT_ID")
    sberpay_secret_key: Optional[str] = os.getenv("SBERPAY_SECRET_KEY")
    
    # File storage (placeholders for now)
    cloudinary_cloud_name: Optional[str] = os.getenv("CLOUDINARY_CLOUD_NAME")
    cloudinary_api_key: Optional[str] = os.getenv("CLOUDINARY_API_KEY")
    cloudinary_api_secret: Optional[str] = os.getenv("CLOUDINARY_API_SECRET")
    
    # Environment
    environment: str = "production"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Игнорируем дополнительные поля

# Create production settings instance
settings = ProductionSettings()
