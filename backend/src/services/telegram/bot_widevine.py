"""Widevine extraction and quality selection handlers for Telegram bot"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
import httpx
import os

logger = logging.getLogger(__name__)

# Backend URL from environment
BACKEND_URL = os.environ.get('REACT_APP_BACKEND_URL', 'http://localhost:8001')


class WidevineHandlers:
    """Handlers for Widevine DRM extraction with quality selection"""
    
    @staticmethod
    async def start_extraction(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start extraction process"""
        text = """
🔑 **Widevine Key Extraction**

To extract DRM keys, please provide:

1️⃣ **PSSH** (Protection System Specific Header)
2️⃣ **License URL** (DRM license server URL)
3️⃣ **Manifest URL** (Optional - for quality detection)

**Example:**
PSSH: `AAAAW3Bzc2gAAAAA7e+LqXnWSs6jyCfc1R0h7QAAADsIARIQ62dqu8s0Xpa7z2FmMPGj2hoNd2lkZXZpbmVfdGVzdCIQZmtqM2xqYVNkZmFsa3IzaioCSEQyAA==`

License URL: `https://www.hotstar.com/drm/license`

Please send your PSSH first.
"""
        
        keyboard = [[InlineKeyboardButton("📊 Check My Quota", callback_data="check_quota")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        context.user_data['extraction_step'] = 'waiting_for_pssh'
    
    @staticmethod
    async def handle_extraction_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle user input during extraction process"""
        user = update.effective_user
        text = update.message.text
        
        step = context.user_data.get('extraction_step')
        
        if step == 'waiting_for_pssh':
            context.user_data['pssh'] = text
            context.user_data['extraction_step'] = 'waiting_for_license_url'
            await update.message.reply_text(
                "✅ PSSH received!\n\nNow send the **License URL**:",
                parse_mode="Markdown"
            )
        
        elif step == 'waiting_for_license_url':
            context.user_data['license_url'] = text
            context.user_data['extraction_step'] = 'waiting_for_manifest_url'
            
            keyboard = [
                [InlineKeyboardButton("⏭️ Skip Manifest URL", callback_data="skip_manifest")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel_extraction")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(
                "✅ License URL received!\n\n"
                "Send the **Manifest URL** (optional - helps detect video qualities)\n"
                "or tap 'Skip' to continue without it:",
                reply_markup=reply_markup,
                parse_mode="Markdown"
            )
        
        elif step == 'waiting_for_manifest_url':
            context.user_data['manifest_url'] = text
            await WidevineHandlers.perform_extraction(update, context)
    
    @staticmethod
    async def perform_extraction(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Perform the actual extraction"""
        user = update.effective_user
        
        # Show processing message
        processing_msg = await update.message.reply_text(
            "🔄 **Extracting keys and detecting qualities...**\n\n"
            "Please wait...",
            parse_mode="Markdown"
        )
        
        try:
            # Prepare extraction request
            pssh = context.user_data.get('pssh')
            license_url = context.user_data.get('license_url')
            manifest_url = context.user_data.get('manifest_url')
            
            payload = {
                'pssh': pssh,
                'license_url': license_url,
                'manifest_url': manifest_url,
                'telegram_id': user.id,
                'headers': {}
            }
            
            # Call backend API
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{BACKEND_URL}/api/extract",
                    json=payload
                )
                
                if response.status_code == 429:
                    await processing_msg.edit_text(
                        "⚠️ **Daily Limit Reached**\n\n"
                        f"{response.json().get('detail', 'You have reached your daily extraction limit.')}\n\n"
                        "Upgrade to premium for more extractions!",
                        parse_mode="Markdown"
                    )
                    return
                
                if response.status_code != 200:
                    error_detail = response.json().get('detail', 'Unknown error')
                    await processing_msg.edit_text(
                        f"❌ **Extraction Failed**\n\n"
                        f"Error: {error_detail}",
                        parse_mode="Markdown"
                    )
                    return
                
                result = response.json()
            
            # Build response message
            if result['success']:
                extraction_id = result['extraction_id']
                platform = result['platform']
                keys = result['keys']
                qualities = result.get('available_qualities', [])
                recommended = result.get('recommended_quality', '720p')
                
                # Format keys
                keys_text = ""
                for i, key_data in enumerate(keys[:5], 1):  # Show max 5 keys
                    keys_text += f"**Key {i}:**\n"
                    keys_text += f"`{key_data['kid']}:{key_data['key']}`\n\n"
                
                # Format qualities
                qualities_text = ""
                if qualities:
                    qualities_text = "\n\n📊 **Available Qualities:**\n"
                    for q in qualities:
                        size_info = f" ({q.get('file_size_mb', 0):.0f} MB)" if q.get('file_size_mb') else ""
                        recommended_mark = " ⭐" if q['quality_id'] == recommended else ""
                        qualities_text += f"• {q['quality_id']} - {q['resolution']}{size_info}{recommended_mark}\n"
                
                message = f"""
✅ **Extraction Successful!**

🎬 **Platform:** {platform}

🔑 **DRM Keys:**
{keys_text}

**Extraction ID:** `{extraction_id}`
{qualities_text}

Select a quality to download:
"""
                
                # Create quality selection keyboard
                keyboard = []
                if qualities:
                    quality_buttons = []
                    for q in qualities:
                        quality_buttons.append(
                            InlineKeyboardButton(
                                f"{q['quality_id']}", 
                                callback_data=f"download_{extraction_id}_{q['quality_id']}"
                            )
                        )
                    
                    # Split into rows of 3
                    for i in range(0, len(quality_buttons), 3):
                        keyboard.append(quality_buttons[i:i+3])
                
                keyboard.append([InlineKeyboardButton("📋 View All Extractions", callback_data="view_extractions")])
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await processing_msg.edit_text(message, reply_markup=reply_markup, parse_mode="Markdown")
                
                # Store extraction_id for later
                context.user_data['last_extraction_id'] = extraction_id
                
            else:
                error_msg = result.get('error', 'Unknown error')
                await processing_msg.edit_text(
                    f"❌ **Extraction Failed**\n\n"
                    f"Error: {error_msg}",
                    parse_mode="Markdown"
                )
        
        except Exception as e:
            logger.error(f"Extraction error: {e}")
            await processing_msg.edit_text(
                f"❌ **Error**\n\n"
                f"An error occurred: {str(e)}",
                parse_mode="Markdown"
            )
        
        finally:
            # Clear extraction data
            context.user_data['extraction_step'] = None
    
    @staticmethod
    async def handle_quality_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle quality selection for download"""
        query = update.callback_query
        await query.answer()
        
        # Parse callback data: download_{extraction_id}_{quality}
        parts = query.data.split('_')
        if len(parts) < 3:
            await query.edit_message_text("❌ Invalid selection")
            return
        
        extraction_id = parts[1]
        quality = parts[2]
        
        # Show downloading message
        await query.edit_message_text(
            f"📥 **Preparing Download**\n\n"
            f"Quality: {quality}\n"
            f"Extraction ID: `{extraction_id}`\n\n"
            f"Please wait...",
            parse_mode="Markdown"
        )
        
        try:
            # Request download
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{BACKEND_URL}/api/download",
                    json={
                        'extraction_id': extraction_id,
                        'quality': quality,
                        'telegram_id': query.from_user.id
                    }
                )
                
                if response.status_code != 200:
                    error_detail = response.json().get('detail', 'Download failed')
                    await query.edit_message_text(
                        f"❌ **Download Failed**\n\n{error_detail}",
                        parse_mode="Markdown"
                    )
                    return
                
                result = response.json()
            
            # Show download info
            quality_details = result.get('quality_details', {})
            download_info = result.get('download_info', {})
            
            message = f"""
✅ **Download Ready!**

📺 **Quality:** {quality}
📐 **Resolution:** {quality_details.get('resolution', 'N/A')}
💾 **Estimated Size:** {download_info.get('estimated_size_mb', 0):.0f} MB
⏱️ **Estimated Time:** {download_info.get('estimated_time_seconds', 0)} seconds

**Note:** This is a mock implementation.
In production, you would receive download links or the video file.

Use the extraction keys shown earlier with your video downloader tool.
"""
            
            keyboard = [
                [InlineKeyboardButton("🔄 New Extraction", callback_data="new_extraction")],
                [InlineKeyboardButton("📋 My History", callback_data="view_extractions")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Download request error: {e}")
            await query.edit_message_text(
                f"❌ **Error**\n\n{str(e)}",
                parse_mode="Markdown"
            )
    
    @staticmethod
    async def check_quota(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check user's quota status"""
        query = update.callback_query
        await query.answer()
        
        user = query.from_user
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(f"{BACKEND_URL}/api/user/quota/{user.id}")
                
                if response.status_code != 200:
                    await query.edit_message_text("❌ Failed to fetch quota information")
                    return
                
                quota = response.json()
            
            message = f"""
📊 **Your Quota Status**

**Daily Limit:** {quota['daily_limit']} extractions
**Used Today:** {quota['used_today']}
**Remaining:** {quota['remaining']}

**Resets at:** {quota['resets_at'].split('T')[0]} 00:00 UTC

{'✅ You have available extractions!' if quota['remaining'] > 0 else '⚠️ Daily limit reached. Resets tomorrow.'}
"""
            
            keyboard = [[InlineKeyboardButton("🔄 Start New Extraction", callback_data="new_extraction")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"Quota check error: {e}")
            await query.edit_message_text(f"❌ Error: {str(e)}", parse_mode="Markdown")
    
    @staticmethod
    async def view_extractions(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """View user's extraction history"""
        query = update.callback_query
        await query.answer()
        
        user = query.from_user
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{BACKEND_URL}/api/extractions",
                    params={'telegram_id': user.id, 'limit': 10}
                )
                
                if response.status_code != 200:
                    await query.edit_message_text("❌ Failed to fetch extraction history")
                    return
                
                extractions = response.json()
            
            if not extractions:
                message = "📋 **Extraction History**\n\nNo extractions yet. Start your first extraction!"
            else:
                message = "📋 **Your Recent Extractions**\n\n"
                for i, ext in enumerate(extractions[:5], 1):
                    platform = ext['platform']
                    success = "✅" if ext['success'] else "❌"
                    timestamp = ext['timestamp'].split('T')[0]
                    qualities_count = len(ext.get('available_qualities', []))
                    
                    message += f"{i}. {success} {platform} - {qualities_count} qualities\n"
                    message += f"   Date: {timestamp}\n\n"
            
            keyboard = [[InlineKeyboardButton("🔄 New Extraction", callback_data="new_extraction")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode="Markdown")
            
        except Exception as e:
            logger.error(f"History fetch error: {e}")
            await query.edit_message_text(f"❌ Error: {str(e)}", parse_mode="Markdown")
