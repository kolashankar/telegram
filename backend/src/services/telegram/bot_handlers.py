"""
Bot handler implementations for all features
This file contains the implementation logic for all menu options
"""
from datetime import datetime, timedelta
from telegram import Update
from telegram.ext import ContextTypes
from .keyboards import get_back_button
from ...services.ott.platform_data import get_all_platforms
import logging

logger = logging.getLogger(__name__)


# Mixins for bot handlers - to be mixed into OTTBot class
class OTTExplorerHandlers:
    """Handlers for OTT Explorer feature"""
    
    async def handle_ott_browse(self, query):
        """Browse latest movies and shows"""
        # Mock data for demonstration
        content_list = [
            "🎬 The Last of Us S02 - HBO Max, Prime Video",
            "🎬 Pathaan - Netflix, Prime Video, Hotstar",
            "🎬 Wednesday S02 - Netflix",
            "🎬 The Night Manager - Hotstar",
            "🎬 Farzi - Prime Video"
        ]
        
        text = "🎬 **Latest Movies & Shows**\n\n"
        text += "\n".join(content_list)
        text += "\n\n💡 Tip: Add items to your watchlist!"
        
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    
    async def handle_ott_filter(self, query):
        """Filter content by genre/language"""
        text = """
🎭 **Filter Content**

**Popular Genres:**
• Action
• Comedy
• Drama
• Thriller
• Romance
• Horror
• Sci-Fi
• Documentary

**Languages:**
• Hindi
• English
• Tamil
• Telugu
• Malayalam
• Kannada

Send me your preference (e.g., "Action English") to filter!
"""
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    
    async def handle_ott_availability(self, query):
        """Show platform availability"""
        platforms = get_all_platforms()
        
        text = "📺 **OTT Platform Availability**\n\n"
        text += f"**Total Platforms:** {len(platforms)}\n\n"
        
        # Indian platforms
        indian = [p for p in platforms if p['country'] == 'India']
        text += f"🇮🇳 **Indian Platforms:** {len(indian)}\n"
        for p in indian[:5]:
            text += f"• {p['icon']} {p['display_name']}\n"
        
        # Global platforms
        global_p = [p for p in platforms if p['country'] in ['Global', 'USA']]
        text += f"\n🌍 **International Platforms:** {len(global_p)}\n"
        for p in global_p[:5]:
            text += f"• {p['icon']} {p['display_name']}\n"
        
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    
    async def handle_ott_trailers(self, query):
        """Watch trailers"""
        text = """
🎥 **Watch Trailers**

Popular trailers:

🎬 **Pathaan** - https://youtu.be/demo123
🎬 **The Last of Us** - https://youtu.be/demo456
🎬 **Wednesday** - https://youtu.be/demo789

💡 Send me a movie/show name to get its trailer link!
"""
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    
    async def handle_ott_watchlist(self, query):
        """Show user watchlist"""
        user_id = query.from_user.id
        
        # Fetch watchlist from database
        watchlist_data = await self.watchlists_collection.find_one({"telegram_id": user_id})
        
        if not watchlist_data or not watchlist_data.get("items"):
            text = """
⭐ **Your Watchlist**

Your watchlist is empty!

Start adding movies and shows you want to watch.
"""
        else:
            items = watchlist_data["items"]
            text = f"⭐ **Your Watchlist** ({len(items)} items)\n\n"
            for item in items[:10]:
                text += f"• {item.get('title', 'Unknown')}\n"
        
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )


class ComparePlansHandlers:
    """Handlers for Compare Plans feature"""
    
    async def handle_compare_all(self, query):
        """Compare all platforms"""
        platforms = get_all_platforms()
        
        text = "💰 **Compare All Platforms**\n\n"
        
        for platform in platforms[:10]:
            text += f"**{platform['icon']} {platform['display_name']}**\n"
            
            if platform.get('mobile_plan'):
                text += f"  📱 Mobile: ₹{platform['mobile_plan']}/year\n"
            if platform.get('monthly_plan'):
                text += f"  📅 Monthly: ₹{platform['monthly_plan']}/month\n"
            if platform.get('yearly_plan'):
                text += f"  📆 Yearly: ₹{platform['yearly_plan']}/year\n"
            if platform.get('family_plan'):
                text += f"  👨‍👩‍👧‍👦 Family: ₹{platform['family_plan']}/month\n"
            
            text += "\n"
        
        text += "\n*Showing 10 of 30+ platforms*"
        
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    
    async def handle_compare_offers(self, query):
        """Show active offers"""
        text = """
🎁 **Active Offers & Discounts**

🔥 **Hot Deals:**
• Netflix - 20% off on yearly plan
• Prime Video - Free trial for 30 days
• Hotstar - Student discount 50% off
• Zee5 - Annual plan at ₹699 (was ₹999)

💡 Grab these deals before they expire!
"""
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    
    async def handle_compare_filter(self, query):
        """Filter plans"""
        text = """
🔽 **Filter Plans**

**Filter by Type:**
• Monthly plans only
• Yearly plans only
• Mobile plans only
• Family plans only
• Student discounts available

**Filter by Price Range:**
• Under ₹100
• ₹100 - ₹500
• ₹500 - ₹1000
• Above ₹1000

Send your preference to filter!
"""
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    
    async def handle_compare_best(self, query):
        """Best value recommendation"""
        text = """
🏆 **Best Value Recommendations**

Based on content library and price:

**🥇 Best Overall:**
Prime Video - ₹1499/year
✅ Huge content library
✅ Free Prime delivery
✅ Hindi & English content

**🥈 Best for Sports:**
Hotstar - ₹1499/year
✅ Live cricket & sports
✅ Disney+ content
✅ Regional languages

**🥉 Best Budget:**
JioCinema - ₹999/year
✅ Affordable pricing
✅ Good content mix
✅ Live sports

**🎯 Best Bundle:**
Netflix + Prime + Hotstar = ₹4497/year
All major content in one combo!
"""
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    
    async def handle_compare_history(self, query):
        """Price history"""
        text = """
📈 **Price History**

**Netflix:**
• 2023: ₹649/month → 2024: ₹649/month
• No change in last year

**Prime Video:**
• 2023: ₹1499/year → 2024: ₹1499/year  
• Stable pricing

**Hotstar:**
• 2023: ₹1499/year → 2024: ₹1499/year
• New mobile plan added at ₹499

💡 Most platforms maintained stable pricing in 2024!
"""
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )


class ReleaseAlertsHandlers:
    """Handlers for Release Alerts feature"""
    
    async def handle_alerts_subscribe(self, query):
        """Subscribe to alerts"""
        text = """
✅ **Subscribe to Release Alerts**

Get notified about new releases!

**Choose what to track:**
• Specific genres (Action, Drama, Comedy, etc.)
• Specific platforms (Netflix, Prime, Hotstar, etc.)
• Specific languages (Hindi, English, etc.)
• All releases

Send me your preferences!
Example: "Action English Netflix"
"""
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    
    async def handle_alerts_frequency(self, query):
        """Set alert frequency"""
        text = """
⏰ **Set Alert Frequency**

How often should I notify you?

• **Daily** - Get updates every day
• **Weekly** - Weekly roundup on Sundays
• **Instant** - Immediate alerts for new releases
• **Custom** - Set your own schedule

Send me your preference!
"""
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    
    async def handle_alerts_timing(self, query):
        """Custom alert timing"""
        text = """
🕐 **Custom Alert Timing**

Choose when to receive alerts:

**Morning:** 9:00 AM
**Afternoon:** 2:00 PM  
**Evening:** 6:00 PM
**Night:** 9:00 PM
**Custom:** Send me time (e.g., "11:30 AM")

What time works best for you?
"""
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    
    async def handle_alerts_trending(self, query):
        """Show trending releases"""
        text = """
🔥 **Trending Now**

**This Week's Hot Releases:**

1️⃣ **Pathaan** (Movie)
   Netflix, Prime - Action, Hindi
   ⭐ 4.5/5

2️⃣ **The Last of Us S02** (Series)
   HBO Max, Prime - Drama, English
   ⭐ 4.8/5

3️⃣ **Farzi** (Series)
   Prime Video - Thriller, Hindi
   ⭐ 4.3/5

4️⃣ **Wednesday S02** (Series)
   Netflix - Mystery, English
   ⭐ 4.6/5

5️⃣ **The Night Manager** (Series)
   Hotstar - Thriller, Hindi/English
   ⭐ 4.4/5
"""
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    
    async def handle_alerts_my(self, query):
        """Show user's alerts"""
        user_id = query.from_user.id
        
        alert_data = await self.alerts_collection.find_one({"telegram_id": user_id})
        
        if not alert_data:
            text = """
📋 **My Alerts**

You haven't subscribed to any alerts yet!

Use "Subscribe to Alerts" to start receiving notifications.
"""
        else:
            text = "📋 **My Alerts**\n\n"
            text += f"**Frequency:** {alert_data.get('frequency', 'daily')}\n"
            text += f"**Timing:** {alert_data.get('notification_time', '09:00')}\n"
            text += f"**Genres:** {', '.join(alert_data.get('genres', ['All']))}\n"
            text += f"**Platforms:** {', '.join(alert_data.get('platforms', ['All']))}\n"
            text += f"**Languages:** {', '.join(alert_data.get('languages', ['All']))}\n"
            text += f"\n**Status:** {'🟢 Active' if alert_data.get('is_active') else '🔴 Inactive'}"
        
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )


class DashboardHandlers:
    """Handlers for User Dashboard feature"""
    
    async def handle_dash_expiry(self, query):
        """Show subscription expiry"""
        user_id = query.from_user.id
        
        user_data = await self.users_collection.find_one({"telegram_id": user_id})
        
        if not user_data or not user_data.get('active_subscriptions'):
            text = """
📅 **Subscription Expiry**

You don't have any active subscriptions.

Visit "Subscriptions" menu to purchase a plan!
"""
        else:
            text = "📅 **Your Active Subscriptions**\n\n"
            
            for sub in user_data['active_subscriptions']:
                if sub.get('is_active'):
                    expiry = datetime.fromisoformat(sub['expiry_date'])
                    days_left = (expiry - datetime.utcnow()).days
                    
                    status_emoji = "🟢" if days_left > 7 else "🟡" if days_left > 3 else "🔴"
                    
                    text += f"{status_emoji} **{sub['plan_type'].title()} Plan**\n"
                    text += f"  Platforms: {', '.join(sub['platforms'][:3])}\n"
                    text += f"  Expires: {expiry.strftime('%d %b %Y')}\n"
                    text += f"  Days left: {days_left} days\n\n"
        
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    
    async def handle_dash_spent(self, query):
        """Show money spent"""
        user_id = query.from_user.id
        
        user_data = await self.users_collection.find_one({"telegram_id": user_id})
        
        total_spent = user_data.get('total_spent', 0) if user_data else 0
        
        # Get payment history
        payments = await self.payment_service.get_user_payments(user_data.get('user_id', ''))
        
        text = f"""
💸 **Money Spent**

**Total Spent:** ₹{total_spent}
**Verified Payments:** {len([p for p in payments if p.status == 'verified'])}
**Pending Payments:** {len([p for p in payments if p.status == 'pending'])}

**Recent Transactions:**
"""
        
        for payment in payments[:5]:
            status_emoji = "✅" if payment.status == "verified" else "⏳" if payment.status == "pending" else "❌"
            text += f"\n{status_emoji} ₹{payment.amount} - {payment.plan_type}"
        
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    
    async def handle_dash_reminders(self, query):
        """Renewal reminders"""
        text = """
🔔 **Renewal Reminders**

**Automatic Reminders:**
• 7 days before expiry
• 3 days before expiry
• 1 day before expiry
• On expiry day

You'll receive a Telegram notification for each reminder.

💡 Enable notifications to never miss a renewal!
"""
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    
    async def handle_dash_watchlist(self, query):
        """Combined watchlist and history"""
        user_id = query.from_user.id
        
        watchlist_data = await self.watchlists_collection.find_one({"telegram_id": user_id})
        
        text = "📚 **Watchlist & History**\n\n"
        
        if watchlist_data and watchlist_data.get('items'):
            text += "**Your Watchlist:**\n"
            for item in watchlist_data['items'][:5]:
                text += f"• {item.get('title', 'Unknown')}\n"
        else:
            text += "**Watchlist:** Empty\n"
        
        text += "\n💡 Add shows to your watchlist from OTT Explorer!"
        
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
    
    async def handle_dash_export(self, query):
        """Export data to PDF"""
        text = """
📄 **Export Data**

Generate a PDF report containing:
• Subscription history
• Payment records
• Watchlist
• Money spent analysis
• Platform usage stats

**Generating your report...**

⏳ This will take a few seconds.

(Feature in development - PDF will be sent shortly!)
"""
        await query.edit_message_text(
            text,
            reply_markup=get_back_button(),
            parse_mode="Markdown"
        )
