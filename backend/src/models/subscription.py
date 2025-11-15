"""Subscription plans and management models"""
from datetime import datetime
from typing import Optional, List, Dict
from pydantic import BaseModel, Field
import uuid


class SubscriptionPlan(BaseModel):
    """OTT Subscription plan model"""
    plan_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    plan_name: str
    plan_type: str  # weekly, monthly, yearly, custom
    platforms: List[str]  # List of OTT platform names
    price: float
    duration_days: int
    features: List[str] = Field(default_factory=list)
    is_active: bool = True
    created_by: str = "admin"  # admin user_id
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class OTTPlatform(BaseModel):
    """OTT Platform details with pricing"""
    platform_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    display_name: str
    icon: str  # emoji or icon identifier
    country: str = "India"
    
    # Pricing
    mobile_plan: Optional[float] = None
    monthly_plan: Optional[float] = None
    yearly_plan: Optional[float] = None
    family_plan: Optional[float] = None
    student_discount: Optional[float] = None
    
    # Features
    features: List[str] = Field(default_factory=list)
    content_types: List[str] = Field(default_factory=lambda: ["Movies", "TV Shows"])
    languages: List[str] = Field(default_factory=list)
    
    # Metadata
    website_url: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
