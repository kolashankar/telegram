"""User model for managing user profiles and subscriptions"""
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
import uuid


class UserPreferences(BaseModel):
    """User preferences for content and notifications"""
    preferred_languages: List[str] = Field(default_factory=lambda: ["Hindi", "English"])
    preferred_genres: List[str] = Field(default_factory=list)
    preferred_platforms: List[str] = Field(default_factory=list)
    notification_frequency: str = "daily"  # daily, weekly
    notification_time: str = "09:00"  # 24-hour format
    region: str = "India"


class UserSubscription(BaseModel):
    """User's active subscription details"""
    subscription_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    plan_type: str  # weekly, monthly, custom
    platforms: List[str]  # List of OTT platforms
    amount_paid: float
    start_date: datetime
    expiry_date: datetime
    is_active: bool = True
    payment_id: Optional[str] = None


class User(BaseModel):
    """Main user model"""
    user_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    telegram_id: int
    telegram_username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_admin: bool = False
    is_premium: bool = False
    
    # Subscription details
    active_subscriptions: List[UserSubscription] = Field(default_factory=list)
    total_spent: float = 0.0
    
    # Usage tracking
    total_extractions: int = 0
    total_downloads: int = 0
    total_data_downloaded_mb: float = 0.0
    
    # Preferences
    preferences: UserPreferences = Field(default_factory=UserPreferences)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class UserWatchlist(BaseModel):
    """User's watchlist for movies and shows"""
    watchlist_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    telegram_id: int
    items: List[Dict] = Field(default_factory=list)  # List of content items
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
