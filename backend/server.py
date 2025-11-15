from fastapi import FastAPI, APIRouter, HTTPException, Request
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import sys
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
import asyncio
import httpx
import json

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ============= MODELS =============
from src.models.extraction import ExtractionResult as ExtractResult, VideoQuality, KeyData as ExtKeyData, UserUsage

class ExtractionRequest(BaseModel):
    pssh: str
    license_url: str
    manifest_url: Optional[str] = None
    headers: Optional[Dict[str, str]] = {}
    challenge: Optional[str] = None
    user_id: Optional[str] = None
    telegram_id: Optional[int] = None

class KeyData(BaseModel):
    kid: str
    key: str

class ExtractionResult(BaseModel):
    model_config = ConfigDict(extra="ignore")
    extraction_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    success: bool
    keys: Optional[List[KeyData]] = []
    error: Optional[str] = None
    platform: str
    platform_name: Optional[str] = None
    url: Optional[str] = None
    pssh: str
    license_url: str
    available_qualities: List[VideoQuality] = []
    recommended_quality: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    user_id: Optional[str] = None
    telegram_id: Optional[int] = None
    extraction_time_ms: Optional[int] = 0

class DownloadRequest(BaseModel):
    extraction_id: str
    quality: str
    telegram_id: Optional[int] = None

class UserConfig(BaseModel):
    model_config = ConfigDict(extra="ignore")
    user_id: str
    widevine_api_key: Optional[str] = None
    telegram_chat_id: Optional[int] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserQuotaResponse(BaseModel):
    telegram_id: int
    daily_limit: int
    used_today: int
    remaining: int
    resets_at: str

# ============= PLATFORM DETECTION =============
from src.utils.platform_detector import detect_platform, is_license_url
from src.services.widevine.extractor import WidevineExtractor
from src.services.video.quality_detector import QualityDetector
from src.services.video.downloader import VideoDownloader

# Load configuration
FREE_USER_LIMIT = int(os.environ.get('FREE_USER_DAILY_LIMIT', 10))
PREMIUM_USER_LIMIT = int(os.environ.get('PREMIUM_USER_DAILY_LIMIT', 100))
ADMIN_USER_LIMIT = int(os.environ.get('ADMIN_USER_DAILY_LIMIT', 999999))

# ============= HEALTH CHECK & STATUS =============
@api_router.get("/health")
async def health_check():
    """Check API and MongoDB connection status"""
    try:
        # Test MongoDB connection
        await client.admin.command('ping')
        mongo_status = "connected"
        mongo_message = "MongoDB connected successfully"
        mongo_error = None
    except Exception as e:
        mongo_status = "disconnected"
        mongo_message = "Failed to connect MongoDB"
        mongo_error = str(e)
    
    return {
        "status": "healthy" if mongo_status == "connected" else "unhealthy",
        "message": mongo_message,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "mongodb": {
            "status": mongo_status,
            "message": mongo_message,
            "error": mongo_error,
            "database": os.environ.get('DB_NAME', 'unknown')
        }
    }

@api_router.get("/status/mongodb")
async def mongodb_status():
    """Get detailed MongoDB connection status"""
    try:
        # Ping MongoDB
        await client.admin.command('ping')
        
        # Get server info
        server_info = await client.admin.command('serverStatus')
        
        # Get database stats
        db_stats = await db.command('dbStats')
        
        # Count collections
        collections = await db.list_collection_names()
        
        # Get connection pool info
        connection_info = {
            "uptime_seconds": server_info.get('uptime', 0),
            "connections": server_info.get('connections', {}),
            "network": server_info.get('network', {}),
        }
        
        return {
            "status": "connected",
            "message": "MongoDB connected successfully",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "connection": {
                "url": mongo_url.replace(mongo_url.split('@')[0].split('://')[1], "***") if '@' in mongo_url else "***",
                "database": os.environ.get('DB_NAME', 'unknown'),
                "status": "active"
            },
            "server": {
                "uptime_seconds": connection_info.get('uptime_seconds', 0),
                "connections": connection_info.get('connections', {}),
                "network": connection_info.get('network', {}),
            },
            "database": {
                "size_bytes": db_stats.get('dataSize', 0),
                "storage_size_bytes": db_stats.get('storageSize', 0),
                "collections_count": len(collections),
                "collections": collections,
                "indexes": db_stats.get('indexes', 0),
                "avg_obj_size": db_stats.get('avgObjSize', 0)
            },
            "health": {
                "is_master": server_info.get('repl', {}).get('ismaster', False) if 'repl' in server_info else True,
                "ok": server_info.get('ok', 0) == 1
            }
        }
    except Exception as e:
        logger.error(f"MongoDB status check error: {str(e)}")
        return {
            "status": "disconnected",
            "message": "Failed to connect MongoDB",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(e),
            "connection": {
                "url": "***",
                "database": os.environ.get('DB_NAME', 'unknown'),
                "status": "inactive"
            }
        }

# ============= API ENDPOINTS =============
@api_router.get("/")
async def root():
    return {"message": "Telegram DRM Bot API", "version": "1.0.0"}

async def check_user_quota(telegram_id: int) -> Dict:
    """Check if user has remaining quota"""
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    
    # Get user usage
    usage = await db.user_usage.find_one({
        'telegram_id': telegram_id,
        'date': today
    })
    
    if not usage:
        usage = {
            'telegram_id': telegram_id,
            'date': today,
            'extraction_count': 0,
            'download_count': 0
        }
        await db.user_usage.insert_one(usage)
    
    # Check if user is admin
    admin = await db.admins.find_one({'telegram_id': telegram_id, 'is_active': True})
    if admin:
        daily_limit = ADMIN_USER_LIMIT
    else:
        # Check if premium user (has active subscription)
        user = await db.users.find_one({'telegram_id': telegram_id})
        if user and user.get('active_subscriptions'):
            daily_limit = PREMIUM_USER_LIMIT
        else:
            daily_limit = FREE_USER_LIMIT
    
    used_today = usage.get('extraction_count', 0)
    remaining = max(0, daily_limit - used_today)
    
    return {
        'has_quota': remaining > 0,
        'daily_limit': daily_limit,
        'used_today': used_today,
        'remaining': remaining
    }

async def increment_user_usage(telegram_id: int, usage_type: str = 'extraction'):
    """Increment user usage counter"""
    today = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    
    field = f'{usage_type}_count'
    await db.user_usage.update_one(
        {'telegram_id': telegram_id, 'date': today},
        {
            '$inc': {field: 1},
            '$set': {f'last_{usage_type}_at': datetime.now(timezone.utc)}
        },
        upsert=True
    )

@api_router.post("/extract", response_model=ExtractionResult)
async def extract_keys(request: ExtractionRequest):
    """Extract DRM keys from PSSH and license URL with quality detection"""
    try:
        start_time = datetime.now(timezone.utc)
        
        # Check user quota if telegram_id provided
        if request.telegram_id:
            quota = await check_user_quota(request.telegram_id)
            if not quota['has_quota']:
                raise HTTPException(
                    status_code=429,
                    detail=f"Daily limit reached. Used {quota['used_today']}/{quota['daily_limit']}. Resets tomorrow."
                )
        
        # Use mock API key for now
        widevine_api_key = os.environ.get('WIDEVINE_API_KEY', 'wv_mock_key_12345')
        
        extractor = WidevineExtractor(widevine_api_key)
        platform = detect_platform(request.license_url)
        
        result = await extractor.extract_keys(
            pssh=request.pssh,
            license_url=request.license_url,
            headers=request.headers,
            challenge=request.challenge
        )
        
        # Detect available video qualities
        qualities = []
        if request.manifest_url:
            qualities = await QualityDetector.detect_from_manifest(
                request.manifest_url, 
                request.headers
            )
        else:
            qualities = QualityDetector.detect_from_pssh(request.pssh)
        
        recommended_quality = QualityDetector.get_recommended_quality(qualities)
        
        extraction_time = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
        
        # Save to database
        extraction_doc = ExtractionResult(
            extraction_id=str(uuid.uuid4()),
            success=result['success'],
            keys=result.get('keys', []),
            error=result.get('error'),
            platform=platform,
            platform_name=platform,
            pssh=request.pssh,
            license_url=request.license_url,
            available_qualities=qualities,
            recommended_quality=recommended_quality,
            extraction_time_ms=extraction_time,
            user_id=request.user_id,
            telegram_id=request.telegram_id
        )
        
        doc = extraction_doc.model_dump()
        doc['timestamp'] = doc['timestamp'].isoformat()
        await db.extractions.insert_one(doc)
        
        # Increment usage counter
        if request.telegram_id:
            await increment_user_usage(request.telegram_id, 'extraction')
        
        return extraction_doc
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Extraction error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/extractions", response_model=List[ExtractionResult])
async def get_extractions(limit: int = 50, telegram_id: Optional[int] = None):
    """Get extraction history"""
    query = {}
    if telegram_id:
        query['telegram_id'] = telegram_id
    
    extractions = await db.extractions.find(query, {"_id": 0}).sort("timestamp", -1).to_list(limit)
    
    for extraction in extractions:
        if isinstance(extraction.get('timestamp'), str):
            extraction['timestamp'] = datetime.fromisoformat(extraction['timestamp'])
        # Ensure available_qualities exists
        if 'available_qualities' not in extraction:
            extraction['available_qualities'] = []
    
    return extractions

@api_router.get("/extraction/{extraction_id}")
async def get_extraction_details(extraction_id: str):
    """Get specific extraction details with available qualities"""
    extraction = await db.extractions.find_one({'extraction_id': extraction_id}, {"_id": 0})
    
    if not extraction:
        raise HTTPException(status_code=404, detail="Extraction not found")
    
    if isinstance(extraction.get('timestamp'), str):
        extraction['timestamp'] = datetime.fromisoformat(extraction['timestamp'])
    
    return extraction

@api_router.post("/download")
async def request_download(request: DownloadRequest):
    """Request video download with selected quality"""
    try:
        # Get extraction details
        extraction = await db.extractions.find_one({'extraction_id': request.extraction_id}, {"_id": 0})
        
        if not extraction:
            raise HTTPException(status_code=404, detail="Extraction not found")
        
        # Verify quality is available
        available_qualities = extraction.get('available_qualities', [])
        quality_ids = [q.get('quality_id') for q in available_qualities]
        
        if request.quality not in quality_ids:
            raise HTTPException(
                status_code=400, 
                detail=f"Quality {request.quality} not available. Available: {', '.join(quality_ids)}"
            )
        
        # Get selected quality details
        selected_quality = next((q for q in available_qualities if q.get('quality_id') == request.quality), None)
        
        # Initialize downloader
        downloader = VideoDownloader()
        download_info = await downloader.get_download_info(request.extraction_id, request.quality)
        
        # Update extraction record
        await db.extractions.update_one(
            {'extraction_id': request.extraction_id},
            {
                '$set': {
                    'downloaded_quality': request.quality,
                    'download_started_at': datetime.now(timezone.utc),
                    'download_status': 'ready'
                }
            }
        )
        
        # Increment download counter
        if request.telegram_id:
            await increment_user_usage(request.telegram_id, 'download')
        
        return {
            'success': True,
            'extraction_id': request.extraction_id,
            'quality': request.quality,
            'quality_details': selected_quality,
            'download_info': download_info,
            'message': f"Download prepared for {request.quality}",
            'note': 'This is a mock implementation. In production, actual download would be initiated.'
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download request error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.get("/user/quota/{telegram_id}", response_model=UserQuotaResponse)
async def get_user_quota(telegram_id: int):
    """Get user's current quota status"""
    try:
        quota = await check_user_quota(telegram_id)
        
        # Calculate reset time (next day at 00:00 UTC)
        from datetime import timedelta
        tomorrow = datetime.now(timezone.utc).date() + timedelta(days=1)
        reset_time = datetime.combine(tomorrow, datetime.min.time())
        
        return UserQuotaResponse(
            telegram_id=telegram_id,
            daily_limit=quota['daily_limit'],
            used_today=quota['used_today'],
            remaining=quota['remaining'],
            resets_at=reset_time.isoformat()
        )
    except Exception as e:
        logger.error(f"Quota check error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@api_router.post("/config")
async def save_user_config(config: UserConfig):
    """Save user configuration"""
    config_dict = config.model_dump()
    config_dict['updated_at'] = datetime.now(timezone.utc).isoformat()
    config_dict['created_at'] = config_dict['created_at'].isoformat()
    
    await db.user_configs.update_one(
        {"user_id": config.user_id},
        {"$set": config_dict},
        upsert=True
    )
    
    return {"message": "Configuration saved successfully"}

@api_router.get("/config/{user_id}")
async def get_user_config(user_id: str):
    """Get user configuration"""
    config = await db.user_configs.find_one({"user_id": user_id}, {"_id": 0})
    if not config:
        raise HTTPException(status_code=404, detail="User configuration not found")
    return config


# ============= ADMIN API ENDPOINTS =============

# --- User Management ---
@api_router.get("/admin/users")
async def get_all_users(
    limit: int = 100,
    skip: int = 0,
    search: Optional[str] = None,
    status: Optional[str] = None
):
    """Get all users with optional filtering"""
    try:
        query = {}
        
        # Search by username or telegram_id
        if search:
            query["$or"] = [
                {"telegram_username": {"$regex": search, "$options": "i"}},
                {"first_name": {"$regex": search, "$options": "i"}},
                {"telegram_id": int(search) if search.isdigit() else 0}
            ]
        
        # Filter by subscription status
        if status == "active":
            query["active_subscriptions.0"] = {"$exists": True}
        elif status == "expired":
            query["active_subscriptions"] = []
        
        users = await db.users.find(query, {"_id": 0}).skip(skip).limit(limit).to_list(limit)
        total = await db.users.count_documents(query)
        
        return {
            "users": users,
            "total": total,
            "limit": limit,
            "skip": skip
        }
    except Exception as e:
        logger.error(f"Error fetching users: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/admin/users/{telegram_id}")
async def get_user_details(telegram_id: int):
    """Get detailed user information"""
    try:
        user = await db.users.find_one({"telegram_id": telegram_id}, {"_id": 0})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get user's payment history
        payments = await db.payments.find(
            {"telegram_id": telegram_id},
            {"_id": 0}
        ).sort("created_at", -1).to_list(50)
        
        return {
            "user": user,
            "payments": payments
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user details: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.put("/admin/users/{telegram_id}/subscription")
async def update_user_subscription(telegram_id: int, subscription_data: Dict[str, Any]):
    """Update or extend user subscription"""
    try:
        user = await db.users.find_one({"telegram_id": telegram_id})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        result = await db.users.update_one(
            {"telegram_id": telegram_id},
            {
                "$set": {
                    "active_subscriptions": subscription_data.get("subscriptions", []),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        return {"message": "Subscription updated successfully", "modified": result.modified_count}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating subscription: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.delete("/admin/users/{telegram_id}")
async def delete_user(telegram_id: int):
    """Delete a user"""
    try:
        result = await db.users.delete_one({"telegram_id": telegram_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Also delete user's payments
        await db.payments.delete_many({"telegram_id": telegram_id})
        
        return {"message": "User deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting user: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Payment Management ---
@api_router.get("/admin/payments")
async def get_all_payments(
    limit: int = 100,
    skip: int = 0,
    status: Optional[str] = None
):
    """Get all payments with optional status filter"""
    try:
        query = {}
        if status:
            query["status"] = status
        
        payments = await db.payments.find(query, {"_id": 0}).sort("created_at", -1).skip(skip).limit(limit).to_list(limit)
        total = await db.payments.count_documents(query)
        
        return {
            "payments": payments,
            "total": total,
            "limit": limit,
            "skip": skip
        }
    except Exception as e:
        logger.error(f"Error fetching payments: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.put("/admin/payments/{payment_id}/approve")
async def approve_payment(payment_id: str, admin_notes: Optional[str] = None):
    """Approve a pending payment"""
    try:
        payment = await db.payments.find_one({"payment_id": payment_id})
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        if payment["status"] != "pending":
            raise HTTPException(status_code=400, detail="Payment is not pending")
        
        # Update payment status
        await db.payments.update_one(
            {"payment_id": payment_id},
            {
                "$set": {
                    "status": "verified",
                    "verified_by": "admin",
                    "verification_date": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        # Activate user subscription
        from datetime import timedelta
        user = await db.users.find_one({"telegram_id": payment["telegram_id"]})
        if user:
            # Calculate subscription dates
            start_date = datetime.now(timezone.utc)
            
            # Determine duration based on plan type
            duration_days = 30  # default monthly
            if "weekly" in payment["plan_type"].lower():
                duration_days = 7
            elif "yearly" in payment["plan_type"].lower():
                duration_days = 365
            
            expiry_date = start_date + timedelta(days=duration_days)
            
            new_subscription = {
                "subscription_id": str(uuid.uuid4()),
                "plan_type": payment["plan_type"],
                "platforms": payment["platforms"],
                "amount_paid": payment["amount"],
                "start_date": start_date.isoformat(),
                "expiry_date": expiry_date.isoformat(),
                "is_active": True,
                "payment_id": payment_id
            }
            
            await db.users.update_one(
                {"telegram_id": payment["telegram_id"]},
                {
                    "$push": {"active_subscriptions": new_subscription},
                    "$inc": {"total_spent": payment["amount"]},
                    "$set": {"updated_at": datetime.now(timezone.utc).isoformat()}
                }
            )
        
        return {"message": "Payment approved and subscription activated"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving payment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.put("/admin/payments/{payment_id}/reject")
async def reject_payment(payment_id: str, reason: Optional[str] = None):
    """Reject a pending payment"""
    try:
        payment = await db.payments.find_one({"payment_id": payment_id})
        if not payment:
            raise HTTPException(status_code=404, detail="Payment not found")
        
        if payment["status"] != "pending":
            raise HTTPException(status_code=400, detail="Payment is not pending")
        
        await db.payments.update_one(
            {"payment_id": payment_id},
            {
                "$set": {
                    "status": "rejected",
                    "rejection_reason": reason or "Payment verification failed",
                    "verified_by": "admin",
                    "verification_date": datetime.now(timezone.utc).isoformat(),
                    "updated_at": datetime.now(timezone.utc).isoformat()
                }
            }
        )
        
        return {"message": "Payment rejected"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error rejecting payment: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Statistics ---
@api_router.get("/admin/statistics")
async def get_admin_statistics():
    """Get dashboard statistics"""
    try:
        # Total users
        total_users = await db.users.count_documents({})
        
        # Active subscriptions (users with at least one active subscription)
        active_users = await db.users.count_documents({
            "active_subscriptions.0": {"$exists": True}
        })
        
        # Total revenue
        revenue_result = await db.payments.aggregate([
            {"$match": {"status": "verified"}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]).to_list(1)
        total_revenue = revenue_result[0]["total"] if revenue_result else 0
        
        # Pending payments
        pending_payments = await db.payments.count_documents({"status": "pending"})
        
        # Revenue by plan type
        revenue_by_plan = await db.payments.aggregate([
            {"$match": {"status": "verified"}},
            {"$group": {"_id": "$plan_type", "total": {"$sum": "$amount"}, "count": {"$sum": 1}}}
        ]).to_list(10)
        
        # Recent user registrations (last 7 days)
        from datetime import timedelta
        seven_days_ago = datetime.now(timezone.utc) - timedelta(days=7)
        new_users_week = await db.users.count_documents({
            "created_at": {"$gte": seven_days_ago.isoformat()}
        })
        
        # Platform usage stats
        platform_stats = {}
        users = await db.users.find({}, {"active_subscriptions": 1, "_id": 0}).to_list(1000)
        for user in users:
            for sub in user.get("active_subscriptions", []):
                for platform in sub.get("platforms", []):
                    platform_stats[platform] = platform_stats.get(platform, 0) + 1
        
        # Top platforms
        top_platforms = sorted(platform_stats.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_revenue": total_revenue,
            "pending_payments": pending_payments,
            "new_users_this_week": new_users_week,
            "revenue_by_plan": revenue_by_plan,
            "top_platforms": [{"platform": p[0], "users": p[1]} for p in top_platforms]
        }
    except Exception as e:
        logger.error(f"Error fetching statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# --- Broadcast Messaging ---
class BroadcastMessage(BaseModel):
    message: str
    target: str = "all"  # all, active, expired
    telegram_ids: Optional[List[int]] = None


@api_router.post("/admin/broadcast")
async def send_broadcast(broadcast: BroadcastMessage):
    """Send broadcast message to users"""
    try:
        # Determine target users
        query = {}
        if broadcast.target == "active":
            query["active_subscriptions.0"] = {"$exists": True}
        elif broadcast.target == "expired":
            query["active_subscriptions"] = []
        elif broadcast.target == "custom" and broadcast.telegram_ids:
            query["telegram_id"] = {"$in": broadcast.telegram_ids}
        
        users = await db.users.find(query, {"telegram_id": 1, "_id": 0}).to_list(10000)
        telegram_ids = [user["telegram_id"] for user in users]
        
        # Store broadcast in database
        broadcast_doc = {
            "broadcast_id": str(uuid.uuid4()),
            "message": broadcast.message,
            "target": broadcast.target,
            "recipient_count": len(telegram_ids),
            "telegram_ids": telegram_ids,
            "status": "queued",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        await db.broadcasts.insert_one(broadcast_doc)
        
        # In real implementation, the Telegram bot would process this
        # For now, we just queue it
        return {
            "message": "Broadcast queued successfully",
            "recipient_count": len(telegram_ids),
            "broadcast_id": broadcast_doc["broadcast_id"]
        }
    except Exception as e:
        logger.error(f"Error sending broadcast: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@api_router.get("/admin/broadcasts")
async def get_broadcasts(limit: int = 50):
    """Get broadcast history"""
    try:
        broadcasts = await db.broadcasts.find({}, {"_id": 0}).sort("created_at", -1).limit(limit).to_list(limit)
        return {"broadcasts": broadcasts}
    except Exception as e:
        logger.error(f"Error fetching broadcasts: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= TELEGRAM OTT BOT =============
try:
    from src.services.telegram.bot_enhanced import EnhancedOTTBot
    TELEGRAM_BOT_AVAILABLE = True
except ImportError as e:
    logger.warning(f"Telegram OTT bot service not available: {e}")
    TELEGRAM_BOT_AVAILABLE = False
    EnhancedOTTBot = None

ott_bot = None

@app.on_event("startup")
async def startup_event():
    global ott_bot
    
    # Check MongoDB connection status
    logger.info("\n" + "="*70)
    logger.info("🔍 CHECKING MONGODB CONNECTION STATUS...")
    logger.info("="*70)
    
    try:
        await client.admin.command('ping')
        logger.info("✅ MongoDB connected successfully")
        logger.info(f"   Database: {os.environ.get('DB_NAME', 'unknown')}")
        logger.info(f"   Connection: Active")
    except Exception as e:
        logger.error("❌ Failed to connect MongoDB")
        logger.error(f"   Error: {str(e)}")
        logger.error(f"   Database: {os.environ.get('DB_NAME', 'unknown')}")
    
    logger.info("="*70 + "\n")
    
    if not TELEGRAM_BOT_AVAILABLE:
        logger.warning("⚠️ Telegram bot service not available. Install with: pip install python-telegram-bot")
        return
    
    # Try BOT_TOKEN first, then TELEGRAM_BOT_TOKEN
    telegram_token = os.environ.get('BOT_TOKEN') or os.environ.get('TELEGRAM_BOT_TOKEN')
    admin_upi_id = os.environ.get('ADMIN_UPI_ID', 'kolashankar113@oksbi')
    
    if telegram_token and telegram_token not in ['', 'your_bot_token_here']:
        try:
            logger.info("🤖 Starting Enhanced OTT Bot with Premium Features...")
            
            # Import config
            sys.path.append('/app/backend')
            import config as bot_config
            
            ott_bot = EnhancedOTTBot(
                token=telegram_token,
                mongo_url=bot_config.DATABASE_URI,
                db_name=bot_config.DATABASE_NAME,
                admin_upi_id=admin_upi_id
            )
            asyncio.create_task(ott_bot.run())
            logger.info("✅ Enhanced OTT Bot started successfully!")
            logger.info(f"   - Premium Mode: {bot_config.PREMIUM_AND_REFERAL_MODE}")
            logger.info(f"   - Auto Approve: {bot_config.AUTO_APPROVE_MODE}")
            logger.info(f"   - Force Subscribe: {'Enabled' if bot_config.AUTH_CHANNEL else 'Disabled'}")
        except Exception as e:
            logger.error(f"❌ Failed to start Enhanced OTT Bot: {e}")
            import traceback
            logger.error(traceback.format_exc())
    else:
        logger.warning("⚠️ Telegram bot token not configured. Bot will not start.")
        logger.info("💡 Set BOT_TOKEN or TELEGRAM_BOT_TOKEN in .env to enable the bot")

@app.on_event("shutdown")
async def shutdown_event():
    global ott_bot
    if ott_bot and hasattr(ott_bot, 'application'):
        try:
            await ott_bot.application.stop()
            await ott_bot.application.shutdown()
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
    if ott_bot and hasattr(ott_bot, 'mongo_client'):
        ott_bot.mongo_client.close()
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)