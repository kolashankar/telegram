"""
Enhanced OTT Bot with Premium Features
Integrates force subscribe, premium/referral system, IMDB, and more
"""
import sys
sys.path.append('/app/backend')

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timedelta
import uuid
import config

# Import services
from src.services.referral.referral_service import ReferralService
from src.services.imdb.imdb_service import IMDBService
from src.services.telegram.force_subscribe import ForceSubscribeService
from src.services.telegram.bot_premium import PremiumHandlers
from src.services.telegram.bot_new import OTTBot as BaseOTTBot

logger = logging.getLogger(__name__)

class EnhancedOTTBot(BaseOTTBot, PremiumHandlers):
    """Enhanced OTT Bot with all premium features"""
    
    def __init__(self, token, mongo_url, db_name, admin_upi_id):
        # Initialize base bot
        super().__init__(token, mongo_url, db_name, admin_upi_id)
        
        # Initialize services that don't need database
        self.imdb_service = IMDBService()
        self.force_sub_service = None  # Will be initialized after setup
        self.referral_service = None   # Will be initialized in initialize_db
        
        # User sessions
        self.user_sessions = {}
        
        logger.info("Enhanced OTT Bot initialized")
        
    async def initialize_db(self):
        """Initialize database and dependent services"""
        # First initialize the database in the parent class
        await super().initialize_db()
        
        # Now that db is initialized, we can create services that depend on it
        self.referral_service = ReferralService(self.db)
        logger.info("Referral service initialized")
        
    async def run(self):
        """Run the enhanced OTT bot"""
        # Initialize database and services
        await self.initialize_db()
        
        # Setup handlers
        self.setup_handlers()
        
        # Start the bot
        logger.info("Starting Enhanced OTT Bot...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        # Keep running
        import asyncio
        await asyncio.Future()  # Run forever
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced start command with force subscribe and referrals"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        first_name = update.effective_user.first_name or "User"
        
        # Initialize force subscribe service
        if not self.force_sub_service:
            self.force_sub_service = ForceSubscribeService(self)
        
        # Check force subscribe
        if config.AUTH_CHANNEL:
            is_subscribed = await self.force_sub_service.handle_force_subscribe(
                update, context, "check_subscription"
            )
            if not is_subscribed:
                return
        
        # Check for referral code in start parameter
        if context.args and len(context.args) > 0:
            referral_code = context.args[0]
            
            # Find referrer
            referrer_id = await self.referral_service.find_user_by_referral_code(referral_code)
            
            if referrer_id and referrer_id != user_id:
                # Add referral
                success = await self.referral_service.add_referral(
                    referrer_telegram_id=referrer_id,
                    referred_telegram_id=user_id,
                    referred_username=username
                )
                
                if success:
                    # Notify referrer
                    try:
                        await context.bot.send_message(
                            chat_id=referrer_id,
                            text=f"🎉 New referral! @{username} joined using your link!\n\n"
                                 f"Keep sharing to earn free premium!"
                        )
                    except:
                        pass
        
        # Register or update user
        user_data = {
            "telegram_id": user_id,
            "telegram_username": username,
            "first_name": first_name,
            "last_name": update.effective_user.last_name or "",
            "user_id": str(user_id),
            "active_subscriptions": [],
            "total_spent": 0,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "last_interaction": datetime.utcnow().isoformat()
        }
        
        await self.users_collection.update_one(
            {"telegram_id": user_id},
            {"$set": user_data},
            upsert=True
        )
        
        # Validate referral if exists
        await self.referral_service.validate_referral(user_id)
        
        # Send welcome message with image
        welcome_text = f"""
🎬 <b>Welcome to {config.SESSION}!</b>

Hello {first_name}! 👋

Your ultimate destination for <b>unlimited OTT content</b> access!

<b>🌟 What we offer:</b>
✓ Access to 30+ OTT platforms
✓ Latest movies and series
✓ Multiple quality options
✓ Premium subscriptions
✓ Referral rewards

<b>💎 Premium Benefits:</b>
• Unlimited streaming
• No ads or verification
• High-speed access
• Priority support

<i>Click the menu button below to get started!</i>
"""
        
        keyboard = [
            [
                InlineKeyboardButton("🎬 Explore OTT", callback_data="ott_explorer"),
                InlineKeyboardButton("💎 Premium", callback_data="premium_menu")
            ],
            [
                InlineKeyboardButton("📊 Dashboard", callback_data="dashboard"),
                InlineKeyboardButton("⚙️ Settings", callback_data="settings")
            ],
            [
                InlineKeyboardButton("👥 Referrals", callback_data="referral_program"),
                InlineKeyboardButton("❓ Help", callback_data="help_menu")
            ]
        ]
        
        markup = InlineKeyboardMarkup(keyboard)
        
        try:
            # Send with welcome image
            await context.bot.send_photo(
                chat_id=user_id,
                photo=config.PICS[0] if config.PICS else config.NOR_IMG,
                caption=welcome_text,
                reply_markup=markup,
                parse_mode="HTML"
            )
        except Exception as e:
            logger.error(f"Error sending welcome photo: {e}")
            # Fallback to text message
            await update.message.reply_text(
                welcome_text,
                reply_markup=markup,
                parse_mode="HTML"
            )
        
        # Log to channel
        if config.LOG_CHANNEL and config.MELCOW_NEW_USERS:
            try:
                await context.bot.send_message(
                    chat_id=config.LOG_CHANNEL,
                    text=f"#NewUser\n\nUser: @{username}\nID: {user_id}\nName: {first_name}"
                )
            except:
                pass
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Enhanced callback query handler"""
        query = update.callback_query
        await query.answer()
        
        data = query.data
        
        # Force subscribe check for protected actions
        if config.AUTH_CHANNEL and data not in ["check_subscription"]:
            if not self.force_sub_service:
                self.force_sub_service = ForceSubscribeService(self)
            
            is_subscribed = await self.force_sub_service.handle_force_subscribe(
                update, context, data
            )
            if not is_subscribed:
                return
        
        # Handle callbacks
        if data == "check_subscription":
            await self.start_command(update, context)
        
        elif data == "main_menu":
            await self.start_command(update, context)
        
        elif data == "premium_menu":
            await self.premium_menu(update, context)
        
        elif data == "show_premium_plans":
            await self.show_premium_plans(update, context)
        
        elif data.startswith("buy_premium_"):
            plan_id = data.replace("buy_premium_", "")
            await self.buy_premium_plan(update, context, plan_id)
        
        elif data == "referral_program":
            await self.referral_program(update, context)
        
        elif data == "my_referrals":
            await self.my_referrals_list(update, context)
        
        elif data == "claim_referral_reward":
            await self.claim_referral_reward(update, context)
        
        elif data == "copy_referral":
            stats = await self.referral_service.get_or_create_referral_stats(update.effective_user.id)
            referral_code = stats.get("referral_code", "N/A")
            bot_username = context.bot.username
            referral_link = f"https://t.me/{bot_username}?start={referral_code}"
            await query.answer(f"Link: {referral_link}", show_alert=True)
        
        elif data == "ott_explorer":
            await self.show_ott_explorer_menu(update.callback_query)
        
        elif data == "dashboard":
            await self.show_dashboard_menu(update.callback_query)
        
        elif data == "settings":
            await self.show_settings_menu(update.callback_query)
        
        elif data == "help_menu":
            await self.help_menu(update, context)
        
        else:
            # Try base bot handler
            await super().button_callback(update, context)
    
    async def help_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help menu"""
        help_text = f"""
❓ <b>Help & Support</b>

<b>Available Commands:</b>
/start - Start the bot
/menu - Show main menu
/myplan - View your subscription
/help - Show this help message

<b>📞 Contact Support:</b>
• Join our group: {config.GRP_LNK}
• Follow our channel: {config.CHNL_LNK}
• Contact admin: @{config.OWNER_USERNAME}

<b>📺 Tutorial:</b>
{config.TUTORIAL}

<b>Need Help?</b>
Feel free to reach out to our support team!
"""
        
        keyboard = [
            [InlineKeyboardButton("📱 Join Group", url=config.GRP_LNK)],
            [InlineKeyboardButton("📢 Join Channel", url=config.CHNL_LNK)],
            [InlineKeyboardButton("📺 Tutorial", url=config.TUTORIAL)],
            [InlineKeyboardButton("« Back", callback_data="main_menu")]
        ]
        
        markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            try:
                await update.callback_query.edit_message_text(
                    help_text,
                    reply_markup=markup,
                    parse_mode="HTML"
                )
            except Exception as e:
                # If editing fails (e.g., message has photo), send new message
                await update.callback_query.message.reply_text(
                    help_text,
                    reply_markup=markup,
                    parse_mode="HTML"
                )
        else:
            await update.message.reply_text(
                help_text,
                reply_markup=markup,
                parse_mode="HTML"
            )
    
    async def handle_photo_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo messages (payment screenshots)"""
        user_id = update.effective_user.id
        
        # Check if user is awaiting payment screenshot
        user_data = context.user_data if hasattr(context, 'user_data') else {}
        
        if user_data.get('awaiting_payment_screenshot'):
            payment_id = user_data.get('payment_id')
            
            if not payment_id:
                await update.message.reply_text("Error: Payment ID not found.")
                return
            
            # Get photo file
            photo = update.message.photo[-1]  # Highest resolution
            file_id = photo.file_id
            
            # Update payment with screenshot
            result = await self.payments_collection.update_one(
                {"payment_id": payment_id},
                {
                    "$set": {
                        "screenshot_file_id": file_id,
                        "screenshot_uploaded_at": datetime.utcnow().isoformat(),
                        "status": "pending",
                        "updated_at": datetime.utcnow().isoformat()
                    }
                }
            )
            
            if result.modified_count > 0:
                await update.message.reply_text(
                    "✅ <b>Payment Screenshot Received!</b>\n\n"
                    "Your payment is now pending admin verification.\n"
                    "You'll be notified once approved (usually within 1-2 hours).\n\n"
                    f"Payment ID: <code>{payment_id[:8]}</code>",
                    parse_mode="HTML"
                )
                
                # Clear session
                user_data['awaiting_payment_screenshot'] = False
                user_data['payment_id'] = None
                
                # Notify admins
                await self.notify_admins_payment(payment_id, context, file_id)
            else:
                await update.message.reply_text(
                    "❌ Failed to upload screenshot. Please try again."
                )
        else:
            await update.message.reply_text(
                "Please use the Premium menu to initiate a payment first."
            )
    
    async def notify_admins_payment(self, payment_id: str, context, screenshot_file_id: str):
        """Notify admins about new payment"""
        payment = await self.payments_collection.find_one({"payment_id": payment_id})
        
        if not payment:
            return
        
        message = f"""
💰 <b>New Payment Received</b>

<b>Payment ID:</b> <code>{payment_id[:8]}</code>
<b>Amount:</b> ₹{payment['amount']}
<b>Plan:</b> {payment['plan_name']}
<b>User:</b> @{payment['telegram_username']} ({payment['telegram_id']})

Screenshot uploaded ✅

<b>Actions:</b>
• Approve: <code>/approve {payment_id}</code>
• Reject: <code>/reject {payment_id} [reason]</code>
"""
        
        for admin_id in config.ADMINS:
            try:
                await context.bot.send_photo(
                    chat_id=admin_id,
                    photo=screenshot_file_id,
                    caption=message,
                    parse_mode="HTML"
                )
            except Exception as e:
                logger.error(f"Failed to notify admin {admin_id}: {e}")
        
        # Also log to channel
        if config.LOG_CHANNEL:
            try:
                await context.bot.send_photo(
                    chat_id=config.LOG_CHANNEL,
                    photo=screenshot_file_id,
                    caption=message,
                    parse_mode="HTML"
                )
            except:
                pass
    
    def setup_handlers(self):
        """Setup all bot handlers"""
        self.application = Application.builder().token(self.token).build()
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_menu))
        self.application.add_handler(CommandHandler("menu", self.start_command))
        self.application.add_handler(CommandHandler("myplan", self.myplan_command))
        
        # Callback query handler
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Photo handler (for payment screenshots)
        self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo_message))
        
        # Text message handler
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_text_message
        ))
        
        logger.info("All handlers registered")
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        text = update.message.text
        user_id = update.effective_user.id
        
        # Admin commands
        if text.startswith("/approve ") and user_id in config.ADMINS:
            parts = text.split()
            if len(parts) >= 2:
                payment_id = parts[1]
                await self.approve_payment_admin(update, context, payment_id)
        
        elif text.startswith("/reject ") and user_id in config.ADMINS:
            parts = text.split(maxsplit=2)
            if len(parts) >= 2:
                payment_id = parts[1]
                reason = parts[2] if len(parts) > 2 else "Payment verification failed"
                await self.reject_payment_admin(update, context, payment_id, reason)
        
        else:
            # Show help
            await update.message.reply_text(
                "Use /menu to see available options!",
                parse_mode="HTML"
            )
    
    async def approve_payment_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE, payment_id: str):
        """Admin approves payment"""
        payment = await self.payments_collection.find_one({"payment_id": payment_id})
        
        if not payment:
            await update.message.reply_text("Payment not found!")
            return
        
        # Get plan details
        plan_id = payment.get("plan_type")
        plan = config.PREMIUM_PLANS.get(plan_id)
        
        if not plan:
            await update.message.reply_text("Invalid plan!")
            return
        
        # Update payment status
        await self.payments_collection.update_one(
            {"payment_id": payment_id},
            {
                "$set": {
                    "status": "verified",
                    "verified_by": update.effective_user.id,
                    "verified_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        # Activate premium for user
        start_date = datetime.utcnow()
        expiry_date = start_date + timedelta(days=plan["duration_days"])
        
        await self.users_collection.update_one(
            {"telegram_id": payment["telegram_id"]},
            {
                "$set": {
                    "premium_subscription": {
                        "plan_type": plan_id,
                        "plan_name": plan["name"],
                        "start_date": start_date.isoformat(),
                        "expiry_date": expiry_date.isoformat(),
                        "is_active": True,
                        "payment_id": payment_id
                    },
                    "updated_at": datetime.utcnow().isoformat()
                },
                "$inc": {"total_spent": payment["amount"]}
            }
        )
        
        # Notify user
        try:
            await context.bot.send_message(
                chat_id=payment["telegram_id"],
                text=f"🎉 <b>Payment Approved!</b>\n\n"
                     f"Your {plan['name']} has been activated!\n"
                     f"Amount: ₹{payment['amount']}\n"
                     f"Valid until: {expiry_date.strftime('%d %b %Y')}\n\n"
                     f"Enjoy unlimited access! 💎",
                parse_mode="HTML"
            )
        except:
            pass
        
        await update.message.reply_text(
            f"✅ Payment approved! Premium activated for user {payment['telegram_id']}"
        )
    
    async def reject_payment_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE, payment_id: str, reason: str):
        """Admin rejects payment"""
        payment = await self.payments_collection.find_one({"payment_id": payment_id})
        
        if not payment:
            await update.message.reply_text("Payment not found!")
            return
        
        # Update payment status
        await self.payments_collection.update_one(
            {"payment_id": payment_id},
            {
                "$set": {
                    "status": "rejected",
                    "rejection_reason": reason,
                    "verified_by": update.effective_user.id,
                    "verified_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
            }
        )
        
        # Notify user
        try:
            await context.bot.send_message(
                chat_id=payment["telegram_id"],
                text=f"❌ <b>Payment Rejected</b>\n\n"
                     f"Reason: {reason}\n\n"
                     f"Please contact support @{config.OWNER_USERNAME} for assistance.",
                parse_mode="HTML"
            )
        except:
            pass
        
        await update.message.reply_text(
            f"❌ Payment rejected. User notified."
        )


# Standalone bot runner
async def start_enhanced_bot():
    """Start the enhanced OTT bot"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    token = os.getenv("BOT_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN", "")
    mongo_url = config.DATABASE_URI
    db_name = config.DATABASE_NAME
    admin_upi_id = "kolashankar113@oksbi"
    
    if not token or token == "your_bot_token_here":
        logger.error("Please set BOT_TOKEN or TELEGRAM_BOT_TOKEN in .env file")
        return
    
    bot = EnhancedOTTBot(token, mongo_url, db_name, admin_upi_id)
    await bot.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(start_enhanced_bot())
