"""
Referral Service for OTT Bot
Handles referral tracking, validation, and rewards
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import uuid
import hashlib

logger = logging.getLogger(__name__)

class ReferralService:
    """Service to manage user referrals and rewards"""
    
    def __init__(self, db):
        self.db = db
        self.referrals_collection = db.referrals
        self.referral_stats_collection = db.referral_stats
    
    def generate_referral_code(self, telegram_id: int) -> str:
        """Generate unique referral code for user"""
        # Create a unique code based on telegram_id
        raw = f"{telegram_id}_{uuid.uuid4().hex[:8]}"
        code = hashlib.md5(raw.encode()).hexdigest()[:8].upper()
        return f"REF{code}"
    
    async def get_or_create_referral_stats(self, telegram_id: int) -> Dict:
        """Get or create referral stats for user"""
        stats = await self.referral_stats_collection.find_one({"telegram_id": telegram_id})
        
        if not stats:
            referral_code = self.generate_referral_code(telegram_id)
            stats = {
                "telegram_id": telegram_id,
                "total_referrals": 0,
                "valid_referrals": 0,
                "pending_referrals": 0,
                "rewards_earned": 0,
                "referral_code": referral_code,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            await self.referral_stats_collection.insert_one(stats)
        
        return stats
    
    async def add_referral(self, referrer_telegram_id: int, referred_telegram_id: int,
                          referrer_username: str = None, referred_username: str = None) -> bool:
        """Add a new referral"""
        try:
            # Check if already referred
            existing = await self.referrals_collection.find_one({
                "referred_telegram_id": referred_telegram_id
            })
            
            if existing:
                logger.warning(f"User {referred_telegram_id} already referred")
                return False
            
            # Check if trying to refer themselves
            if referrer_telegram_id == referred_telegram_id:
                logger.warning("User cannot refer themselves")
                return False
            
            # Create referral record
            referral = {
                "referral_id": str(uuid.uuid4()),
                "referrer_telegram_id": referrer_telegram_id,
                "referred_telegram_id": referred_telegram_id,
                "referrer_username": referrer_username,
                "referred_username": referred_username,
                "created_at": datetime.utcnow(),
                "is_valid": True,
                "reward_claimed": False
            }
            
            await self.referrals_collection.insert_one(referral)
            
            # Update referrer stats
            await self.referral_stats_collection.update_one(
                {"telegram_id": referrer_telegram_id},
                {
                    "$inc": {
                        "total_referrals": 1,
                        "pending_referrals": 1
                    },
                    "$set": {"updated_at": datetime.utcnow()}
                },
                upsert=True
            )
            
            logger.info(f"Referral added: {referrer_telegram_id} -> {referred_telegram_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding referral: {e}")
            return False
    
    async def validate_referral(self, referred_telegram_id: int) -> bool:
        """Validate a referral (called when referred user becomes active)"""
        try:
            referral = await self.referrals_collection.find_one({
                "referred_telegram_id": referred_telegram_id,
                "is_valid": True
            })
            
            if not referral:
                return False
            
            # Update referral status
            await self.referrals_collection.update_one(
                {"referral_id": referral["referral_id"]},
                {"$set": {"is_valid": True, "validated_at": datetime.utcnow()}}
            )
            
            # Update referrer stats
            await self.referral_stats_collection.update_one(
                {"telegram_id": referral["referrer_telegram_id"]},
                {
                    "$inc": {
                        "valid_referrals": 1,
                        "pending_referrals": -1
                    },
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            logger.info(f"Referral validated for user {referred_telegram_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error validating referral: {e}")
            return False
    
    async def check_referral_rewards(self, telegram_id: int, required_count: int = 20) -> Dict:
        """Check if user is eligible for referral rewards"""
        stats = await self.get_or_create_referral_stats(telegram_id)
        
        valid_referrals = stats.get("valid_referrals", 0)
        rewards_earned = stats.get("rewards_earned", 0)
        
        # Calculate eligible rewards (1 reward per required_count referrals)
        eligible_rewards = valid_referrals // required_count
        pending_rewards = eligible_rewards - rewards_earned
        
        return {
            "valid_referrals": valid_referrals,
            "required_count": required_count,
            "eligible_rewards": eligible_rewards,
            "pending_rewards": pending_rewards,
            "rewards_earned": rewards_earned,
            "progress": valid_referrals % required_count,
            "next_reward_at": required_count - (valid_referrals % required_count)
        }
    
    async def claim_referral_reward(self, telegram_id: int) -> bool:
        """Claim pending referral reward"""
        try:
            reward_info = await self.check_referral_rewards(telegram_id)
            
            if reward_info["pending_rewards"] <= 0:
                return False
            
            # Update rewards earned
            await self.referral_stats_collection.update_one(
                {"telegram_id": telegram_id},
                {
                    "$inc": {"rewards_earned": 1},
                    "$set": {"updated_at": datetime.utcnow()}
                }
            )
            
            logger.info(f"Referral reward claimed by user {telegram_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error claiming reward: {e}")
            return False
    
    async def get_referral_list(self, telegram_id: int, limit: int = 50) -> List[Dict]:
        """Get list of users referred by this user"""
        referrals = await self.referrals_collection.find(
            {"referrer_telegram_id": telegram_id}
        ).sort("created_at", -1).limit(limit).to_list(limit)
        
        return referrals
    
    async def get_referrer(self, telegram_id: int) -> Optional[Dict]:
        """Get who referred this user"""
        referral = await self.referrals_collection.find_one({
            "referred_telegram_id": telegram_id
        })
        return referral
    
    async def find_user_by_referral_code(self, referral_code: str) -> Optional[int]:
        """Find telegram_id by referral code"""
        stats = await self.referral_stats_collection.find_one({
            "referral_code": referral_code
        })
        
        if stats:
            return stats.get("telegram_id")
        return None
