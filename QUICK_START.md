# 🚀 Quick Start Guide - Enhanced OTT Bot

## Get Your Bot Running in 5 Minutes!

---

## 📋 Prerequisites

Before starting, make sure you have:

1. ✅ **Telegram Bot Token**
   - Open Telegram and search for `@BotFather`
   - Send `/newbot` and follow instructions
   - Copy the bot token (looks like: `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`)

2. ✅ **Your Telegram User ID**
   - Search for `@userinfobot` on Telegram
   - Send any message to get your user ID
   - Copy the ID number

3. ✅ **Channel IDs** (Optional but recommended)
   - Create a channel for force subscribe
   - Create a channel for logs
   - Add your bot as admin in both
   - Get channel IDs using `@username_to_id_bot`

---

## 🎯 Method 1: Automated Setup (Recommended)

### Step 1: Run Setup Wizard
```bash
cd /app/backend
python3 setup_bot.py
```

### Step 2: Follow the prompts
The wizard will ask you for:
- Bot token
- Admin ID
- Channel IDs
- Payment details
- Links

### Step 3: Restart Services
```bash
sudo supervisorctl restart backend
```

### Step 4: Test Your Bot
Open Telegram, search for your bot, and send `/start`

---

## ⚡ Method 2: Manual Setup (Quick)

### Step 1: Edit Configuration
```bash
nano /app/backend/.env
```

### Step 2: Update These Critical Fields
```bash
# YOUR BOT TOKEN (REQUIRED)
BOT_TOKEN="paste_your_bot_token_here"

# YOUR ADMIN ID (REQUIRED)
ADMINS="your_telegram_user_id"

# OPTIONAL: Force Subscribe Channel
AUTH_CHANNEL="-1001234567890"  # Your channel ID

# OPTIONAL: Log Channel
LOG_CHANNEL="-1001234567890"  # Your log channel ID
```

### Step 3: Save and Exit
- Press `Ctrl + X`
- Press `Y` to confirm
- Press `Enter` to save

### Step 4: Restart Backend
```bash
sudo supervisorctl restart backend
```

### Step 5: Check Status
```bash
sudo supervisorctl status backend
```

Should show: `RUNNING`

---

## 🔍 Verify Bot is Working

### Check Logs:
```bash
tail -f /var/log/supervisor/backend.err.log
```

You should see:
```
🤖 Starting Enhanced OTT Bot with Premium Features...
✅ Enhanced OTT Bot started successfully!
   - Premium Mode: True
   - Auto Approve: True
   - Force Subscribe: Enabled
```

If you see:
```
⚠️ Telegram bot token not configured
```
Then your BOT_TOKEN is not set correctly.

---

## 🎮 Test the Bot

### 1. Start Conversation
- Open Telegram
- Search for your bot by username
- Send `/start`

### 2. Expected Behavior
- You should see a welcome message with an image
- Main menu with buttons should appear
- Buttons should be:
  - 🎬 Explore OTT
  - 💎 Premium
  - 📊 Dashboard
  - ⚙️ Settings
  - 👥 Referrals
  - ❓ Help

### 3. Test Premium Flow
1. Click "💎 Premium"
2. Click "📋 View Plans"
3. Select any plan (e.g., "1 Month - ₹50")
4. QR code should appear with payment instructions
5. ✅ If QR code appears, payment system is working!

### 4. Test Referral System
1. Click "👥 Referrals"
2. You should see your referral stats
3. Your unique referral link should be displayed
4. ✅ If you see stats, referral system is working!

---

## 🔧 Common Issues & Fixes

### Issue 1: Bot not responding
**Solution:**
```bash
# Check if backend is running
sudo supervisorctl status backend

# If not running, restart
sudo supervisorctl restart backend

# Check logs for errors
tail -n 50 /var/log/supervisor/backend.err.log
```

### Issue 2: "Bot token not configured" error
**Solution:**
```bash
# Verify BOT_TOKEN is set in .env
grep BOT_TOKEN /app/backend/.env

# Make sure it's not empty or "your_bot_token_here"
# Edit if needed
nano /app/backend/.env

# Restart
sudo supervisorctl restart backend
```

### Issue 3: Force subscribe not working
**Solutions:**
1. Make sure your bot is admin in AUTH_CHANNEL
2. Verify AUTH_CHANNEL ID is correct (should start with `-100`)
3. Check if bot has "invite users" permission in channel

### Issue 4: QR code not showing
**Solution:**
```bash
# Update PAYMENT_QR URL in .env
nano /app/backend/.env

# Find this line:
PAYMENT_QR="https://envs.sh/L-M.jpg"

# Replace with your QR code image URL
# Restart
sudo supervisorctl restart backend
```

### Issue 5: Admin commands not working
**Solution:**
```bash
# Verify your user ID is in ADMINS
grep ADMINS /app/backend/.env

# Should show your Telegram user ID
# Example: ADMINS="1636733122"
```

---

## 📱 Configure Channels

### For Force Subscribe (AUTH_CHANNEL):

1. **Create a Channel**
   - Open Telegram
   - Create new channel
   - Make it public or private

2. **Add Bot as Admin**
   - Go to channel settings
   - Click "Administrators"
   - Click "Add Administrator"
   - Search for your bot
   - Give it "Invite users" permission

3. **Get Channel ID**
   - Forward a message from channel to `@username_to_id_bot`
   - Copy the channel ID (e.g., `-1001234567890`)
   - Update AUTH_CHANNEL in .env

### For Logs (LOG_CHANNEL):

1. **Create a Channel or Use Same**
2. **Add Bot as Admin** (same steps as above)
3. **Update LOG_CHANNEL** in .env with channel ID

---

## 💳 Setup Payment QR Code

### Option 1: Use Online QR Generator
1. Go to https://www.qr-code-generator.com/
2. Select "UPI Payment"
3. Enter your UPI ID: `kolashankar113@oksbi`
4. Generate QR code
5. Download image
6. Upload to https://telegra.ph/ or imgur.com
7. Copy image URL
8. Update PAYMENT_QR in .env

### Option 2: Use Existing URL
Keep the default: `PAYMENT_QR="https://envs.sh/L-M.jpg"`

---

## 🎯 What's Next?

### After Bot is Running:

1. **Test All Features:**
   - ✅ Premium subscription flow
   - ✅ Referral system
   - ✅ Payment screenshot upload
   - ✅ Admin commands

2. **Customize:**
   - Update welcome images (PICS in .env)
   - Change premium plan prices (config.py)
   - Modify referral rewards (REFERAL_COUNT)

3. **Go Live:**
   - Share bot link with users
   - Monitor logs for issues
   - Process payments as they come in

4. **Admin Dashboard:**
   - Access at: `http://your-domain.com/`
   - Manage users and payments
   - View statistics
   - Send broadcasts

---

## 📊 Monitor Your Bot

### View Logs in Real-Time:
```bash
tail -f /var/log/supervisor/backend.err.log
```

### Check Active Users:
Open MongoDB or use admin dashboard

### Process Payments:
When you receive payment notification:
```
/approve {payment_id}
```

Or use admin dashboard to approve visually.

---

## 🎉 Success Checklist

- [ ] Bot responds to `/start`
- [ ] Welcome message with image appears
- [ ] All menu buttons work
- [ ] Premium plans display correctly
- [ ] QR code shows on payment
- [ ] Referral link generates
- [ ] Admin commands work (`/approve`, `/reject`)
- [ ] Force subscribe works (if enabled)
- [ ] Admin dashboard accessible

---

## 📞 Need Help?

### Check Documentation:
- **Full Guide:** `/app/ENHANCED_BOT_GUIDE.md`
- **Implementation Details:** `/app/IMPLEMENTATION_SUMMARY.md`
- **Configuration:** `/app/backend/config.py`

### Common Commands:
```bash
# Restart bot
sudo supervisorctl restart backend

# View logs
tail -f /var/log/supervisor/backend.err.log

# Check status
sudo supervisorctl status

# Edit config
nano /app/backend/.env
```

### Still Stuck?
- Review error logs carefully
- Check all IDs are correct (bot token, admin ID, channel IDs)
- Ensure bot is admin in all channels
- Verify MongoDB is running

---

## 🎊 You're All Set!

Your Enhanced OTT Bot is now ready to serve users!

**Share your bot:**
- Post in groups
- Share on social media
- Add to channel description

**Monitor and manage:**
- Use admin commands
- Check dashboard regularly
- Process payments promptly

**Grow your business:**
- Encourage referrals
- Offer promotions
- Engage with users

---

**Happy Bot-ing! 🚀**
