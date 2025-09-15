from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import relationship
from app.database.base import Base
import enum


class PhotoType(str, enum.Enum):
    SELFIE = "selfie"
    FULL_BODY = "full_body"
    CLOTHING = "clothing"


class UserPhoto(Base):
    __tablename__ = "user_photos"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    photo_url = Column(String, nullable=False)
    photo_type = Column(Enum(PhotoType), nullable=False)
    cloudinary_public_id = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="photos")
