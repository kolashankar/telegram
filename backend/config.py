"""
OTT Bot Configuration
Centralized configuration for all bot settings
"""
import os
from dotenv import load_dotenv
import re

load_dotenv()

# Helper function
id_pattern = re.compile(r'^-?\d+$')

def is_enabled(value, default):
    if value.lower() in ['true', 'yes', '1', 'enable', 'y']:
        return True
    elif value.lower() in ['false', 'no', '0', 'disable', 'n']:
        return False
    else:
        return default

# Bot Information
SESSION = os.environ.get('SESSION', 'TechVJBot')
API_ID = int(os.environ.get('API_ID', '24271861'))
API_HASH = os.environ.get('API_HASH', 'fc5e782b934ed58b28780f41f01ed024')
BOT_TOKEN = os.environ.get('BOT_TOKEN', "")

# Bot Settings
CACHE_TIME = int(os.environ.get('CACHE_TIME', 1800))
PICS = (os.environ.get('PICS', 'https://envs.sh/L-f.jpg')).split()
NOR_IMG = os.environ.get("NOR_IMG", "https://graph.org/file/b69af2db776e4e85d21ec.jpg")
MELCOW_VID = os.environ.get("MELCOW_VID", "https://t.me/How_To_Open_Linkl")
SPELL_IMG = os.environ.get("SPELL_IMG", "https://te.legra.ph/file/15c1ad448dfe472a5cbb8.jpg")

# Admins, Channels & Users
LOG_CHANNEL = int(os.environ.get('LOG_CHANNEL', '-1002409317177'))
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in os.environ.get('ADMINS', '1636733122').split()]
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in os.environ.get('CHANNELS', '-1002309517928').split()]
auth_users = [int(user) if id_pattern.search(user) else user for user in os.environ.get('AUTH_USERS', '6479751412').split()]
AUTH_USERS = (auth_users + ADMINS) if auth_users else []

# Force Subscribe Configuration
REQUEST_TO_JOIN_MODE = bool(os.environ.get('REQUEST_TO_JOIN_MODE', False))
TRY_AGAIN_BTN = bool(os.environ.get('TRY_AGAIN_BTN', False))
auth_channel = os.environ.get('AUTH_CHANNEL', '-1001710985956')
AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None
reqst_channel = os.environ.get('REQST_CHANNEL_ID', '-1001765035645')
REQST_CHANNEL = int(reqst_channel) if reqst_channel and id_pattern.search(reqst_channel) else None
support_chat_id = os.environ.get('SUPPORT_CHAT_ID', '')
SUPPORT_CHAT_ID = int(support_chat_id) if support_chat_id and id_pattern.search(support_chat_id) else None

# MongoDB Information
MULTIPLE_DATABASE = bool(os.environ.get('MULTIPLE_DATABASE', False))

DATABASE_URI = os.environ.get('DATABASE_URI', "mongodb+srv://shankar113:pkfZ2NlPLngYvo73@cluster0.52v0v.mongodb.net/?retryWrites=true&w=majority")
if MULTIPLE_DATABASE == False:
    USER_DB_URI = DATABASE_URI
    OTHER_DB_URI = DATABASE_URI
    FILE_DB_URI = DATABASE_URI
    SEC_FILE_DB_URI = DATABASE_URI
else:
    USER_DB_URI = DATABASE_URI
    OTHER_DB_URI = os.environ.get('OTHER_DB_URI', "")
    FILE_DB_URI = os.environ.get('FILE_DB_URI', "")
    SEC_FILE_DB_URI = os.environ.get('SEC_FILE_DB_URI', "")
    
DATABASE_NAME = os.environ.get('DATABASE_NAME', "techvjautobot")
COLLECTION_NAME = os.environ.get('COLLECTION_NAME', 'vjcollection')

# Premium and Referral Settings
PREMIUM_AND_REFERAL_MODE = bool(os.environ.get('PREMIUM_AND_REFERAL_MODE', True))

# Premium Plans Configuration
REFERAL_COUNT = int(os.environ.get('REFERAL_COUNT', '20'))
REFERAL_PREMEIUM_TIME = os.environ.get('REFERAL_PREMEIUM_TIME', '1month')
PAYMENT_QR = os.environ.get('PAYMENT_QR', 'https://envs.sh/L-M.jpg')
PAYMENT_TEXT = os.environ.get('PAYMENT_TEXT', '''<b>- ᴀᴠᴀɪʟᴀʙʟᴇ ᴘʟᴀɴs - 

- 30ʀs - 1 ᴡᴇᴇᴋ
- 50ʀs - 1 ᴍᴏɴᴛʜs
- 120ʀs - 3 ᴍᴏɴᴛʜs
- 220ʀs - 6 ᴍᴏɴᴛʜs

🎁 ᴘʀᴇᴍɪᴜᴍ ғᴇᴀᴛᴜʀᴇs 🎁

○ ɴᴏ ɴᴇᴇᴅ ᴛᴏ ᴠᴇʀɪғʏ
○ ɴᴏ ɴᴇᴇᴅ ᴛᴏ ᴏᴘᴇɴ ʟɪɴᴋ
○ ᴅɪʀᴇᴄᴛ ғɪʟᴇs
○ ᴀᴅ-ғʀᴇᴇ ᴇxᴘᴇʀɪᴇɴᴄᴇ
○ ʜɪɢʜ-sᴘᴇᴇᴅ ᴅᴏᴡɴʟᴏᴀᴅ ʟɪɴᴋ
○ ᴜɴʟɪᴍɪᴛᴇᴅ ᴍᴏᴠɪᴇs & sᴇʀɪᴇs
○ ꜰᴜʟʟ ᴀᴅᴍɪɴ sᴜᴘᴘᴏʀᴛ
○ ʀᴇǫᴜᴇsᴛ ᴡɪʟʟ ʙᴇ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ɪɴ 1ʜ ɪꜰ ᴀᴠᴀɪʟᴀʙʟᴇ

✨ ᴜᴘɪ ɪᴅ - <code>kolashankar113@oksbi</code>

ᴄʟɪᴄᴋ ᴛᴏ ᴄʜᴇᴄᴋ ʏᴏᴜʀ ᴀᴄᴛɪᴠᴇ ᴘʟᴀɴ /myplan

💢 ᴍᴜsᴛ sᴇɴᴅ sᴄʀᴇᴇɴsʜᴏᴛ ᴀғᴛᴇʀ ᴘᴀʏᴍᴇɴᴛ

‼️ ᴀғᴛᴇʀ sᴇɴᴅɪɴɢ ᴀ sᴄʀᴇᴇɴsʜᴏᴛ ᴘʟᴇᴀsᴇ ɢɪᴠᴇ ᴜs sᴏᴍᴇ ᴛɪᴍᴇ ᴛᴏ ᴀᴅᴅ ʏᴏᴜ ɪɴ ᴛʜᴇ ᴘʀᴇᴍɪᴜᴍ</b>''')
OWNER_USERNAME = os.environ.get('OWNER_USERNAME', 'Shankar_Kola')

# Links
GRP_LNK = os.environ.get('GRP_LNK', 'https://t.me/chillbot_movie')
CHNL_LNK = os.environ.get('CHNL_LNK', 'https://t.me/+nsKuewNAKQtkMGJl')
TUTORIAL = os.environ.get('TUTORIAL', 'https://t.me/how_to_open_link_time2chill')
SUPPORT_CHAT = os.environ.get('SUPPORT_CHAT', 'time2chill_discussion')

# Feature Flags
PM_SEARCH = bool(os.environ.get('PM_SEARCH', True))
IS_TUTORIAL = bool(os.environ.get('IS_TUTORIAL', True))
P_TTI_SHOW_OFF = is_enabled((os.environ.get('P_TTI_SHOW_OFF', "False")), False)
IMDB = is_enabled((os.environ.get('IMDB', "True")), True)
AUTO_DELETE = is_enabled((os.environ.get('AUTO_DELETE', "True")), True)
SINGLE_BUTTON = is_enabled((os.environ.get('SINGLE_BUTTON', "True")), True)
LONG_IMDB_DESCRIPTION = is_enabled(os.environ.get("LONG_IMDB_DESCRIPTION", "False"), False)
SPELL_CHECK_REPLY = is_enabled(os.environ.get("SPELL_CHECK_REPLY", "True"), True)
MELCOW_NEW_USERS = is_enabled((os.environ.get('MELCOW_NEW_USERS', "True")), True)
PROTECT_CONTENT = is_enabled((os.environ.get('PROTECT_CONTENT', "False")), False)
NO_RESULTS_MSG = bool(os.environ.get("NO_RESULTS_MSG", False))

# Shortlink Configuration (Mock for now)
SHORTLINK_MODE = bool(os.environ.get('SHORTLINK_MODE', False))
SHORTLINK_URL = os.environ.get('SHORTLINK_URL', 'https://runurl.in/')
SHORTLINK_API = os.environ.get('SHORTLINK_API', '02d038634b0ed6e5245e2502243d494f87df3c57')

# Auto Approve
AUTO_APPROVE_MODE = bool(os.environ.get('AUTO_APPROVE_MODE', True))

# Others
MAX_B_TN = os.environ.get("MAX_B_TN", "5")
PORT = os.environ.get("PORT", "8080")
MSG_ALRT = os.environ.get('MSG_ALRT', 'Hello My Dear Friends ❤️')

# Premium Plans
PREMIUM_PLANS = {
    "1week": {
        "name": "Weekly Plan",
        "duration_days": 7,
        "price": 30,
        "description": "1 Week Access"
    },
    "1month": {
        "name": "Monthly Plan",
        "duration_days": 30,
        "price": 50,
        "description": "1 Month Access"
    },
    "3months": {
        "name": "Quarterly Plan",
        "duration_days": 90,
        "price": 120,
        "description": "3 Months Access"
    },
    "6months": {
        "name": "Half-Yearly Plan",
        "duration_days": 180,
        "price": 220,
        "description": "6 Months Access"
    }
}

# OTT Platforms Categories
LANGUAGES = ["malayalam", "mal", "tamil", "tam", "english", "eng", "hindi", "hin", "telugu", "tel", "kannada", "kan"]
QUALITIES = ["360p", "480p", "720p", "1080p", "1440p", "2160p"]
YEARS = [str(year) for year in range(1990, 2026)]

# Logging Configuration
LOG_STR = "Current OTT Bot Configuration:\n"
LOG_STR += f"Premium & Referral Mode: {'Enabled' if PREMIUM_AND_REFERAL_MODE else 'Disabled'}\n"
LOG_STR += f"Auto Approve Mode: {'Enabled' if AUTO_APPROVE_MODE else 'Disabled'}\n"
LOG_STR += f"IMDB Integration: {'Enabled' if IMDB else 'Disabled'}\n"
LOG_STR += f"Force Subscribe: {'Enabled' if AUTH_CHANNEL else 'Disabled'}\n"
LOG_STR += f"Multiple Database: {'Enabled' if MULTIPLE_DATABASE else 'Disabled'}\n"
