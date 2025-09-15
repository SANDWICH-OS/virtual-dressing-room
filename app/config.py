from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Telegram Bot
    bot_token: str
    
    # Database
    database_url: str
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # AI APIs
    replicate_api_token: Optional[str] = None
    openai_api_key: Optional[str] = None
    
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


settings = Settings()
