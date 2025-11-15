"""Telegram bot service for DRM key extraction"""
import logging
try:
    from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
from typing import Optional
import re
from datetime import datetime, timezone

from src.utils.platform_detector import detect_platform, is_license_url
from src.services.widevine.extractor import WidevineExtractor
import os

logger = logging.getLogger(__name__)

class TelegramBotService:
    """Telegram bot for Widevine key extraction"""
    
    def __init__(self, token: str, db):
        if not TELEGRAM_AVAILABLE:
            raise ImportError("Telegram library not available. Install with: pip install python-telegram-bot")
        self.token = token
        self.db = db
        self.application = None
        self.widevine_api_key = os.environ.get('WIDEVINE_API_KEY', 'wv_mock_key_12345')
    
    async def start(self):
        """Start the Telegram bot"""
        self.application = Application.builder().token(self.token).build()
        
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.cmd_start))
        self.application.add_handler(CommandHandler("help", self.cmd_help))
        self.application.add_handler(CommandHandler("extract", self.cmd_extract))
        self.application.add_handler(CommandHandler("history", self.cmd_history))
        self.application.add_handler(CommandHandler("config", self.cmd_config))
        self.application.add_handler(CommandHandler("platforms", self.cmd_platforms))
        
        # Message handler for text messages
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        # Callback query handler
        self.application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Start polling
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
    
    async def stop(self):
        """Stop the Telegram bot"""
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
    
    async def cmd_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = (
            "🔑 *Welcome to Widevine DRM Bot*\\!\n\n"
            "I can extract DRM keys from 30\\+ OTT platforms including:\n"
            "🇮🇳 Hotstar, Zee5, SonyLIV, JioCinema, Voot\n"
            "🌍 Netflix, Prime Video, Disney\\+, HBO Max\n\n"
            "*How to use:*\n"
            "1\\. Send me a video URL or license URL\n"
            "2\\. Provide PSSH data when asked\n"
            "3\\. Get your DRM keys instantly\\!\n\n"
            "*Commands:*\n"
            "/help \\- Show detailed help\n"
            "/extract \\- Extract keys manually\n"
            "/history \\- View extraction history\n"
            "/platforms \\- Supported platforms\n"
            "/config \\- Configure API key\n\n"
            "_Note: Currently using mock API for demo\\. Configure your Widevine API key for real extraction\\._"
        )
        
        keyboard = [
            [InlineKeyboardButton("📚 Help", callback_data="help"),
             InlineKeyboardButton("🔧 Extract Keys", callback_data="extract")],
            [InlineKeyboardButton("📊 History", callback_data="history"),
             InlineKeyboardButton("🌐 Platforms", callback_data="platforms")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_message,
            parse_mode='MarkdownV2',
            reply_markup=reply_markup
        )
    
    async def cmd_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = (
            "📖 *Detailed Help Guide*\n\n"
            "*Method 1: Automatic Extraction*\n"
            "Just send me a video URL and I\\'ll try to extract keys automatically\\!\n\n"
            "*Method 2: Manual Extraction*\n"
            "Use /extract command and provide:\n"
            "• PSSH \\(Protection System Specific Header\\)\n"
            "• License URL\n"
            "• Optional: Headers\n\n"
            "*Example:*\n"
            "`PSSH: AAAANHBzc2gAAAAA...`\n"
            "`License URL: https://api\\.platform\\.com/license`\n\n"
            "*Getting PSSH:*\n"
            "• Use browser developer tools\n"
            "• Check network requests for EME API calls\n"
            "• Look for base64 encoded PSSH data\n\n"
            "*Supported Platforms:*\n"
            "Use /platforms to see full list\n\n"
            "_Need more help\\? Contact support\\._"
        )
        
        await update.message.reply_text(help_text, parse_mode='MarkdownV2')
    
    async def cmd_extract(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /extract command"""
        await update.message.reply_text(
            "🔧 *Manual Extraction Mode*\n\n"
            "Please provide the following information:\n\n"
            "*Format:*\n"
            "`PSSH: <your_pssh_here>`\n"
            "`License: <license_url_here>`\n\n"
            "Or send them line by line\\.",
            parse_mode='MarkdownV2'
        )
        
        # Store extraction mode in user context
        context.user_data['extraction_mode'] = True
    
    async def cmd_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /history command"""
        user_id = str(update.effective_user.id)
        
        # Get last 5 extractions for this user
        extractions = await self.db.extractions.find(
            {"user_id": user_id},
            {"_id": 0}
        ).sort("timestamp", -1).limit(5).to_list(5)
        
        if not extractions:
            await update.message.reply_text(
                "📊 *Extraction History*\n\n"
                "No extractions found\\. Start extracting keys to build your history\\!",
                parse_mode='MarkdownV2'
            )
            return
        
        history_text = "📊 *Recent Extractions*\n\n"
        
        for i, ext in enumerate(extractions, 1):
            status = "✅" if ext.get('success') else "❌"
            platform = ext.get('platform', 'Unknown')
            timestamp = ext.get('timestamp', '')
            keys_count = len(ext.get('keys', []))
            
            history_text += f"{status} *{platform}*\n"
            history_text += f"   Keys: {keys_count}\n"
            history_text += f"   Time: {timestamp[:19] if isinstance(timestamp, str) else timestamp}\n\n"
        
        await update.message.reply_text(history_text, parse_mode='MarkdownV2')
    
    async def cmd_config(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /config command"""
        config_text = (
            "⚙️ *Configuration*\n\n"
            "*Current Status:*\n"
            "API Mode: Mock \\(Demo\\)\n\n"
            "*To use real Widevine API:*\n"
            "Set your API key in environment:\n"
            "`WIDEVINE_API_KEY=wv_your_key_here`\n\n"
            "_Contact admin for API key access\\._"
        )
        
        await update.message.reply_text(config_text, parse_mode='MarkdownV2')
    
    async def cmd_platforms(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /platforms command"""
        platforms_text = (
            "🌐 *Supported Platforms*\n\n"
            "*Indian OTT:*\n"
            "🇮🇳 Hotstar, Zee5, SonyLIV, SunNXT\n"
            "🇮🇳 Aha Video, JioCinema, Voot\n"
            "🇮🇳 MX Player, Eros Now, ALTBalaji\n\n"
            "*International OTT:*\n"
            "🌍 Netflix, Prime Video, Disney\\+\n"
            "🌍 HBO Max, Hulu\n\n"
            "*Demo Platforms:*\n"
            "🎬 Shaka Player Demo\n"
            "🎬 Bitmovin Demo\n\n"
            "_\\+ Many more platforms supported\\!_"
        )
        
        await update.message.reply_text(platforms_text, parse_mode='MarkdownV2')
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        message_text = update.message.text
        user_id = str(update.effective_user.id)
        
        # Check if in extraction mode
        if context.user_data.get('extraction_mode'):
            await self.process_extraction_input(update, context, message_text)
            return
        
        # Try to detect if message contains extraction data
        if 'pssh' in message_text.lower() or 'license' in message_text.lower():
            await self.process_extraction_input(update, context, message_text)
        elif message_text.startswith('http'):
            # Try to detect platform from URL
            platform = detect_platform(message_text)
            await update.message.reply_text(
                f"🔍 Detected platform: *{platform}*\n\n"
                "To extract keys, please provide PSSH data\\.",
                parse_mode='MarkdownV2'
            )
        else:
            await update.message.reply_text(
                "I didn\\'t understand that\\. Use /help to see available commands\\.",
                parse_mode='MarkdownV2'
            )
    
    async def process_extraction_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Process extraction input from user"""
        user_id = str(update.effective_user.id)
        
        # Parse PSSH and License URL from text
        pssh_match = re.search(r'pssh[:\s]+([A-Za-z0-9+/=]+)', text, re.IGNORECASE)
        license_match = re.search(r'license[:\s]+(https?://[^\s]+)', text, re.IGNORECASE)
        
        if not pssh_match or not license_match:
            await update.message.reply_text(
                "⚠️ Please provide both PSSH and License URL\\."
            )
            return
        
        pssh = pssh_match.group(1)
        license_url = license_match.group(1)
        
        # Show processing message
        processing_msg = await update.message.reply_text(
            "⏳ Extracting keys\\.\\.\\. Please wait\\."
        )
        
        try:
            # Extract keys
            extractor = WidevineExtractor(self.widevine_api_key)
            platform = detect_platform(license_url)
            
            result = await extractor.extract_keys(
                pssh=pssh,
                license_url=license_url
            )
            
            # Save to database
            extraction_doc = {
                'user_id': user_id,
                'success': result['success'],
                'keys': result.get('keys', []),
                'error': result.get('error'),
                'platform': platform,
                'pssh': pssh[:50] + '...',  # Truncate for storage
                'license_url': license_url,
                'timestamp': datetime.now(timezone.utc).isoformat()
            }
            
            await self.db.extractions.insert_one(extraction_doc)
            
            # Format response
            if result['success']:
                keys_text = "✅ *Keys Extracted Successfully\\!*\n\n"
                keys_text += f"*Platform:* {platform}\n"
                keys_text += f"*Keys Found:* {len(result['keys'])}\n\n"
                
                for i, key_data in enumerate(result['keys'], 1):
                    keys_text += f"*Key {i}:*\n"
                    keys_text += f"`KID: {key_data['kid']}`\n"
                    keys_text += f"`KEY: {key_data['key']}`\n\n"
                
                await processing_msg.edit_text(keys_text, parse_mode='MarkdownV2')
            else:
                error_msg = result.get('error', 'Unknown error')
                await processing_msg.edit_text(
                    f"❌ *Extraction Failed*\n\n"
                    f"Error: {error_msg}",
                    parse_mode='MarkdownV2'
                )
        
        except Exception as e:
            logger.error(f"Extraction error: {str(e)}")
            await processing_msg.edit_text(
                f"❌ *Error*\n\nFailed to extract keys: {str(e)}"
            )
        
        finally:
            # Clear extraction mode
            context.user_data['extraction_mode'] = False
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "help":
            await self.cmd_help(update, context)
        elif query.data == "extract":
            await self.cmd_extract(update, context)
        elif query.data == "history":
            await self.cmd_history(update, context)
        elif query.data == "platforms":
            await self.cmd_platforms(update, context)