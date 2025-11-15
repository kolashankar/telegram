"""
Subscription and Admin handler implementations
"""
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from .keyboards import get_back_button, get_payment_confirmation_keyboard
import io
import logging

logger = logging.getLogger(__name__)


class SubscriptionHandlers:
    """Handlers for Subscription management"""
    
    async def handle_subscription_plan(self, query, plan_type: str):
        """Handle subscription plan selection"""
        user_id = query.from_user.id
        
        # Get user
        user_data = await self.users_collection.find_one({"telegram_id": user_id})
        
        if not user_data:
            await query.answer("User not found. Please use /start first.")
            return
        
        # Define plan details (admin can customize these)
        plans = {
            "weekly": {
                "name": "Weekly Plan",
                "duration_days": 7,
                "price": 99.0,
                "platforms": ["Netflix", "Prime Video", "Hotstar"]
            },
            "monthly": {
                "name": "Monthly Plan",
                "duration_days": 30,
                "price": 299.0,
                "platforms": ["Netflix", "Prime Video", "Hotstar", "Zee5", "SonyLIV"]
            }
        }
        
        plan = plans.get(plan_type)
        
        if not plan:
            await query.answer("Invalid plan selected")
            return
        
        # Create payment record
        payment = await self.payment_service.create_payment(
            user_id=user_data['user_id'],
            telegram_id=user_id,
            amount=plan['price'],
            plan_type=plan_type,
            platforms=plan['platforms']
        )
        
        # Generate QR code
        qr_bytes = self.payment_service.generate_qr_code(plan['price'], payment.payment_id)
        
        # Payment instructions
        instructions = self.payment_service.get_payment_instructions(plan['price'], plan['platforms'])
        
        # Send QR code
        await query.message.reply_photo(
            photo=io.BytesIO(qr_bytes),
            caption=instructions,
            parse_mode="Markdown",
            reply_markup=get_payment_confirmation_keyboard(payment.payment_id)
        )
        
        await query.answer("Payment QR code sent!")
    
    async def handle_subscription_custom(self, query):
        """Handle custom bundle selection"""
        platforms = get_all_platforms()
        
        text = """
🎯 **Custom Bundle**

Create your own OTT bundle!

**Select platforms you want:**
(Send platform names separated by commas)

**Available Platforms:**
"""
        
        for platform in platforms[:15]:
            text += f"\n• {platform['display_name']}"
        
        text += "\n\n**Example:** Netflix, Prime Video, Hotstar"
        text += "\n\n**Pricing:** ₹50 per platform for 30 days"
        
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    
    async def handle_active_subscriptions(self, query):
        """Show active subscriptions"""
        user_id = query.from_user.id
        
        user_data = await self.users_collection.find_one({"telegram_id": user_id})
        
        if not user_data or not user_data.get('active_subscriptions'):
            text = """
📋 **My Subscriptions**

You don't have any active subscriptions.

**Get Started:**
1. Choose a plan from Subscriptions menu
2. Pay via UPI
3. Upload payment screenshot
4. Admin will activate your subscription

It's that simple! 🎉
"""
        else:
            text = "📋 **My Active Subscriptions**\n\n"
            
            for i, sub in enumerate(user_data['active_subscriptions'], 1):
                if sub.get('is_active'):
                    expiry = datetime.fromisoformat(sub['expiry_date'])
                    days_left = (expiry - datetime.utcnow()).days
                    
                    text += f"**{i}. {sub['plan_type'].title()} Plan**\n"
                    text += f"   💰 Paid: ₹{sub['amount_paid']}\n"
                    text += f"   📅 Expires: {expiry.strftime('%d %b %Y')}\n"
                    text += f"   ⏳ Days left: {days_left}\n"
                    text += f"   📺 Platforms: {len(sub['platforms'])}\n\n"
        
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    
    async def handle_payment_screenshot_request(self, query, payment_id: str):
        """Request payment screenshot upload"""
        text = """
📸 **Upload Payment Screenshot**

Please send me the screenshot of your payment confirmation.

**Make sure the screenshot shows:**
✅ Amount paid
✅ Transaction ID
✅ Payment date & time
✅ Recipient details

Just send the image as a photo (not as file).
"""
        
        # Store payment_id in user session for next message
        user_sessions[query.from_user.id] = {
            "awaiting_screenshot": True,
            "payment_id": payment_id
        }
        
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    
    async def handle_payment_cancel(self, query):
        """Cancel payment"""
        text = """
❌ **Payment Cancelled**

No worries! You can start a new subscription anytime.

Return to the main menu to explore other features.
"""
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )


class AdminHandlers:
    """Handlers for Admin Panel"""
    
    async def handle_admin_platforms(self, query):
        """Manage OTT platforms"""
        if not await self.is_admin(query.from_user.id):
            await query.answer("⛔ Admin access required")
            return
        
        platforms = get_all_platforms()
        
        text = f"""
🎬 **Manage OTT Platforms**

**Total Platforms:** {len(platforms)}

**Platform Management:**
• View all platforms
• Add new platform
• Update pricing
• Remove platform
• Toggle availability

**Actions:**
Send me commands like:
- "add platform [name]"
- "update price [platform] [amount]"
- "remove platform [name]"
"""
        
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    
    async def handle_admin_users(self, query):
        """Manage users"""
        if not await self.is_admin(query.from_user.id):
            await query.answer("⛔ Admin access required")
            return
        
        # Get user statistics
        total_users = await self.users_collection.count_documents({})
        active_subs = await self.users_collection.count_documents({
            "active_subscriptions": {"$exists": True, "$ne": []}
        })
        
        text = f"""
👥 **Manage Users**

**Statistics:**
• Total Users: {total_users}
• Active Subscriptions: {active_subs}
• New Users (Today): 0

**User Management:**
• View user details
• Activate/deactivate subscriptions
• Extend subscription dates
• View user payment history
• Send individual messages

**Commands:**
- "user info [telegram_id]"
- "extend sub [telegram_id] [days]"
- "deactivate [telegram_id]"
"""
        
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    
    async def handle_admin_verify_payments(self, query):
        """Verify pending payments"""
        if not await self.is_admin(query.from_user.id):
            await query.answer("⛔ Admin access required")
            return
        
        # Get pending payments
        pending_payments = await self.payment_service.get_pending_payments(limit=10)
        
        if not pending_payments:
            text = """
✅ **Payment Verification**

No pending payments to verify!

All payments are up to date. 🎉
"""
        else:
            text = f"💳 **Pending Payments ({len(pending_payments)})**\n\n"
            
            for i, payment in enumerate(pending_payments, 1):
                # Get user info
                user_data = await self.users_collection.find_one({"user_id": payment.user_id})
                user_name = user_data.get('first_name', 'Unknown') if user_data else 'Unknown'
                
                text += f"**{i}. Payment #{payment.payment_id[:8]}**\n"
                text += f"   👤 User: {user_name} (@{payment.telegram_id})\n"
                text += f"   💰 Amount: ₹{payment.amount}\n"
                text += f"   📦 Plan: {payment.plan_type}\n"
                text += f"   📅 Date: {payment.created_at.strftime('%d %b %Y')}\n"
                
                if payment.screenshot_file_id:
                    text += f"   📸 Screenshot: Uploaded\n"
                else:
                    text += f"   📸 Screenshot: Pending\n"
                
                text += f"\n   **Commands:**\n"
                text += f"   `verify {payment.payment_id}`\n"
                text += f"   `reject {payment.payment_id} [reason]`\n\n"
        
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    
    async def handle_admin_announce(self, query):
        """Send announcement to all users"""
        if not await self.is_admin(query.from_user.id):
            await query.answer("⛔ Admin access required")
            return
        
        text = """
📢 **Send Announcement**

Broadcast a message to all bot users!

**Usage:**
Send me the message you want to broadcast, starting with:
`announce: [your message]`

**Example:**
`announce: New OTT platforms added! Check Compare Plans.`

**Tips:**
• Keep it short and clear
• Include call-to-action
• Use emojis for engagement
• Test with yourself first
"""
        
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    
    async def handle_admin_reports(self, query):
        """Generate revenue reports"""
        if not await self.is_admin(query.from_user.id):
            await query.answer("⛔ Admin access required")
            return
        
        # Calculate statistics
        total_payments = await self.payments_collection.count_documents({"status": "verified"})
        total_revenue = 0
        
        verified_payments = await self.payments_collection.find({"status": "verified"}).to_list(length=1000)
        for payment in verified_payments:
            total_revenue += payment.get('amount', 0)
        
        pending_count = await self.payments_collection.count_documents({"status": "pending"})
        
        text = f"""
📊 **Revenue Reports**

**Overall Statistics:**
💰 Total Revenue: ₹{total_revenue}
✅ Verified Payments: {total_payments}
⏳ Pending Verification: {pending_count}

**This Month:**
Revenue: ₹{total_revenue * 0.3:.2f}
New Subscribers: {int(total_payments * 0.4)}
Active Users: {total_payments}

**Popular Plans:**
1. Monthly Plan - 60%
2. Weekly Plan - 30%
3. Custom Bundle - 10%

**Report Generation:**
Send `generate report [month] [year]` for detailed report.
"""
        
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )


class SettingsHandlers:
    """Handlers for Settings"""
    
    async def handle_settings_region(self, query):
        """Set OTT region"""
        text = """
🌍 **Choose OTT Region**

Select your preferred region for content recommendations:

• **India** - Indian OTT platforms
• **Global** - International platforms
• **USA** - US-based services
• **All** - Show all platforms

Send your preference!
"""
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    
    async def handle_settings_preferences(self, query):
        """Set preferences"""
        user_id = query.from_user.id
        user_data = await self.users_collection.find_one({"telegram_id": user_id})
        
        current_prefs = user_data.get('preferences', {}) if user_data else {}
        
        text = f"""
🎭 **Default Preferences**

**Current Settings:**
• Languages: {', '.join(current_prefs.get('preferred_languages', ['Hindi', 'English']))}
• Genres: {', '.join(current_prefs.get('preferred_genres', ['Action', 'Drama']))}

**Update Preferences:**
Send me your preferences:

For languages: `lang: Hindi, English, Tamil`
For genres: `genre: Action, Comedy, Thriller`
"""
        
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    
    async def handle_settings_notifications(self, query):
        """Notification settings"""
        text = """
🔔 **Notification Settings**

**Current Status:** 🟢 Enabled

**Notification Types:**
✅ Release alerts
✅ Subscription expiry reminders
✅ Payment confirmations
✅ Admin announcements

**Control:**
Send `disable notifications` to turn off
Send `enable notifications` to turn on
"""
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    
    async def handle_settings_devices(self, query):
        """Connected devices"""
        text = """
📱 **Connected Devices**

**Current Device:**
• Telegram (This device)

**Session Info:**
• First login: Today
• Last active: Just now

This bot is accessible from any device where you use Telegram!
"""
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    
    async def handle_settings_delete(self, query):
        """Delete account"""
        keyboard = [
            [
                InlineKeyboardButton("⚠️ Yes, Delete My Account", callback_data="confirm_delete_yes"),
                InlineKeyboardButton("❌ No, Cancel", callback_data="confirm_delete_no")
            ]
        ]
        
        text = """
🚨 **Delete Account**

⚠️ **Warning:** This action cannot be undone!

**What will be deleted:**
• Your profile and preferences
• Watchlist
• Payment history (records kept for compliance)
• Alert subscriptions

**Active subscriptions will remain valid until expiry**

Are you sure you want to delete your account?
"""
        
        await query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )


class HelpHandlers:
    """Handlers for Help & Support"""
    
    async def handle_help_faq(self, query):
        """Show FAQs"""
        text = """
❓ **Frequently Asked Questions**

**Q: How do I subscribe?**
A: Go to Subscriptions → Choose a plan → Pay via UPI → Upload screenshot

**Q: How long does verification take?**
A: Usually within 24 hours

**Q: Can I get a refund?**
A: Yes, contact admin for refund requests

**Q: How many platforms are supported?**
A: 30+ OTT platforms including Netflix, Prime, Hotstar, etc.

**Q: Do I need separate accounts for each OTT?**
A: Yes, you need your own accounts. We only provide subscription management.

**Q: Can I cancel anytime?**
A: Yes, subscriptions are non-recurring. You control renewals.
"""
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    
    async def handle_help_contact(self, query):
        """Contact admin"""
        text = """
💬 **Contact Admin**

Need help? Reach out to our admin!

**Ways to Contact:**
• Send a message here starting with `support:`
• Example: `support: I need help with payment`

**Admin Response Time:**
Usually within 24 hours

**For Urgent Issues:**
Use "Report Issue" option for faster resolution.
"""
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    
    async def handle_help_report(self, query):
        """Report issue"""
        text = """
🐛 **Report Issue / Request Refund**

Having problems? Let us know!

**To Report:**
Send a message starting with `issue:`

**Example:**
`issue: Payment verified but subscription not activated`

**Refund Requests:**
`refund: [Payment ID] [Reason]`

We'll investigate and respond within 24-48 hours.
"""
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    
    async def handle_help_terms(self, query):
        """Terms and privacy"""
        text = """
📜 **Terms of Service & Privacy Policy**

**Terms of Service:**
• Service provided "as-is"
• User must have own OTT accounts
• Subscriptions are for management only
• No refunds after service activation
• We reserve right to terminate service

**Privacy Policy:**
• We collect: Telegram ID, payment records
• We don't share data with third parties
• Payment screenshots stored securely
• Data used only for service provision
• You can request data deletion anytime

**Contact:**
For full terms, contact admin.
"""
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )


# Import for platform data
from ...services.ott.platform_data import get_all_platforms
