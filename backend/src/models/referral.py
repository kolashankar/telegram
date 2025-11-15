"""
Referral System Models
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

class Referral(BaseModel):
    """Referral model for tracking user referrals"""
    referral_id: str = Field(default_factory=lambda: str(__import__('uuid').uuid4()))
    referrer_telegram_id: int
    referred_telegram_id: int
    referrer_username: Optional[str] = None
    referred_username: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_valid: bool = True  # False if referred user leaves or gets banned
    reward_claimed: bool = False

class ReferralStats(BaseModel):
    """User's referral statistics"""
    telegram_id: int
    total_referrals: int = 0
    valid_referrals: int = 0
    pending_referrals: int = 0
    rewards_earned: int = 0
    referral_code: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
