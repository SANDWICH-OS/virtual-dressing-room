from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from app.database.base import Base
import enum


class SubscriptionType(str, enum.Enum):
    FREE = "free"
    PREMIUM = "premium"


class User(Base):
    __tablename__ = "users"
    
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    subscription_type = Column(Enum(SubscriptionType), default=SubscriptionType.FREE)
    generation_count = Column(Integer, default=0)
    
    # Relationships
    photos = relationship("UserPhoto", back_populates="user", cascade="all, delete-orphan")
