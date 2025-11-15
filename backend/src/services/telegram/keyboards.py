"""Inline keyboard layouts for Telegram bot"""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def get_main_menu_keyboard():
    """Get the main menu with 8 options"""
    keyboard = [
        [
            InlineKeyboardButton("🎬 OTT Explorer", callback_data="menu_ott_explorer"),
            InlineKeyboardButton("💰 Compare Plans", callback_data="menu_compare_plans")
        ],
        [
            InlineKeyboardButton("🔔 Release Alerts", callback_data="menu_release_alerts"),
            InlineKeyboardButton("📊 Dashboard", callback_data="menu_dashboard")
        ],
        [
            InlineKeyboardButton("💵 Subscriptions", callback_data="menu_subscriptions"),
            InlineKeyboardButton("👑 Admin Panel", callback_data="menu_admin")
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="menu_settings"),
            InlineKeyboardButton("🆘 Help & Support", callback_data="menu_help")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_ott_explorer_keyboard():
    """OTT Explorer submenu - 5 features"""
    keyboard = [
        [InlineKeyboardButton("🔍 Browse Latest", callback_data="ott_browse")],
        [InlineKeyboardButton("🎭 Filter by Genre/Language", callback_data="ott_filter")],
        [InlineKeyboardButton("📺 Platform Availability", callback_data="ott_availability")],
        [InlineKeyboardButton("🎥 Watch Trailers", callback_data="ott_trailers")],
        [InlineKeyboardButton("⭐ My Watchlist", callback_data="ott_watchlist")],
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_compare_plans_keyboard():
    """Compare Plans submenu - 5 features"""
    keyboard = [
        [InlineKeyboardButton("💳 Compare All Platforms", callback_data="compare_all")],
        [InlineKeyboardButton("🎁 Active Offers & Discounts", callback_data="compare_offers")],
        [InlineKeyboardButton("🔽 Filter Plans", callback_data="compare_filter")],
        [InlineKeyboardButton("🏆 Best Value Recommendation", callback_data="compare_best")],
        [InlineKeyboardButton("📈 Price History", callback_data="compare_history")],
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_release_alerts_keyboard():
    """Release Alerts submenu - 5 features"""
    keyboard = [
        [InlineKeyboardButton("➕ Subscribe to Alerts", callback_data="alerts_subscribe")],
        [InlineKeyboardButton("⏰ Set Frequency", callback_data="alerts_frequency")],
        [InlineKeyboardButton("🕐 Custom Timing", callback_data="alerts_timing")],
        [InlineKeyboardButton("🔥 Trending Now", callback_data="alerts_trending")],
        [InlineKeyboardButton("📋 My Alerts", callback_data="alerts_my")],
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_dashboard_keyboard():
    """User Dashboard submenu - 5 features"""
    keyboard = [
        [InlineKeyboardButton("📅 Subscription Expiry", callback_data="dash_expiry")],
        [InlineKeyboardButton("💸 Money Spent", callback_data="dash_spent")],
        [InlineKeyboardButton("🔔 Renewal Reminders", callback_data="dash_reminders")],
        [InlineKeyboardButton("📚 Watchlist & History", callback_data="dash_watchlist")],
        [InlineKeyboardButton("📄 Export Data (PDF)", callback_data="dash_export")],
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_subscriptions_keyboard():
    """Subscriptions menu"""
    keyboard = [
        [InlineKeyboardButton("📅 Weekly Plan", callback_data="sub_weekly")],
        [InlineKeyboardButton("📆 Monthly Plan", callback_data="sub_monthly")],
        [InlineKeyboardButton("🎯 Custom Bundle", callback_data="sub_custom")],
        [InlineKeyboardButton("📜 My Active Subscriptions", callback_data="sub_active")],
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_admin_panel_keyboard():
    """Admin Panel menu"""
    keyboard = [
        [InlineKeyboardButton("➕ Add/Remove Platform", callback_data="admin_platforms")],
        [InlineKeyboardButton("👥 Manage Users", callback_data="admin_users")],
        [InlineKeyboardButton("✅ Verify Payments", callback_data="admin_verify")],
        [InlineKeyboardButton("📢 Send Announcement", callback_data="admin_announce")],
        [InlineKeyboardButton("📊 Revenue Reports", callback_data="admin_reports")],
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_settings_keyboard():
    """Settings menu - 5 features"""
    keyboard = [
        [InlineKeyboardButton("🌍 OTT Region", callback_data="settings_region")],
        [InlineKeyboardButton("🎭 Default Genres/Languages", callback_data="settings_preferences")],
        [InlineKeyboardButton("🔔 Notifications", callback_data="settings_notifications")],
        [InlineKeyboardButton("📱 Connected Devices", callback_data="settings_devices")],
        [InlineKeyboardButton("🗑️ Delete Account", callback_data="settings_delete")],
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_help_keyboard():
    """Help & Support menu - 5 features"""
    keyboard = [
        [InlineKeyboardButton("❓ FAQs", callback_data="help_faq")],
        [InlineKeyboardButton("💬 Contact Admin", callback_data="help_contact")],
        [InlineKeyboardButton("🐛 Report Issue", callback_data="help_report")],
        [InlineKeyboardButton("👥 Community Group", url="https://t.me/otthelp")],
        [InlineKeyboardButton("📜 Terms & Privacy", callback_data="help_terms")],
        [InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_payment_confirmation_keyboard(payment_id: str):
    """Keyboard for payment confirmation"""
    keyboard = [
        [InlineKeyboardButton("✅ Upload Payment Screenshot", callback_data=f"payment_upload_{payment_id}")],
        [InlineKeyboardButton("❌ Cancel", callback_data="payment_cancel")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_back_button():
    """Simple back button"""
    keyboard = [[InlineKeyboardButton("⬅️ Back to Menu", callback_data="back_to_menu")]]
    return InlineKeyboardMarkup(keyboard)
