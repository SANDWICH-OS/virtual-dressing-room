from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.database.base import Base
import enum


class TryOnStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TryOnRequest(Base):
    __tablename__ = "tryon_requests"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user_photo_id = Column(Integer, ForeignKey("user_photos.id"), nullable=False)
    clothing_photo_id = Column(Integer, ForeignKey("user_photos.id"), nullable=False)
    result_photo_url = Column(String, nullable=True)
    status = Column(Enum(TryOnStatus), default=TryOnStatus.PENDING)
    error_message = Column(Text, nullable=True)
    ai_model_used = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="tryon_requests")
    user_photo = relationship("UserPhoto", foreign_keys=[user_photo_id])
    clothing_photo = relationship("UserPhoto", foreign_keys=[clothing_photo_id])
