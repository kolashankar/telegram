## 🎬 OTT Subscription Management Bot

A complete multi-user Telegram bot for managing OTT subscriptions with payment handling, admin panel, and 30+ platform support.

---

## 🚀 Quick Start

### 1. Get Your Telegram Bot Token

1. Open Telegram and search for **@BotFather**
2. Send `/newbot` command
3. Choose a name for your bot (e.g., "My OTT Manager")
4. Choose a username (must end in 'bot', e.g., "myott_manager_bot")
5. **Copy the bot token** (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Configure the Bot

Edit the file `/app/backend/.env` and update:

```bash
TELEGRAM_BOT_TOKEN="YOUR_TOKEN_HERE"
ADMIN_UPI_ID="yourname@upi"
```

### 3. Register Yourself as Admin

```bash
cd /app/backend
python3 src/utils/admin_setup.py
```

**To get your Telegram ID:**
1. Open Telegram
2. Search for **@userinfobot**
3. Send `/start`
4. Copy your numeric ID

### 4. Restart the Bot

```bash
sudo supervisorctl restart backend
```

### 5. Start Using!

1. Open your bot in Telegram
2. Send `/start`
3. Explore the 8 main features!

---

## 💡 Features Overview

### 🎬 1. OTT Explorer
- Browse latest movies & shows across 30+ platforms
- Filter by genre, language, release date
- View platform availability
- Watch trailers
- Manage your watchlist

### 💰 2. Compare Plans
- Compare subscription costs across all OTT platforms
- View active offers and discounts
- Filter by plan type (monthly/yearly/mobile/family)
- Get best value recommendations
- See price history

### 🔔 3. Release Alerts
- Subscribe to alerts for specific genres/platforms
- Set daily, weekly, or instant notifications
- Customize notification timing
- View trending content
- Manage your alert preferences

### 📊 4. User Dashboard
- View subscription expiry dates
- Track total money spent
- Get renewal reminders
- View watchlist & history
- Export data to PDF

### 💵 5. Subscriptions
**Complete payment workflow:**

1. **Choose a plan:**
   - Weekly Plan (₹99) - 7 days access
   - Monthly Plan (₹299) - 30 days access
   - Custom Bundle - Choose your platforms

2. **Pay via UPI:**
   - Bot generates QR code
   - Scan with any UPI app (GPay, PhonePe, Paytm)
   - Pay the amount

3. **Upload screenshot:**
   - Take screenshot of payment confirmation
   - Send it to the bot

4. **Admin verification:**
   - Admin verifies payment
   - Subscription activates automatically
   - You get notified!

### 👑 6. Admin Panel

**Admin can:**
- Add/remove OTT platforms
- Manage users and subscriptions
- Verify pending payments (with screenshot review)
- Send announcements to all users
- Generate revenue reports

**Admin Commands (send as text):**
```
verify {payment_id}              # Approve payment
reject {payment_id} [reason]     # Reject payment
announce: Your message here      # Broadcast to all users
```

### ⚙️ 7. Settings
- Choose OTT region (India/Global/All)
- Set default genres and languages
- Manage notification preferences
- View connected devices
- Delete account option

### 🆘 8. Help & Support

**Support commands:**
```
support: Your question           # Contact admin
issue: Problem description       # Report issues
refund: payment_id reason        # Request refund
```

---

## 🎯 Supported OTT Platforms (30+)

### Indian Platforms
Disney+ Hotstar, Zee5, SonyLIV, SunNXT, Aha Video, JioCinema, Voot, MX Player, Eros Now, ALTBalaji, Lionsgate Play, Hoichoi, FanCode, Epic On, ShemarooMe, Chaupal, Stage OTT

### International Platforms
Netflix, Prime Video, Disney+, HBO Max, Hulu, Apple TV+, YouTube Premium, Discovery+, Mubi, DocuBay, IVI, Viu, CuriosityStream

---

## 🔧 Technical Details

### Architecture
- **Backend:** FastAPI (Python)
- **Bot Framework:** python-telegram-bot
- **Database:** MongoDB
- **Payment:** UPI QR codes (manual verification)

### File Structure
```
/app/backend/
├── server.py                    # Main FastAPI server
├── src/
│   ├── models/                  # Data models
│   ├── services/
│   │   ├── telegram/           # Bot implementation
│   │   ├── ott/                # Platform data
│   │   └── payment/            # Payment services
│   └── utils/
│       └── admin_setup.py      # Admin registration tool
```

### Database Collections
- `users` - User profiles and subscriptions
- `payments` - Payment records with screenshots
- `admins` - Admin users
- `watchlists` - User watchlists
- `release_alerts` - Alert subscriptions

---

## 📝 Bot Commands Reference

### User Commands
| Command | Description |
|---------|-------------|
| `/start` | Start bot and show main menu |
| `/help` | Show help and feature guide |
| `/menu` | Display main menu |

### Admin Commands (via text)
| Command | Example | Description |
|---------|---------|-------------|
| `verify` | `verify abc123` | Approve payment |
| `reject` | `reject abc123 Invalid amount` | Reject payment with reason |
| `announce:` | `announce: New offers available!` | Broadcast to all users |

### Support Commands (via text)
| Command | Example | Description |
|---------|---------|-------------|
| `support:` | `support: Need help with payment` | Contact admin |
| `issue:` | `issue: Bot not responding` | Report technical issue |
| `refund:` | `refund: abc123 Paid wrong amount` | Request refund |

---

## 💳 Payment Flow Guide

### For Users:

1. **Select Plan**
   - Go to "Subscriptions" menu
   - Choose Weekly/Monthly/Custom plan
   - Bot shows platforms included

2. **Receive QR Code**
   - Bot generates UPI QR code
   - Shows payment amount and UPI ID
   - Includes payment instructions

3. **Pay via UPI**
   - Open GPay/PhonePe/Paytm
   - Scan QR code OR use UPI ID
   - Complete payment

4. **Upload Screenshot**
   - Take screenshot of payment confirmation
   - Send as photo to bot (NOT as file)
   - Bot confirms receipt

5. **Wait for Verification**
   - Admin reviews payment (usually within 24 hours)
   - You get notified when approved
   - Subscription activates automatically

### For Admins:

1. **Receive Notification**
   - Bot notifies when new payment screenshot uploaded
   - Shows user details and amount

2. **Review Screenshot**
   - Check amount matches
   - Verify transaction ID
   - Confirm payment date

3. **Verify or Reject**
   - To approve: `verify {payment_id}`
   - To reject: `reject {payment_id} Reason here`
   - User gets notified instantly

4. **Subscription Activation**
   - On approval, subscription activates automatically
   - Expiry date set based on plan
   - User can start using services

---

## 🔐 Admin Setup Guide

### Register New Admin

```bash
cd /app/backend
python3 src/utils/admin_setup.py
```

**Follow the prompts:**
1. Enter Telegram ID (get from @userinfobot)
2. Enter username (optional)
3. Enter first name (optional)
4. Confirm registration

### Admin Permissions

Admins can:
- ✅ Verify payments
- ✅ Manage users
- ✅ Manage platforms
- ✅ Send announcements
- ✅ View analytics

### Admin Best Practices

1. **Payment Verification:**
   - Check screenshot carefully
   - Verify amount and date
   - Look for transaction ID
   - Reject if suspicious

2. **User Management:**
   - Monitor active subscriptions
   - Handle expiry notifications
   - Respond to support requests

3. **Announcements:**
   - Keep messages brief
   - Include call-to-action
   - Test on yourself first

---

## 🛠️ Troubleshooting

### Bot Not Responding

**Check if bot is running:**
```bash
sudo supervisorctl status backend
```

**View logs:**
```bash
tail -f /var/log/supervisor/backend.err.log
```

**Restart bot:**
```bash
sudo supervisorctl restart backend
```

### Payment Issues

**QR Code Not Generating:**
- Check `ADMIN_UPI_ID` in `/app/backend/.env`
- Ensure UPI ID format is correct (name@upi)

**Screenshot Upload Fails:**
- User must send as **photo**, not file
- Check if bot has permissions to receive photos
- Try sending again

**Admin Not Receiving Notifications:**
- Verify admin is registered: `python3 src/utils/admin_setup.py` (option 2)
- Check admin's Telegram ID is correct
- Ensure admin has started the bot (`/start`)

### Database Issues

**Check MongoDB connection:**
```bash
mongo --eval "db.stats()"
```

**View collections:**
```bash
mongo test_database --eval "show collections"
```

---

## 📊 Admin Dashboard

### View Pending Payments

1. Go to **Admin Panel**
2. Click **Verify Payments**
3. See list of pending payments with:
   - User details
   - Amount
   - Plan type
   - Screenshot status
   - Commands to verify/reject

### Manage Users

1. Go to **Admin Panel**
2. Click **Manage Users**
3. View statistics:
   - Total users
   - Active subscriptions
   - New users

### Send Announcements

1. Go to **Admin Panel**
2. Click **Send Announcement**
3. Type: `announce: Your message`
4. Bot broadcasts to all users

### View Reports

1. Go to **Admin Panel**
2. Click **Revenue Reports**
3. See:
   - Total revenue
   - Verified payments
   - Popular plans
   - User statistics

---

## 🎨 Customization

### Update Platform Pricing

Edit `/app/backend/src/services/ott/platform_data.py`:

```python
{
    "name": "netflix",
    "display_name": "Netflix",
    "mobile_plan": 149.0,    # Update these
    "monthly_plan": 199.0,
    "yearly_plan": None,
    # ...
}
```

### Update Plan Pricing

Edit `/app/backend/src/services/telegram/bot_subscription_admin.py`:

Look for `handle_subscription_plan` function:

```python
plans = {
    "weekly": {
        "price": 99.0,  # Change price here
        "duration_days": 7,
        # ...
    }
}
```

### Change UPI ID

Update `/app/backend/.env`:

```bash
ADMIN_UPI_ID="newname@upi"
```

Then restart:
```bash
sudo supervisorctl restart backend
```

---

## 📱 User Guide

### Getting Started

1. **Find Your Bot**
   - Search for your bot username in Telegram
   - Start a chat

2. **Register**
   - Send `/start`
   - Bot creates your profile automatically

3. **Explore Features**
   - Use inline buttons to navigate
   - Or type `/menu` anytime

### Managing Subscriptions

1. **Choose Plan:**
   - Tap "Subscriptions"
   - Select plan type
   - Review platforms and price

2. **Payment:**
   - Receive QR code
   - Pay via any UPI app
   - Upload screenshot

3. **Track Status:**
   - Go to "Dashboard"
   - View expiry dates
   - See days remaining

### Using Features

**Browse Content:**
- Tap "OTT Explorer"
- Browse latest releases
- Add to watchlist

**Compare Prices:**
- Tap "Compare Plans"
- View all platforms
- See best deals

**Set Alerts:**
- Tap "Release Alerts"
- Choose preferences
- Get notifications

---

## 🔒 Security & Privacy

### Data Storage
- User data stored securely in MongoDB
- Payment screenshots stored as Telegram file IDs
- Admin access controlled

### What We Store
- Telegram ID and username
- Subscription details
- Payment records
- Watchlist items
- Preferences

### What We Don't Store
- Personal messages
- Payment credentials
- Bank details

### Data Deletion
- Users can delete account anytime
- Go to Settings → Delete Account
- All data removed (except payment records for compliance)

---

## 💡 Tips & Best Practices

### For Users
1. Take clear payment screenshots
2. Include transaction ID in screenshot
3. Pay exact amount shown
4. Upload screenshot within 24 hours
5. Check spam/notifications for bot messages

### For Admins
1. Verify payments daily
2. Respond to support requests quickly
3. Keep platform pricing updated
4. Send regular announcements about offers
5. Monitor revenue reports weekly

---

## 🆘 Support

### Common Questions

**Q: How long does payment verification take?**
A: Usually within 24 hours, depending on admin availability.

**Q: Can I cancel my subscription?**
A: Subscriptions run until expiry. No auto-renewal.

**Q: What if I paid wrong amount?**
A: Contact admin via `refund:` command with details.

**Q: Can I change platforms after payment?**
A: No, platform selection is final. Choose carefully.

**Q: Is my payment information safe?**
A: We only store payment screenshots. Never store card/bank details.

### Getting Help

1. **Bot Issues:** Type `issue: [your problem]`
2. **Payment Issues:** Type `refund: [payment_id] [reason]`
3. **General Questions:** Type `support: [your question]`

### Admin Contact

- All support messages go directly to admin
- Admin responds via bot
- Urgent issues prioritized

---

## 📈 Future Enhancements

Possible future additions:
- Automated payment verification (Razorpay/Instamojo)
- Email notifications
- Group subscriptions
- Referral rewards
- Mobile app
- Content recommendations
- Live chat support

---

## 📜 License & Terms

### Terms of Service

1. **Service Nature**
   - Subscription management only
   - Users must have own OTT accounts
   - No content provided

2. **Payments**
   - UPI payments only
   - Manual verification by admin
   - Refunds subject to admin approval

3. **Usage**
   - Personal use only
   - No commercial reselling
   - Admin reserves right to terminate

### Privacy Policy

- Minimal data collection
- Secure storage
- No third-party sharing
- Data deletion on request

---

## 🎉 You're All Set!

**Your OTT Subscription Management Bot is ready to use!**

Quick checklist:
- ✅ Bot token configured
- ✅ Admin registered
- ✅ UPI ID set
- ✅ Backend running

**Start managing OTT subscriptions like a pro!** 🚀

---

**Questions? Issues? Feature requests?**
Contact via the bot's Help & Support section.

**Happy streaming! 🎬🍿**
