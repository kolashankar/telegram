# 🤖 Enhanced OTT Telegram Bot - Complete Guide

## 📋 Overview

The Enhanced OTT Bot is a comprehensive Telegram bot for managing OTT (Over-The-Top) platform subscriptions with premium features, referral system, and administrative controls.

## 🌟 Key Features

### 1. **Force Subscribe System**
- Users must join specified channels before accessing the bot
- Two modes: Instant Join or Request-to-Join
- Automatic verification of channel membership
- Customizable try-again buttons

### 2. **Premium Subscription Plans**
Four subscription tiers available:
- **1 Week** - ₹30 (7 days access)
- **1 Month** - ₹50 (30 days access)  
- **3 Months** - ₹120 (90 days access)
- **6 Months** - ₹220 (180 days access)

**Premium Benefits:**
- Unlimited OTT platform access
- No ads or verification required
- Direct file access
- High-speed streaming
- Priority support
- Early access to new content

### 3. **Referral Rewards System**
- Unique referral code for each user
- Track referrals in real-time
- Earn FREE premium: 20 valid referrals = 1 month premium
- Automatic reward claiming
- View referral list and statistics

### 4. **Payment System**
- UPI payment integration
- QR code for easy payment
- Screenshot upload for verification
- Admin approval workflow
- Automatic premium activation
- Payment history tracking

### 5. **IMDB Integration**
- Movie and series information lookup
- Ratings, genres, and cast details
- OTT platform availability
- Trending content discovery
- Ready for TMDb API integration

### 6. **Admin Features**
- Quick payment approval/rejection
- User management from Telegram
- Broadcast messaging
- Admin notifications with screenshots
- Logging to admin channel

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Bot Credentials
API_ID="24271861"
API_HASH="fc5e782b934ed58b28780f41f01ed024"
BOT_TOKEN="your_telegram_bot_token_here"

# Database
DATABASE_URI="mongodb+srv://..."
DATABASE_NAME="techvjautobot"

# Channels & Groups
LOG_CHANNEL="-1002409317177"
AUTH_CHANNEL="-1001710985956"  # Force subscribe channel
ADMINS="1636733122"
CHANNELS="-1002309517928"

# Premium Settings
PREMIUM_AND_REFERAL_MODE="True"
REFERAL_COUNT="20"
REFERAL_PREMEIUM_TIME="1month"
PAYMENT_QR="https://envs.sh/L-M.jpg"
OWNER_USERNAME="Shankar_Kola"

# Links
GRP_LNK="https://t.me/chillbot_movie"
CHNL_LNK="https://t.me/+nsKuewNAKQtkMGJl"
TUTORIAL="https://t.me/how_to_open_link_time2chill"
SUPPORT_CHAT="time2chill_discussion"

# Features
IMDB="True"
AUTO_APPROVE_MODE="True"
REQUEST_TO_JOIN_MODE="False"
```

## 📱 User Commands

- `/start` - Start the bot and show main menu
- `/menu` - Display main menu with all options
- `/myplan` - Check premium subscription status
- `/help` - Get help and support information

## 👨‍💼 Admin Commands

- `/approve {payment_id}` - Approve pending payment
- `/reject {payment_id} [reason]` - Reject payment with optional reason

## 🚀 Getting Started

### For Users:

1. **Start the Bot**
   - Click `/start` or visit bot link
   - Join required channels if prompted
   - Complete registration

2. **Explore OTT Content**
   - Browse available OTT platforms
   - Search for movies/series
   - View content details with IMDB info

3. **Get Premium**
   - Click "💎 Premium" in main menu
   - Choose a subscription plan
   - Make UPI payment using QR code
   - Upload payment screenshot
   - Wait for admin approval (1-2 hours)

4. **Earn Free Premium**
   - Get your referral link
   - Share with friends
   - Each 20 referrals = 1 month free premium
   - Claim rewards automatically

### For Admins:

1. **Approve Payments**
   - Receive notification with screenshot
   - Use `/approve {payment_id}` to activate premium
   - User gets notified automatically

2. **Reject Payments**
   - Use `/reject {payment_id} [reason]`
   - User receives rejection reason

3. **Monitor System**
   - Check LOG_CHANNEL for activities
   - View new user registrations
   - Track payment notifications

## 📊 Database Collections

### 1. **users**
Stores user information and subscription status
```json
{
  "telegram_id": 123456789,
  "telegram_username": "user123",
  "first_name": "John",
  "premium_subscription": {
    "plan_type": "1month",
    "start_date": "2024-01-01T00:00:00",
    "expiry_date": "2024-02-01T00:00:00",
    "is_active": true
  }
}
```

### 2. **referrals**
Tracks referral relationships
```json
{
  "referral_id": "uuid",
  "referrer_telegram_id": 123456789,
  "referred_telegram_id": 987654321,
  "is_valid": true,
  "reward_claimed": false
}
```

### 3. **referral_stats**
User referral statistics
```json
{
  "telegram_id": 123456789,
  "total_referrals": 25,
  "valid_referrals": 23,
  "rewards_earned": 1,
  "referral_code": "REF12AB34CD"
}
```

### 4. **payments**
Payment records
```json
{
  "payment_id": "uuid",
  "telegram_id": 123456789,
  "amount": 50,
  "plan_type": "1month",
  "status": "pending",
  "screenshot_file_id": "file_id"
}
```

## 🏗️ Architecture

```
EnhancedOTTBot
├── BaseOTTBot (Core functionality)
├── PremiumHandlers (Premium features)
├── ReferralService (Referral management)
├── IMDBService (Content info)
├── ForceSubscribeService (Channel enforcement)
└── PaymentService (Payment processing)
```

## 🔒 Security Features

- Channel membership verification before access
- Payment screenshot validation
- Admin-only commands protection
- User session management
- Secure payment processing

## 📈 Premium Plans Matrix

| Plan | Duration | Price | Best For |
|------|----------|-------|----------|
| 1 Week | 7 days | ₹30 | Trial users |
| 1 Month | 30 days | ₹50 | Regular users |
| 3 Months | 90 days | ₹120 | Value seekers |
| 6 Months | 180 days | ₹220 | Long-term users |

## 🎯 Referral Rewards

- **Tier 1**: 20 referrals = 1 month FREE premium
- **Tier 2**: 40 referrals = 2 months FREE premium
- **Tier 3**: 60 referrals = 3 months FREE premium
- And so on...

## 💡 Tips for Maximizing Referrals

1. Share your referral link in WhatsApp groups
2. Post on social media with bot benefits
3. Share in Telegram movie/series groups
4. Create content about the bot
5. Engage with your referrals

## 🐛 Troubleshooting

### Bot not responding?
- Check BOT_TOKEN is set correctly
- Verify bot is running: `sudo supervisorctl status backend`
- Check logs: `tail -n 50 /var/log/supervisor/backend.err.log`

### Force subscribe not working?
- Verify AUTH_CHANNEL ID is correct
- Bot must be admin in the channel
- Check channel is public or bot has access

### Payments not processing?
- Ensure PAYMENT_QR image URL is accessible
- Verify admin IDs in ADMINS config
- Check MongoDB connection

### Referrals not counting?
- Referred user must use referral link
- User must complete registration
- Wait for validation (happens on first interaction)

## 📝 Customization

### Change Premium Plans
Edit `config.py`:
```python
PREMIUM_PLANS = {
    "custom": {
        "name": "Custom Plan",
        "duration_days": 365,
        "price": 500,
        "description": "1 Year Access"
    }
}
```

### Change Referral Rewards
Edit `.env`:
```bash
REFERAL_COUNT="10"  # 10 referrals for reward
REFERAL_PREMEIUM_TIME="3months"  # 3 months reward
```

### Update Payment Details
Edit `.env`:
```bash
PAYMENT_QR="your_qr_code_url"
OWNER_USERNAME="your_username"
```

## 🔄 Maintenance

### Restart Bot
```bash
sudo supervisorctl restart backend
```

### View Logs
```bash
tail -f /var/log/supervisor/backend.err.log
```

### Update Database
```bash
# Connect to MongoDB and run migrations if needed
```

## 📞 Support

For support and queries:
- Telegram: @Shankar_Kola
- Group: https://t.me/chillbot_movie
- Channel: https://t.me/+nsKuewNAKQtkMGJl

## 📄 License

This bot is configured for private/commercial use. Ensure compliance with Telegram's Bot API terms and local regulations.

---

**Built with ❤️ for OTT enthusiasts**
