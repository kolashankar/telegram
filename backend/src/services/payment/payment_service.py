"""Payment management service"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
import uuid

from ...models.payment import Payment
from ...models.user import UserSubscription
from .qr_generator import generate_upi_qr, generate_payment_text


class PaymentService:
    """Service for managing payments"""
    
    def __init__(self, db: AsyncIOMotorDatabase, admin_upi_id: str = "admin@upi"):
        self.db = db
        self.admin_upi_id = admin_upi_id
        self.payments_collection = db["payments"]
    
    async def create_payment(self, user_id: str, telegram_id: int, amount: float, 
                           plan_type: str, platforms: list) -> Payment:
        """
        Create a new payment record
        
        Args:
            user_id: User ID
            telegram_id: Telegram user ID
            amount: Payment amount
            plan_type: Type of plan (weekly, monthly, custom)
            platforms: List of platforms
        
        Returns:
            Payment: Created payment record
        """
        payment = Payment(
            user_id=user_id,
            telegram_id=telegram_id,
            amount=amount,
            plan_type=plan_type,
            platforms=platforms,
            upi_id=self.admin_upi_id,
            status="pending"
        )
        
        await self.payments_collection.insert_one(payment.model_dump())
        return payment
    
    async def get_payment(self, payment_id: str) -> Optional[Payment]:
        """
        Get payment by ID
        
        Args:
            payment_id: Payment ID
        
        Returns:
            Optional[Payment]: Payment record if found
        """
        payment_data = await self.payments_collection.find_one({"payment_id": payment_id})
        if payment_data:
            return Payment(**payment_data)
        return None
    
    async def update_screenshot(self, payment_id: str, file_id: str, file_url: Optional[str] = None) -> bool:
        """
        Update payment with screenshot
        
        Args:
            payment_id: Payment ID
            file_id: Telegram file ID
            file_url: Optional file URL
        
        Returns:
            bool: True if updated successfully
        """
        result = await self.payments_collection.update_one(
            {"payment_id": payment_id},
            {
                "$set": {
                    "screenshot_file_id": file_id,
                    "screenshot_url": file_url,
                    "updated_at": datetime.utcnow()
                }
            }
        )
        return result.modified_count > 0
    
    async def verify_payment(self, payment_id: str, admin_id: str, approved: bool = True, 
                           reason: Optional[str] = None) -> bool:
        """
        Verify or reject a payment
        
        Args:
            payment_id: Payment ID
            admin_id: Admin user ID
            approved: Whether payment is approved
            reason: Rejection reason if not approved
        
        Returns:
            bool: True if updated successfully
        """
        status = "verified" if approved else "rejected"
        
        update_data = {
            "status": status,
            "verified_by": admin_id,
            "verification_date": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        if not approved and reason:
            update_data["rejection_reason"] = reason
        
        result = await self.payments_collection.update_one(
            {"payment_id": payment_id},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    async def get_pending_payments(self, limit: int = 50) -> list:
        """
        Get all pending payments for admin verification
        
        Args:
            limit: Maximum number of payments to return
        
        Returns:
            list: List of pending payments
        """
        cursor = self.payments_collection.find({"status": "pending"}).sort("created_at", -1).limit(limit)
        payments = await cursor.to_list(length=limit)
        return [Payment(**p) for p in payments]
    
    async def get_user_payments(self, user_id: str, limit: int = 20) -> list:
        """
        Get all payments for a user
        
        Args:
            user_id: User ID
            limit: Maximum number of payments
        
        Returns:
            list: List of user payments
        """
        cursor = self.payments_collection.find({"user_id": user_id}).sort("created_at", -1).limit(limit)
        payments = await cursor.to_list(length=limit)
        return [Payment(**p) for p in payments]
    
    def generate_qr_code(self, amount: float, payment_id: str) -> bytes:
        """
        Generate UPI QR code for payment
        
        Args:
            amount: Payment amount
            payment_id: Payment ID for reference
        
        Returns:
            bytes: QR code image
        """
        return generate_upi_qr(
            upi_id=self.admin_upi_id,
            amount=amount,
            name="OTT Subscription",
            transaction_id=payment_id[:8]
        )
    
    def get_payment_instructions(self, amount: float, platforms: list) -> str:
        """
        Get payment instruction text
        
        Args:
            amount: Payment amount
            platforms: List of platforms
        
        Returns:
            str: Payment instructions
        """
        return generate_payment_text(self.admin_upi_id, amount, platforms)
