"""
Force Subscribe Service for OTT Bot
Ensures users join required channels before accessing bot
"""
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ChatMemberStatus
from typing import Optional, Tuple
import sys
sys.path.append('/app/backend')
import config

logger = logging.getLogger(__name__)

class ForceSubscribeService:
    """Service to handle force subscribe functionality"""
    
    def __init__(self, bot_instance):
        self.bot = bot_instance
        self.auth_channel = config.AUTH_CHANNEL
        self.request_to_join_mode = config.REQUEST_TO_JOIN_MODE
        self.try_again_btn = config.TRY_AGAIN_BTN
    
    async def check_user_subscription(self, user_id: int, context) -> Tuple[bool, Optional[str]]:
        """
        Check if user is subscribed to required channel
        Returns: (is_subscribed, channel_link)
        """
        if not self.auth_channel:
            return True, None
        
        try:
            # Check if user is member of auth channel
            member = await context.bot.get_chat_member(
                chat_id=self.auth_channel,
                user_id=user_id
            )
            
            # Check membership status
            if member.status in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                return True, None
            
            # User is not subscribed, get channel link
            try:
                chat = await context.bot.get_chat(self.auth_channel)
                if chat.username:
                    channel_link = f"https://t.me/{chat.username}"
                elif chat.invite_link:
                    channel_link = chat.invite_link
                else:
                    channel_link = None
                
                return False, channel_link
            except Exception as e:
                logger.error(f"Error getting channel link: {e}")
                return False, None
                
        except Exception as e:
            logger.error(f"Error checking subscription: {e}")
            # If we can't check (e.g., chat not found), allow access (fail open)
            return True, None
    
    def get_force_subscribe_keyboard(self, channel_link: Optional[str] = None, callback_data: str = "check_subscription") -> InlineKeyboardMarkup:
        """Generate force subscribe keyboard"""
        keyboard = []
        
        if channel_link:
            if self.request_to_join_mode:
                keyboard.append([InlineKeyboardButton("📢 Request to Join Channel", url=channel_link)])
            else:
                keyboard.append([InlineKeyboardButton("📢 Join Channel", url=channel_link)])
        
        # Add try again button
        if self.try_again_btn or not self.request_to_join_mode:
            keyboard.append([InlineKeyboardButton("🔄 Try Again", callback_data=callback_data)])
        
        # Add help button
        if config.TUTORIAL:
            keyboard.append([InlineKeyboardButton("❓ How to Join", url=config.TUTORIAL)])
        
        return InlineKeyboardMarkup(keyboard)
    
    def get_force_subscribe_message(self) -> str:
        """Get force subscribe message text"""
        if self.request_to_join_mode:
            message = """
🔒 <b>Access Restricted</b>

To use this bot, you need to request to join our channel first.

📢 Click the button below to request access to our channel
✅ Once your request is approved, click "Try Again"

<i>This helps us keep the community active and engaged!</i>
"""
        else:
            message = """
🔒 <b>Join Our Channel First</b>

To access this bot and enjoy premium OTT content, you must join our official channel.

📢 Click "Join Channel" button below
✅ After joining, click "Try Again"

<i>Stay updated with latest movies, series, and OTT content!</i>
"""
        
        return message.strip()
    
    async def handle_force_subscribe(self, update, context, callback_data: str = "check_subscription") -> bool:
        """
        Main handler for force subscribe
        Returns: True if user is subscribed, False otherwise
        """
        user_id = update.effective_user.id
        
        # Check subscription status
        is_subscribed, channel_link = await self.check_user_subscription(user_id, context)
        
        if is_subscribed:
            return True
        
        # User not subscribed, show force subscribe message
        message = self.get_force_subscribe_message()
        keyboard = self.get_force_subscribe_keyboard(channel_link, callback_data)
        
        try:
            if update.callback_query:
                await update.callback_query.answer(
                    "Please join our channel first! 📢",
                    show_alert=True
                )
                await update.callback_query.message.reply_text(
                    message,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            else:
                await update.message.reply_text(
                    message,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
        except Exception as e:
            logger.error(f"Error sending force subscribe message: {e}")
        
        return False
    
    async def check_multiple_channels(self, user_id: int, context, channels: list) -> Tuple[bool, list]:
        """
        Check subscription to multiple channels
        Returns: (all_subscribed, unsubscribed_channels)
        """
        unsubscribed = []
        
        for channel_id in channels:
            try:
                member = await context.bot.get_chat_member(
                    chat_id=channel_id,
                    user_id=user_id
                )
                
                if member.status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]:
                    unsubscribed.append(channel_id)
                    
            except Exception as e:
                logger.error(f"Error checking channel {channel_id}: {e}")
                # If error (e.g., chat not found), consider as not subscribed
                unsubscribed.append(channel_id)
        
        return len(unsubscribed) == 0, unsubscribed
