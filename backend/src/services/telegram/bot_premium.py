"""
Premium Features Handler for OTT Bot
Handles premium subscriptions, referrals, and payments
"""
import logging
import sys
sys.path.append('/app/backend')
import config
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from datetime import datetime, timedelta
from typing import Optional, Dict
import uuid

logger = logging.getLogger(__name__)

class PremiumHandlers:
    """Mixin class for premium subscription features"""
    
    async def premium_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show premium subscription menu"""
        user_id = update.effective_user.id
        
        # Check if user already has premium
        user = await self.users_collection.find_one({"telegram_id": user_id})
        has_premium = False
        expiry_date = None
        
        if user and user.get("premium_subscription"):
            sub = user["premium_subscription"]
            if sub.get("is_active") and sub.get("expiry_date"):
                expiry = datetime.fromisoformat(sub["expiry_date"])
                if expiry > datetime.utcnow():
                    has_premium = True
                    expiry_date = expiry
        
        if has_premium:
            # Show current plan
            days_left = (expiry_date - datetime.utcnow()).days
            message = f"""
💎 <b>Your Premium Status</b>

✅ <b>Status:</b> Active
⏰ <b>Expires in:</b> {days_left} days
📅 <b>Expiry Date:</b> {expiry_date.strftime('%d %b %Y')}

<b>Premium Benefits:</b>
✓ Unlimited OTT platform access
✓ No ads or verification required
✓ Direct file access
✓ High-speed streaming
✓ Priority support
✓ Early access to new content

<i>Renew your premium to continue enjoying benefits!</i>
"""
            keyboard = [
                [InlineKeyboardButton("🔄 Renew Premium", callback_data="show_premium_plans")],
                [InlineKeyboardButton("👥 Refer Friends", callback_data="referral_program")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
            ]
        else:
            # Show premium plans
            message = f"""
💎 <b>Upgrade to Premium</b>

{config.PAYMENT_TEXT}

<b>Why Premium?</b>
Get instant access to all OTT platforms without any hassle!
"""
            keyboard = [
                [InlineKeyboardButton("📋 View Plans", callback_data="show_premium_plans")],
                [InlineKeyboardButton("👥 Earn Free Premium", callback_data="referral_program")],
                [InlineKeyboardButton("🏠 Main Menu", callback_data="main_menu")]
            ]
        
        markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            try:
                await update.callback_query.edit_message_text(
                    message,
                    reply_markup=markup,
                    parse_mode="HTML"
                )
            except Exception as e:
                # If editing fails (e.g., message has photo), send new message
                await update.callback_query.message.reply_text(
                    message,
                    reply_markup=markup,
                    parse_mode="HTML"
                )
        else:
            await update.message.reply_text(
                message,
                reply_markup=markup,
                parse_mode="HTML"
            )
    
    async def show_premium_plans(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Display available premium plans"""
        message = """
💎 <b>Premium Subscription Plans</b>

Choose the plan that suits you best:

"""
        keyboard = []
        
        for plan_id, plan in config.PREMIUM_PLANS.items():
            plan_text = f"💳 {plan['name']} - ₹{plan['price']}"
            keyboard.append([InlineKeyboardButton(
                plan_text,
                callback_data=f"buy_premium_{plan_id}"
            )])
            
            message += f"\n<b>{plan['name']}</b>\n"
            message += f"💰 Price: ₹{plan['price']}\n"
            message += f"⏰ Duration: {plan['description']}\n"
        
        message += f"\n\n📱 <b>Payment Method:</b> UPI\n"
        message += f"💵 <b>UPI ID:</b> <code>kolashankar113@oksbi</code>\n\n"
        message += f"<i>Select a plan to proceed with payment</i>"
        
        keyboard.append([InlineKeyboardButton("👥 Earn Free Premium", callback_data="referral_program")])
        keyboard.append([InlineKeyboardButton("« Back", callback_data="premium_menu")])
        
        markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await update.callback_query.edit_message_text(
                message,
                reply_markup=markup,
                parse_mode="HTML"
            )
        except Exception as e:
            # If editing fails (e.g., message has photo), send new message
            await update.callback_query.message.reply_text(
                message,
                reply_markup=markup,
                parse_mode="HTML"
            )
    
    async def buy_premium_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE, plan_id: str):
        """Initiate premium plan purchase"""
        user_id = update.effective_user.id
        username = update.effective_user.username or "Unknown"
        
        if plan_id not in config.PREMIUM_PLANS:
            await update.callback_query.answer("Invalid plan selected!")
            return
        
        plan = config.PREMIUM_PLANS[plan_id]
        
        # Create payment record
        payment_id = str(uuid.uuid4())
        payment_doc = {
            "payment_id": payment_id,
            "user_id": str(user_id),
            "telegram_id": user_id,
            "telegram_username": username,
            "amount": plan["price"],
            "plan_type": plan_id,
            "plan_name": plan["name"],
            "platforms": ["All OTT Platforms"],
            "status": "pending",
            "payment_method": "UPI",
            "screenshot_file_id": None,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        await self.payments_collection.insert_one(payment_doc)
        
        # Send payment instructions with QR code
        message = f"""
💳 <b>Payment for {plan['name']}</b>

<b>Amount:</b> ₹{plan['price']}
<b>Duration:</b> {plan['description']}

<b>🔸 Payment Instructions:</b>

1️⃣ Scan the QR code or use UPI ID below
2️⃣ Pay exactly ₹{plan['price']}
3️⃣ Take a screenshot of successful payment
4️⃣ Send the screenshot here

💵 <b>UPI ID:</b> <code>kolashankar113@oksbi</code>

<b>Payment ID:</b> <code>{payment_id[:8]}</code>

⚠️ <b>Important:</b> Screenshot must clearly show:
• Transaction ID
• Amount: ₹{plan['price']}
• Status: Success

<i>After sending screenshot, wait for admin verification (usually within 1-2 hours)</i>
"""
        
        keyboard = [
            [InlineKeyboardButton("✅ I've Sent Screenshot", callback_data=f"check_payment_{payment_id[:8]}")],
            [InlineKeyboardButton("« Cancel", callback_data="premium_menu")]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        
        # Send QR code image
        try:
            await context.bot.send_photo(
                chat_id=user_id,
                photo=config.PAYMENT_QR,
                caption=message,
                reply_markup=markup,
                parse_mode="HTML"
            )
            
            # Store payment_id in user session
            if not hasattr(context, 'user_data'):
                context.user_data = {}
            context.user_data['awaiting_payment_screenshot'] = True
            context.user_data['payment_id'] = payment_id
            
            await update.callback_query.answer("Payment initiated! Please complete payment.")
            
        except Exception as e:
            logger.error(f"Error sending payment QR: {e}")
            await update.callback_query.answer("Error initiating payment. Please try again.")
    
    async def referral_program(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show referral program details"""
        user_id = update.effective_user.id
        
        # Get referral stats
        stats = await self.referral_service.get_or_create_referral_stats(user_id)
        reward_info = await self.referral_service.check_referral_rewards(user_id, config.REFERAL_COUNT)
        
        referral_code = stats.get("referral_code", "N/A")
        valid_referrals = reward_info.get("valid_referrals", 0)
        required = reward_info.get("required_count", 20)
        pending_rewards = reward_info.get("pending_rewards", 0)
        next_reward = reward_info.get("next_reward_at", required)
        
        # Generate referral link
        bot_username = context.bot.username
        referral_link = f"https://t.me/{bot_username}?start={referral_code}"
        
        message = f"""
👥 <b>Referral Program</b>

Invite friends and earn FREE premium subscription!

<b>Your Referral Stats:</b>
✅ Valid Referrals: {valid_referrals}/{required}
🎁 Pending Rewards: {pending_rewards}
📈 Next Reward in: {next_reward} referrals

<b>Your Referral Link:</b>
<code>{referral_link}</code>

<b>How it Works:</b>
1️⃣ Share your referral link with friends
2️⃣ They join using your link
3️⃣ After {required} valid referrals, get {config.REFERAL_PREMEIUM_TIME} premium FREE!

<b>💡 Tips:</b>
• Share in groups and social media
• Your friend must stay active to count
• Each {required} referrals = 1 free premium month

<i>Start sharing and earn premium for free!</i>
"""
        
        keyboard = [
            [InlineKeyboardButton("📋 Copy Referral Link", callback_data="copy_referral")],
            [InlineKeyboardButton("📊 My Referrals", callback_data="my_referrals")]
        ]
        
        if pending_rewards > 0:
            keyboard.insert(0, [InlineKeyboardButton(
                f"🎁 Claim {pending_rewards} Free Premium",
                callback_data="claim_referral_reward"
            )])
        
        keyboard.append([InlineKeyboardButton("« Back", callback_data="premium_menu")])
        
        markup = InlineKeyboardMarkup(keyboard)
        
        if update.callback_query:
            try:
                await update.callback_query.edit_message_text(
                    message,
                    reply_markup=markup,
                    parse_mode="HTML"
                )
            except Exception as e:
                # If editing fails (e.g., message has photo), send new message
                await update.callback_query.message.reply_text(
                    message,
                    reply_markup=markup,
                    parse_mode="HTML"
                )
        else:
            await update.message.reply_text(
                message,
                reply_markup=markup,
                parse_mode="HTML"
            )
    
    async def claim_referral_reward(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Claim referral reward (free premium)"""
        user_id = update.effective_user.id
        
        # Check if eligible
        reward_info = await self.referral_service.check_referral_rewards(user_id, config.REFERAL_COUNT)
        
        if reward_info["pending_rewards"] <= 0:
            await update.callback_query.answer("No pending rewards!", show_alert=True)
            return
        
        # Claim reward
        success = await self.referral_service.claim_referral_reward(user_id)
        
        if success:
            # Activate premium
            duration_days = 30  # 1 month default
            if "3month" in config.REFERAL_PREMEIUM_TIME:
                duration_days = 90
            elif "6month" in config.REFERAL_PREMEIUM_TIME:
                duration_days = 180
            
            start_date = datetime.utcnow()
            expiry_date = start_date + timedelta(days=duration_days)
            
            # Update user with premium
            await self.users_collection.update_one(
                {"telegram_id": user_id},
                {
                    "$set": {
                        "premium_subscription": {
                            "plan_type": "referral_reward",
                            "start_date": start_date.isoformat(),
                            "expiry_date": expiry_date.isoformat(),
                            "is_active": True,
                            "source": "referral"
                        },
                        "updated_at": datetime.utcnow().isoformat()
                    }
                }
            )
            
            message = f"""
🎉 <b>Congratulations!</b>

You've successfully claimed your referral reward!

💎 <b>Premium Activated!</b>
⏰ <b>Duration:</b> {config.REFERAL_PREMEIUM_TIME}
📅 <b>Expires on:</b> {expiry_date.strftime('%d %b %Y')}

<b>Keep inviting friends to earn more!</b>
"""
            
            await update.callback_query.answer("Reward claimed! 🎉", show_alert=False)
            try:
                await update.callback_query.edit_message_text(
                    message,
                    parse_mode="HTML"
                )
            except Exception as e:
                # If editing fails (e.g., message has photo), send new message
                await update.callback_query.message.reply_text(
                    message,
                    parse_mode="HTML"
                )
            
            # Log to channel
            if config.LOG_CHANNEL:
                try:
                    await context.bot.send_message(
                        chat_id=config.LOG_CHANNEL,
                        text=f"🎁 Premium reward claimed via referral\nUser: @{update.effective_user.username or user_id}\nDuration: {config.REFERAL_PREMEIUM_TIME}"
                    )
                except:
                    pass
        else:
            await update.callback_query.answer("Error claiming reward. Please try again.", show_alert=True)
    
    async def my_referrals_list(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show list of referrals"""
        user_id = update.effective_user.id
        
        referrals = await self.referral_service.get_referral_list(user_id, limit=20)
        
        if not referrals:
            message = """
👥 <b>My Referrals</b>

You haven't referred anyone yet!

Share your referral link to start earning free premium.
"""
        else:
            message = f"""
👥 <b>My Referrals ({len(referrals)})</b>

"""
            for i, ref in enumerate(referrals[:10], 1):
                username = ref.get("referred_username", "Unknown")
                date = ref.get("created_at").strftime("%d %b") if isinstance(ref.get("created_at"), datetime) else "N/A"
                status = "✅" if ref.get("is_valid") else "⏳"
                message += f"{i}. {status} @{username} - {date}\n"
            
            if len(referrals) > 10:
                message += f"\n<i>+{len(referrals) - 10} more referrals</i>"
        
        keyboard = [
            [InlineKeyboardButton("« Back", callback_data="referral_program")]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        
        try:
            await update.callback_query.edit_message_text(
                message,
                reply_markup=markup,
                parse_mode="HTML"
            )
        except Exception as e:
            # If editing fails (e.g., message has photo), send new message
            await update.callback_query.message.reply_text(
                message,
                reply_markup=markup,
                parse_mode="HTML"
            )
    
    async def myplan_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /myplan command"""
        await self.premium_menu(update, context)
