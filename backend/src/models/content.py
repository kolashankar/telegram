"""Content models for movies and shows"""
from datetime import datetime, date
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
import uuid


class ContentItem(BaseModel):
    """Movie or TV show content item"""
    content_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    content_type: str  # movie, tv_show
    
    # Details
    description: Optional[str] = None
    genres: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    release_date: Optional[date] = None
    rating: Optional[float] = None
    
    # Availability
    platforms: List[str] = Field(default_factory=list)  # OTT platforms where available
    platform_urls: Dict[str, str] = Field(default_factory=dict)
    
    # Media
    poster_url: Optional[str] = None
    trailer_url: Optional[str] = None
    
    # Metadata
    tmdb_id: Optional[str] = None
    imdb_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ReleaseAlert(BaseModel):
    """User's release alert subscription"""
    alert_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    telegram_id: int
    
    # Alert preferences
    genres: List[str] = Field(default_factory=list)
    platforms: List[str] = Field(default_factory=list)
    languages: List[str] = Field(default_factory=list)
    
    # Notification settings
    frequency: str = "daily"  # daily, weekly, instant
    notification_time: str = "09:00"
    telegram_alerts: bool = True
    email_alerts: bool = False
    email: Optional[str] = None
    
    # Metadata
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
