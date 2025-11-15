"""Admin user models"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
import uuid


class Admin(BaseModel):
    """Admin user model"""
    admin_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    telegram_id: int
    telegram_username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    # Admin permissions
    permissions: List[str] = Field(default_factory=lambda: [
        "verify_payments",
        "manage_users",
        "manage_plans",
        "send_announcements",
        "view_analytics"
    ])
    
    # Registration
    registration_code: Optional[str] = None  # Used during registration
    is_active: bool = True
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
