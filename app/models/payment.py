from sqlalchemy import Column, Integer, String, ForeignKey, Enum, Numeric
from sqlalchemy.orm import relationship
from app.database.base import Base
import enum


class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PaymentType(str, enum.Enum):
    SUBSCRIPTION = "subscription"
    PACKAGE = "package"


class Payment(Base):
    __tablename__ = "payments"
    
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), default="RUB")
    status = Column(Enum(PaymentStatus), default=PaymentStatus.PENDING)
    payment_type = Column(Enum(PaymentType), nullable=False)
    yoomoney_payment_id = Column(String, nullable=True)
    description = Column(String, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="payments")
