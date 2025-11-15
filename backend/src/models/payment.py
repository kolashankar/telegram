"""Payment and transaction models"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
import uuid


class Payment(BaseModel):
    """Payment record model"""
    payment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    telegram_id: int
    
    # Payment details
    amount: float
    plan_type: str
    platforms: list  # List of platforms
    
    # UPI details
    upi_id: str = "admin@upi"  # Admin's UPI ID
    transaction_id: Optional[str] = None
    
    # Screenshot verification
    screenshot_file_id: Optional[str] = None  # Telegram file_id
    screenshot_url: Optional[str] = None
    
    # Verification
    status: str = "pending"  # pending, verified, rejected
    verified_by: Optional[str] = None  # admin user_id
    verification_date: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
