"""Extraction model for DRM key extraction with video quality support"""
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
import uuid


class VideoQuality(BaseModel):
    """Video quality/resolution information"""
    quality_id: str  # e.g., "720p", "1080p", "4k"
    resolution: str  # e.g., "1280x720", "1920x1080"
    bitrate: Optional[int] = None  # in kbps
    codec: Optional[str] = None  # e.g., "h264", "h265"
    fps: Optional[int] = None  # frames per second
    file_size_mb: Optional[float] = None
    stream_url: Optional[str] = None


class KeyData(BaseModel):
    """DRM key information"""
    kid: str  # Key ID
    key: str  # Decryption key
    type: Optional[str] = "CONTENT"  # CONTENT, SD, HD, UHD


class ExtractionResult(BaseModel):
    """Complete extraction result with quality options"""
    extraction_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    telegram_id: Optional[int] = None
    
    # Extraction data
    success: bool
    keys: List[KeyData] = Field(default_factory=list)
    error: Optional[str] = None
    
    # Platform & URL info
    platform: str
    platform_name: Optional[str] = None
    license_url: str
    manifest_url: Optional[str] = None
    pssh: str
    
    # Video quality information
    available_qualities: List[VideoQuality] = Field(default_factory=list)
    recommended_quality: Optional[str] = None
    
    # Metadata
    extraction_time_ms: int = 0
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Download tracking
    downloaded_quality: Optional[str] = None
    download_started_at: Optional[datetime] = None
    download_completed_at: Optional[datetime] = None
    download_status: str = "pending"  # pending, downloading, completed, failed


class UserUsage(BaseModel):
    """Track user usage for rate limiting"""
    user_id: str
    telegram_id: int
    date: str  # YYYY-MM-DD format
    extraction_count: int = 0
    download_count: int = 0
    total_data_downloaded_mb: float = 0.0
    last_extraction_at: Optional[datetime] = None
    last_download_at: Optional[datetime] = None
