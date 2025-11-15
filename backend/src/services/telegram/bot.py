"""
Integrated OTT Subscription Management Bot
Combines all handler classes into one main bot
"""
import sys
sys.path.append('/app/backend')

from src.services.telegram.bot_new import OTTBot as BaseOTTBot
from src.services.telegram.bot_handlers import (
    OTTExplorerHandlers,
    ComparePlansHandlers,
    ReleaseAlertsHandlers,
    DashboardHandlers
)
from src.services.telegram.bot_subscription_admin import (
    SubscriptionHandlers,
    AdminHandlers,
    SettingsHandlers,
    HelpHandlers
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)
import logging

logger = logging.getLogger(__name__)


# Create integrated bot class with all handlers
class OTTBot(
    BaseOTTBot,
    OTTExplorerHandlers,
    ComparePlansHandlers,
    ReleaseAlertsHandlers,
    DashboardHandlers,
    SubscriptionHandlers,
    AdminHandlers,
    SettingsHandlers,
    HelpHandlers
):
    """Complete OTT Bot with all features"""
    
    async def handle_photo_message(self, update, context):
        """Handle photo uploads (payment screenshots)"""
        user_id = update.effective_user.id
        
        # Check if user is awaiting screenshot upload
        from src.services.telegram.bot_new import user_sessions
        session = user_sessions.get(user_id, {})
        
        if session.get("awaiting_screenshot"):
            payment_id = session.get("payment_id")
            
            if not payment_id:
                await update.message.reply_text("Error: Payment ID not found.")
                return
            
            # Get photo file
            photo = update.message.photo[-1]  # Get highest resolution
            file_id = photo.file_id
            
            # Update payment with screenshot
            success = await self.payment_service.update_screenshot(
                payment_id=payment_id,
                file_id=file_id
            )
            
            if success:
                await update.message.reply_text(
                    "✅ **Payment Screenshot Received!**\n\n"
                    "Your payment is now pending admin verification.\n"
                    "You'll be notified once approved (usually within 24 hours).\n\n"
                    "Payment ID: `" + payment_id[:8] + "`",
                    parse_mode="Markdown"
                )
                
                # Clear session
                user_sessions[user_id] = {}
                
                # Notify admins
                await self.notify_admins_new_payment(payment_id)
            else:
                await update.message.reply_text(
                    "❌ Failed to upload screenshot. Please try again."
                )
        else:
            await update.message.reply_text(
                "Please use the Subscriptions menu to initiate a payment first."
            )
    
    async def handle_text_message(self, update, context):
        """Handle text messages (commands, preferences, etc.)"""
        text = update.message.text
        user_id = update.effective_user.id
        
        # Admin commands
        if text.startswith("verify "):
            if await self.is_admin(user_id):
                payment_id = text.split(" ")[1]
                await self.admin_verify_payment(update, payment_id, approved=True)
            else:
                await update.message.reply_text("⛔ Admin access required")
        
        elif text.startswith("reject "):
            if await self.is_admin(user_id):
                parts = text.split(" ", 2)
                payment_id = parts[1]
                reason = parts[2] if len(parts) > 2 else "Payment verification failed"
                await self.admin_verify_payment(update, payment_id, approved=False, reason=reason)
            else:
                await update.message.reply_text("⛔ Admin access required")
        
        elif text.startswith("announce:"):
            if await self.is_admin(user_id):
                message = text.replace("announce:", "").strip()
                await self.broadcast_announcement(update, message)
            else:
                await update.message.reply_text("⛔ Admin access required")
        
        # User commands
        elif text.startswith("support:"):
            message = text.replace("support:", "").strip()
            await self.forward_to_admin(update, message)
        
        elif text.startswith("issue:"):
            issue = text.replace("issue:", "").strip()
            await self.report_issue(update, issue)
        
        elif text.startswith("refund:"):
            refund_request = text.replace("refund:", "").strip()
            await self.request_refund(update, refund_request)
        
        else:
            # Generic response
            await update.message.reply_text(
                "Use /menu to see available options!",
                parse_mode="Markdown"
            )
    
    async def admin_verify_payment(self, update, payment_id: str, approved: bool = True, reason: str = None):
        """Admin verifies a payment"""
        admin_id = update.effective_user.id
        
        # Get admin user
        admin_data = await self.admins_collection.find_one({"telegram_id": admin_id})
        if not admin_data:
            await update.message.reply_text("Admin not found")
            return
        
        # Verify payment
        success = await self.payment_service.verify_payment(
            payment_id=payment_id,
            admin_id=admin_data['admin_id'],
            approved=approved,
            reason=reason
        )
        
        if not success:
            await update.message.reply_text("Payment not found or already processed")
            return
        
        # Get payment details
        payment = await self.payment_service.get_payment(payment_id)
        
        if approved:
            # Activate subscription for user
            await self.activate_user_subscription(payment)
            
            # Notify user
            await context.bot.send_message(
                chat_id=payment.telegram_id,
                text=f"✅ **Payment Verified!**\n\n"
                     f"Your {payment.plan_type} subscription has been activated.\n"
                     f"Amount: ₹{payment.amount}\n"
                     f"Platforms: {', '.join(payment.platforms)}\n\n"
                     f"Enjoy your subscription! 🎉",
                parse_mode="Markdown"
            )
            
            await update.message.reply_text(
                f"✅ Payment {payment_id[:8]} verified and subscription activated!"
            )
        else:
            # Notify user of rejection
            await context.bot.send_message(
                chat_id=payment.telegram_id,
                text=f"❌ **Payment Rejected**\n\n"
                     f"Reason: {reason}\n\n"
                     f"Please contact support for assistance.",
                parse_mode="Markdown"
            )
            
            await update.message.reply_text(
                f"❌ Payment {payment_id[:8]} rejected. User notified."
            )
    
    async def activate_user_subscription(self, payment):
        """Activate subscription for user after payment verification"""
        from datetime import datetime, timedelta
        
        # Determine duration based on plan type
        duration_map = {
            "weekly": 7,
            "monthly": 30,
            "custom": 30
        }
        
        duration_days = duration_map.get(payment.plan_type, 30)
        
        # Create subscription
        from src.models.user import UserSubscription
        subscription = UserSubscription(
            plan_type=payment.plan_type,
            platforms=payment.platforms,
            amount_paid=payment.amount,
            start_date=datetime.utcnow(),
            expiry_date=datetime.utcnow() + timedelta(days=duration_days),
            is_active=True,
            payment_id=payment.payment_id
        )
        
        # Update user
        await self.users_collection.update_one(
            {"user_id": payment.user_id},
            {
                "$push": {"active_subscriptions": subscription.model_dump()},
                "$inc": {"total_spent": payment.amount}
            }
        )
        
        logger.info(f"Subscription activated for user {payment.user_id}")
    
    async def notify_admins_new_payment(self, payment_id: str):
        """Notify all admins about new payment"""
        admins = await self.admins_collection.find({"is_active": True}).to_list(length=100)
        
        payment = await self.payment_service.get_payment(payment_id)
        if not payment:
            return
        
        message = f"""
🔔 **New Payment Received**

**Payment ID:** `{payment.payment_id[:8]}`
**Amount:** ₹{payment.amount}
**Plan:** {payment.plan_type}
**User:** @{payment.telegram_id}

Screenshot uploaded ✅

**Verify:** `verify {payment.payment_id}`
**Reject:** `reject {payment.payment_id} [reason]`
"""
        
        for admin in admins:
            try:
                await context.bot.send_message(
                    chat_id=admin['telegram_id'],
                    text=message,
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"Failed to notify admin {admin['telegram_id']}: {e}")
    
    async def broadcast_announcement(self, update, message: str):
        """Broadcast message to all users"""
        users = await self.users_collection.find({}).to_list(length=10000)
        
        sent_count = 0
        failed_count = 0
        
        for user in users:
            try:
                await context.bot.send_message(
                    chat_id=user['telegram_id'],
                    text=f"📢 **Announcement**\n\n{message}",
                    parse_mode="Markdown"
                )
                sent_count += 1
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to send to {user['telegram_id']}: {e}")
        
        await update.message.reply_text(
            f"📢 Announcement sent!\n\n"
            f"✅ Sent: {sent_count}\n"
            f"❌ Failed: {failed_count}"
        )
    
    async def forward_to_admin(self, update, message: str):
        """Forward user message to admins"""
        user = update.effective_user
        
        admin_message = f"""
💬 **Support Request**

**From:** {user.first_name} (@{user.id})
**Message:** {message}

**Reply:** `announce: @{user.id} [your response]`
"""
        
        admins = await self.admins_collection.find({"is_active": True}).to_list(length=100)
        
        for admin in admins:
            try:
                await context.bot.send_message(
                    chat_id=admin['telegram_id'],
                    text=admin_message,
                    parse_mode="Markdown"
                )
            except Exception as e:
                logger.error(f"Failed to forward to admin {admin['telegram_id']}: {e}")
        
        await update.message.reply_text(
            "✅ Your message has been forwarded to the admin team.\n"
            "We'll get back to you shortly!"
        )
    
    async def report_issue(self, update, issue: str):
        """Report an issue"""
        # Same as forward_to_admin but with different context
        await self.forward_to_admin(update, f"ISSUE: {issue}")
    
    async def request_refund(self, update, refund_details: str):
        """Request a refund"""
        await self.forward_to_admin(update, f"REFUND REQUEST: {refund_details}")
    
    def setup_handlers(self):
        """Setup all bot handlers"""
        self.application = Application.builder().token(self.token).build()
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("menu", self.menu_command))
        
        # Callback query handler (for buttons)
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Photo handler (for payment screenshots)
        self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo_message))
        
        # Text message handler
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
        
        logger.info("All handlers registered")
    
    async def run(self):
        """Run the bot"""
        # Initialize database
        await self.initialize_db()
        
        # Setup handlers
        self.setup_handlers()
        
        # Start bot
        logger.info("Starting OTT Subscription Bot...")
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        # Keep running
        import asyncio
        await asyncio.Future()  # Run forever


# Entry point for running the bot
async def start_bot():
    """Start the OTT bot"""
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    token = os.getenv("TELEGRAM_BOT_TOKEN", "your_bot_token_here")
    mongo_url = os.getenv("MONGO_URL", "mongodb://localhost:27017")
    db_name = os.getenv("DB_NAME", "ott_bot_db")
    admin_upi_id = os.getenv("ADMIN_UPI_ID", "admin@upi")
    
    if token == "your_bot_token_here":
        logger.error("Please set TELEGRAM_BOT_TOKEN in .env file")
        return
    
    bot = OTTBot(token, mongo_url, db_name, admin_upi_id)
    await bot.run()


if __name__ == "__main__":
    import asyncio
    asyncio.run(start_bot())
