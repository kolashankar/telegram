"""
Telegram Bot for OTT Subscription Management
Multi-user bot with 8 main features and admin panel
"""
import os
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio

from .keyboards import (
    get_main_menu_keyboard,
    get_ott_explorer_keyboard,
    get_compare_plans_keyboard,
    get_release_alerts_keyboard,
    get_dashboard_keyboard,
    get_subscriptions_keyboard,
    get_admin_panel_keyboard,
    get_settings_keyboard,
    get_help_keyboard,
    get_payment_confirmation_keyboard,
    get_back_button
)
from ...models.user import User, UserPreferences, UserSubscription
from ...models.payment import Payment
from ...models.admin import Admin
from ...services.ott.platform_data import get_all_platforms, get_platform_by_name
from ...services.payment.payment_service import PaymentService

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global state for user sessions
user_sessions: Dict[int, Dict[str, Any]] = {}


class OTTBot:
    """Main OTT Subscription Bot class"""
    
    def __init__(self, token: str, mongo_url: str, db_name: str, admin_upi_id: str = "admin@upi"):
        self.token = token
        self.mongo_url = mongo_url
        self.db_name = db_name
        self.admin_upi_id = admin_upi_id
        
        # Database connections
        self.mongo_client = None
        self.db = None
        self.users_collection = None
        self.payments_collection = None
        self.admins_collection = None
        self.watchlists_collection = None
        self.alerts_collection = None
        
        # Services
        self.payment_service = None
        
        # Bot application
        self.application = None
    
    async def initialize_db(self):
        """Initialize database connections"""
        self.mongo_client = AsyncIOMotorClient(self.mongo_url)
        self.db = self.mongo_client[self.db_name]
        
        # Collections
        self.users_collection = self.db["users"]
        self.payments_collection = self.db["payments"]
        self.admins_collection = self.db["admins"]
        self.watchlists_collection = self.db["watchlists"]
        self.alerts_collection = self.db["release_alerts"]
        self.platforms_collection = self.db["ott_platforms"]
        
        # Initialize services
        self.payment_service = PaymentService(self.db, self.admin_upi_id)
        
        # Clean up any documents with null telegram_id before creating index
        try:
            # Drop any existing index that might cause conflicts
            await self.users_collection.drop_index("telegram_id_1")
        except Exception as e:
            logger.debug(f"No existing telegram_id index to drop: {e}")
            
        # Remove or update documents with null telegram_id
        result = await self.users_collection.delete_many({"telegram_id": None})
        if result.deleted_count > 0:
            logger.warning(f"Removed {result.deleted_count} users with null telegram_id")
        
        # Create indexes
        try:
            await self.users_collection.create_index("telegram_id", unique=True, sparse=True)
            logger.info("Created unique index on telegram_id (sparse)")
        except Exception as e:
            logger.error(f"Failed to create telegram_id index: {e}")
            # If sparse index fails, try with partial filter
            try:
                await self.users_collection.create_index(
                    [("telegram_id", 1)],
                    unique=True,
                    partialFilterExpression={"telegram_id": {"$exists": True}}
                )
                logger.info("Created unique index on telegram_id with partial filter")
            except Exception as e2:
                logger.error(f"Failed to create partial index: {e2}")
                raise
                
        # Create other indexes
        await self.admins_collection.create_index("telegram_id", unique=True)
        await self.payments_collection.create_index("payment_id", unique=True)
        
        logger.info("Database initialized successfully")
    
    async def get_or_create_user(self, telegram_id: int, first_name: str = None, 
                                last_name: str = None, username: str = None) -> User:
        """Get existing user or create new one"""
        user_data = await self.users_collection.find_one({"telegram_id": telegram_id})
        
        if user_data:
            return User(**user_data)
        
        # Create new user
        user = User(
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            telegram_username=username
        )
        
        await self.users_collection.insert_one(user.model_dump())
        logger.info(f"Created new user: {telegram_id}")
        return user
    
    async def is_admin(self, telegram_id: int) -> bool:
        """Check if user is admin"""
        admin_data = await self.admins_collection.find_one({"telegram_id": telegram_id, "is_active": True})
        return admin_data is not None
    
    async def update_user_activity(self, telegram_id: int):
        """Update user's last active timestamp"""
        await self.users_collection.update_one(
            {"telegram_id": telegram_id},
            {"$set": {"last_active": datetime.utcnow()}}
        )
    
    # ================== COMMAND HANDLERS ==================
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        await self.get_or_create_user(user.id, user.first_name, user.last_name, user.username)
        await self.update_user_activity(user.id)
        
        welcome_text = f"""
🎬 **Welcome to OTT Subscription Manager** 🎬

Hello {user.first_name}! 👋

I help you manage OTT subscriptions across 30+ platforms!

**What I can do:**
🎬 Browse latest movies & shows
💰 Compare subscription plans
🔔 Get release alerts
📊 Track your subscriptions
💵 Manage payments via UPI
👑 Admin panel (for admins)

Choose an option below to get started:
"""
        
        await update.message.reply_text(
            welcome_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
📖 **Bot Commands & Features**

**Main Menu Options:**
🎬 **OTT Explorer** - Browse content across platforms
💰 **Compare Plans** - Compare OTT subscription prices
🔔 **Release Alerts** - Get notified about new releases
📊 **Dashboard** - View your subscription status
💵 **Subscriptions** - Purchase subscription plans
👑 **Admin Panel** - Manage users & payments (admins only)
⚙️ **Settings** - Customize preferences
🆘 **Help & Support** - Get assistance

**How to Subscribe:**
1. Choose "Subscriptions" from menu
2. Select a plan (Weekly/Monthly/Custom)
3. Pay via UPI using QR code
4. Upload payment screenshot
5. Admin will verify and activate

**Need Help?**
Use /help or tap "Help & Support" in menu
"""
        
        await update.message.reply_text(
            help_text,
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )
    
    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /menu command"""
        await update.message.reply_text(
            "🎯 **Main Menu**\n\nSelect an option:",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )
    
    # ================== CALLBACK QUERY HANDLERS ==================
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        await self.update_user_activity(user.id)
        
        callback_data = query.data
        
        # Main menu navigation
        if callback_data == "back_to_menu":
            await self.show_main_menu(query)
        
        # Menu options
        elif callback_data == "menu_ott_explorer":
            await self.show_ott_explorer_menu(query)
        elif callback_data == "menu_compare_plans":
            await self.show_compare_plans_menu(query)
        elif callback_data == "menu_release_alerts":
            await self.show_release_alerts_menu(query)
        elif callback_data == "menu_dashboard":
            await self.show_dashboard_menu(query)
        elif callback_data == "menu_subscriptions":
            await self.show_subscriptions_menu(query)
        elif callback_data == "menu_admin":
            await self.show_admin_menu(query)
        elif callback_data == "menu_settings":
            await self.show_settings_menu(query)
        elif callback_data == "menu_help":
            await self.show_help_menu(query)
        
        # OTT Explorer features
        elif callback_data == "ott_browse":
            await self.handle_ott_browse(query)
        elif callback_data == "ott_filter":
            await self.handle_ott_filter(query)
        elif callback_data == "ott_availability":
            await self.handle_ott_availability(query)
        elif callback_data == "ott_trailers":
            await self.handle_ott_trailers(query)
        elif callback_data == "ott_watchlist":
            await self.handle_ott_watchlist(query)
        
        # Compare Plans features
        elif callback_data == "compare_all":
            await self.handle_compare_all(query)
        elif callback_data == "compare_offers":
            await self.handle_compare_offers(query)
        elif callback_data == "compare_filter":
            await self.handle_compare_filter(query)
        elif callback_data == "compare_best":
            await self.handle_compare_best(query)
        elif callback_data == "compare_history":
            await self.handle_compare_history(query)
        
        # Release Alerts features
        elif callback_data == "alerts_subscribe":
            await self.handle_alerts_subscribe(query)
        elif callback_data == "alerts_frequency":
            await self.handle_alerts_frequency(query)
        elif callback_data == "alerts_timing":
            await self.handle_alerts_timing(query)
        elif callback_data == "alerts_trending":
            await self.handle_alerts_trending(query)
        elif callback_data == "alerts_my":
            await self.handle_alerts_my(query)
        
        # Dashboard features
        elif callback_data == "dash_expiry":
            await self.handle_dash_expiry(query)
        elif callback_data == "dash_spent":
            await self.handle_dash_spent(query)
        elif callback_data == "dash_reminders":
            await self.handle_dash_reminders(query)
        elif callback_data == "dash_watchlist":
            await self.handle_dash_watchlist(query)
        elif callback_data == "dash_export":
            await self.handle_dash_export(query)
        
        # Subscription features
        elif callback_data == "sub_weekly":
            await self.handle_subscription_plan(query, "weekly")
        elif callback_data == "sub_monthly":
            await self.handle_subscription_plan(query, "monthly")
        elif callback_data == "sub_custom":
            await self.handle_subscription_custom(query)
        elif callback_data == "sub_active":
            await self.handle_active_subscriptions(query)
        
        # Admin features
        elif callback_data == "admin_platforms":
            await self.handle_admin_platforms(query)
        elif callback_data == "admin_users":
            await self.handle_admin_users(query)
        elif callback_data == "admin_verify":
            await self.handle_admin_verify_payments(query)
        elif callback_data == "admin_announce":
            await self.handle_admin_announce(query)
        elif callback_data == "admin_reports":
            await self.handle_admin_reports(query)
        
        # Settings features
        elif callback_data == "settings_region":
            await self.handle_settings_region(query)
        elif callback_data == "settings_preferences":
            await self.handle_settings_preferences(query)
        elif callback_data == "settings_notifications":
            await self.handle_settings_notifications(query)
        elif callback_data == "settings_devices":
            await self.handle_settings_devices(query)
        elif callback_data == "settings_delete":
            await self.handle_settings_delete(query)
        
        # Help features
        elif callback_data == "help_faq":
            await self.handle_help_faq(query)
        elif callback_data == "help_contact":
            await self.handle_help_contact(query)
        elif callback_data == "help_report":
            await self.handle_help_report(query)
        elif callback_data == "help_terms":
            await self.handle_help_terms(query)
        
        # Payment callbacks
        elif callback_data.startswith("payment_upload_"):
            payment_id = callback_data.replace("payment_upload_", "")
            await self.handle_payment_screenshot_request(query, payment_id)
        elif callback_data == "payment_cancel":
            await self.handle_payment_cancel(query)
    
    # ================== MENU DISPLAY FUNCTIONS ==================
    
    async def show_main_menu(self, query):
        """Show main menu"""
        await query.edit_message_text(
            "🎯 **Main Menu**\n\nSelect an option:",
            reply_markup=get_main_menu_keyboard(),
            parse_mode="Markdown"
        )
    
    async def show_ott_explorer_menu(self, query):
        """Show OTT Explorer submenu"""
        text = """
🎬 **OTT Explorer**

Browse movies and shows across 30+ OTT platforms!

**Features:**
• Browse latest releases
• Filter by genre, language, release date
• Check platform availability
• Watch trailers
• Manage your watchlist
"""
        try:
            await query.edit_message_text(
                text,
                reply_markup=get_ott_explorer_keyboard(),
                parse_mode="Markdown"
            )
        except Exception as e:
            # If editing fails (e.g., message has photo), send new message
            await query.message.reply_text(
                text,
                reply_markup=get_ott_explorer_keyboard(),
                parse_mode="Markdown"
            )
    
    async def show_compare_plans_menu(self, query):
        """Show Compare Plans submenu"""
        text = """
💰 **Compare Plans**

Compare subscription costs and find the best deals!

**Features:**
• Compare all OTT platforms
• View active offers and discounts
• Filter by plan type (monthly, yearly, mobile, family)
• Get personalized recommendations
• View price history
"""
        await query.edit_message_text(
            text,
            reply_markup=get_compare_plans_keyboard(),
            parse_mode="Markdown"
        )
    
    async def show_release_alerts_menu(self, query):
        """Show Release Alerts submenu"""
        text = """
🔔 **Release Alerts**

Stay updated with latest releases!

**Features:**
• Subscribe to genre/platform alerts
• Set notification frequency
• Customize alert timing
• View trending releases
• Manage your alert preferences
"""
        await query.edit_message_text(
            text,
            reply_markup=get_release_alerts_keyboard(),
            parse_mode="Markdown"
        )
    
    async def show_dashboard_menu(self, query):
        """Show Dashboard submenu"""
        text = """
📊 **User Dashboard**

Track your subscriptions and activity!

**Features:**
• View subscription expiry dates
• Track money spent
• Set renewal reminders
• View watchlist & history
• Export your data to PDF
"""
        try:
            await query.edit_message_text(
                text,
                reply_markup=get_dashboard_keyboard(),
                parse_mode="Markdown"
            )
        except Exception as e:
            # If editing fails (e.g., message has photo), send new message
            await query.message.reply_text(
                text,
                reply_markup=get_dashboard_keyboard(),
                parse_mode="Markdown"
            )
    
    async def show_subscriptions_menu(self, query):
        """Show Subscriptions submenu"""
        text = """
💵 **Subscriptions**

Choose a subscription plan:

**Available Plans:**
• Weekly Plan - Access to select platforms
• Monthly Plan - Full access to all platforms
• Custom Bundle - Choose your own platforms

After selecting a plan, you'll receive a UPI QR code for payment.
"""
        await query.edit_message_text(
            text,
            reply_markup=get_subscriptions_keyboard(),
            parse_mode="Markdown"
        )
    
    async def show_admin_menu(self, query):
        """Show Admin Panel submenu"""
        user_id = query.from_user.id
        is_admin = await self.is_admin(user_id)
        
        if not is_admin:
            await query.edit_message_text(
                "🚫 **Access Denied**\n\nYou don't have admin privileges.\n\nTo become an admin, contact the bot owner.",
                reply_markup=get_back_button(),
                parse_mode="Markdown"
            )
            return
        
        text = """
👑 **Admin Panel**

Manage the bot and users:

**Features:**
• Add/remove OTT platforms
• Manage users and subscriptions
• Verify pending payments
• Send announcements to all users
• Generate revenue reports
"""
        await query.edit_message_text(
            text,
            reply_markup=get_admin_panel_keyboard(),
            parse_mode="Markdown"
        )
    
    async def show_settings_menu(self, query):
        """Show Settings submenu"""
        text = """
⚙️ **Settings**

Customize your experience:

**Options:**
• Choose OTT region (India, Global, etc.)
• Set default genres and languages
• Manage notification preferences
• View connected devices
• Delete account & data
"""
        try:
            await query.edit_message_text(
                text,
                reply_markup=get_settings_keyboard(),
                parse_mode="Markdown"
            )
        except Exception as e:
            # If editing fails (e.g., message has photo), send new message
            await query.message.reply_text(
                text,
                reply_markup=get_settings_keyboard(),
                parse_mode="Markdown"
            )
    
    async def show_help_menu(self, query):
        """Show Help & Support submenu"""
        text = """
🆘 **Help & Support**

Need assistance? We're here to help!

**Resources:**
• Frequently Asked Questions (FAQs)
• Contact admin directly
• Report issues or request refunds
• Join community group
• Read terms of service & privacy policy
"""
        await query.edit_message_text(
            text,
            reply_markup=get_help_keyboard(),
            parse_mode="Markdown"
        )
