# ═══════════════════════════════════════════════════════════
#        🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   GɪᴛHᴜʙ : github.com/ItsMeVishal0/VishalMusic
#   Dᴇᴠʟᴏᴘᴇʀ : @ItsMeVishalBots | Telegram
# ═══════════════════════════════════════════════════════════

import re
from os import getenv
from dotenv import load_dotenv
from pyrogram import filters

# Load environment variables from .env file
load_dotenv()


def _clean_str(val, default: str = "") -> str:
    if val is None:
        return default
    return str(val).strip().strip('"').strip("'")


def _clean_int(val, default: int) -> int:
    if val is None:
        return default
    try:
        clean = str(val).strip().strip('"').strip("'")
        return int(clean)
    except Exception:
        return default


def _clean_api_id(val, default: int = 26493077) -> int:
    clean = _clean_int(val, default)
    if clean > 2147483647:
        clean = (clean & 0x7FFFFFFF)
    return clean


# ── Core bot config ─────────────────────────────────────────────────────────
API_ID = _clean_api_id(getenv("API_ID"), 26493077)
API_HASH = _clean_str(getenv("API_HASH"), "6586f0276c7748e54684719bdd247d90")
BOT_TOKEN = _clean_str(getenv("BOT_TOKEN"))

OWNER_ID = _clean_int(getenv("OWNER_ID"), 7044783841)
OWNER_USERNAME = _clean_str(getenv("OWNER_USERNAME"), "ItsMeVishalBots")
BOT_USERNAME = _clean_str(getenv("BOT_USERNAME"), "vaishaliTune_bot")
BOT_NAME = _clean_str(getenv("BOT_NAME"), "≽ ^⎚ 𝘃𝗮𝗶𝘀𝗵𝗮𝗹𝗶 𝘅 𝗺𝘂𝘀𝗶𝗰 ⎚^ ≼")
ASSUSERNAME = _clean_str(getenv("ASSUSERNAME"), "≽ ^⎚ 𝗮𝘀𝘀𝗶𝘀𝘁𝗮𝗻𝘁 ⎚^ ≼")

# ── Database & logging ────────────────────────────────────────────────────────
MONGO_DB_URI = _clean_str(getenv("MONGO_DB_URI"))
LOGGER_ID = _clean_int(getenv("LOGGER_ID"), -1002425220992)

# ── Limits (durations in min/sec; sizes in bytes) ──────────────────────────────
DURATION_LIMIT_MIN = _clean_int(getenv("DURATION_LIMIT"), 300)
SONG_DOWNLOAD_DURATION = _clean_int(getenv("SONG_DOWNLOAD_DURATION"), 1200)
SONG_DOWNLOAD_DURATION_LIMIT = _clean_int(getenv("SONG_DOWNLOAD_DURATION_LIMIT"), 1800)
TG_AUDIO_FILESIZE_LIMIT = _clean_int(getenv("TG_AUDIO_FILESIZE_LIMIT"), 3221225472)  # 3 GB
TG_VIDEO_FILESIZE_LIMIT = _clean_int(getenv("TG_VIDEO_FILESIZE_LIMIT"), 3221225472)  # 3 GB
PLAYLIST_FETCH_LIMIT = _clean_int(getenv("PLAYLIST_FETCH_LIMIT"), 30)

# ── External APIs ──────────────────────────────────────────────────────────
COOKIE_URL = _clean_str(getenv("COOKIE_URL"), "https://pastebin.com/RurxsvMF")
API_URL = _clean_str(getenv("API_URL"))        # optional
API_KEY = _clean_str(getenv("API_KEY"))        # optional 
DEEP_API = _clean_str(getenv("DEEP_API"))      # optional

# ── YouTube Download APIs & Keys ───────────────────────────────────────────
VISHAL_API_KEY = _clean_str(getenv("VISHAL_API_KEY"), "ShrutiBotsc7zkBuuYtyvKJas3omsr")
PRIMARY_API_URL = _clean_str(getenv("PRIMARY_API_URL"), "https://api.shrutibots.site")
FALLBACK_API_URL = _clean_str(getenv("FALLBACK_API_URL"), "http://13.212.126.0:2020")

# ── Telegram Bot API (Local Server for colored buttons support) ───────────────
LOCAL_BOT_API_URL = _clean_str(getenv("LOCAL_BOT_API_URL"), "").rstrip("/")

# ── Hosting / deployment ───────────────────────────────────────────────────────
HEROKU_APP_NAME = _clean_str(getenv("HEROKU_APP_NAME"))
HEROKU_API_KEY = _clean_str(getenv("HEROKU_API_KEY"))

# ── Git / updates ──────────────────────────────────────────────────────────
UPSTREAM_REPO = _clean_str(getenv("UPSTREAM_REPO"), "https://github.com/ItsMeVishal0/VishalMusic.git")
UPSTREAM_BRANCH = _clean_str(getenv("UPSTREAM_BRANCH"), "main")
GIT_TOKEN = _clean_str(getenv("GIT_TOKEN"))  # needed if repo is private

# ── Support links ──────────────────────────────────────────────────────────
SUPPORT_CHANNEL = _clean_str(getenv("SUPPORT_CHANNEL"), "https://t.me/ItsMeVishalBots")
SUPPORT_CHAT = _clean_str(getenv("SUPPORT_CHAT"), "https://t.me/ItsMeVishalBots")
PRIVACY_LINK = _clean_str(getenv("PRIVACY_LINK"), SUPPORT_CHAT)

# ── Assistant auto-leave ───────────────────────────────────────────────────────
AUTO_LEAVING_ASSISTANT = False
AUTO_LEAVE_ASSISTANT_TIME = _clean_int(getenv("ASSISTANT_LEAVE_TIME"), 3600)

# ── Debug ──────────────────────────────────────────────────────────
DEBUG_IGNORE_LOG = True

# ── Spotify (optional) ─────────────────────────────────────────────────────
SPOTIFY_CLIENT_ID = _clean_str(getenv("SPOTIFY_CLIENT_ID"), "22b6125bfe224587b722d6815002db2b")
SPOTIFY_CLIENT_SECRET = _clean_str(getenv("SPOTIFY_CLIENT_SECRET"), "c9c63c6fbf2f467c8bc68624851e9773")

# ── Session strings (optional) ─────────────────────────────────────────────────
STRING1 = _clean_str(getenv("STRING_SESSION"))
STRING2 = _clean_str(getenv("STRING_SESSION2"))
STRING3 = _clean_str(getenv("STRING_SESSION3"))
STRING4 = _clean_str(getenv("STRING_SESSION4"))
STRING5 = _clean_str(getenv("STRING_SESSION5"))

# ── Media assets ──────────────────────────────────────────────────────────
START_IMGS = [
    "https://files.catbox.moe/a6sz5r.jpg",
    "https://files.catbox.moe/53szdj.jpg",
    "https://files.catbox.moe/h9dan0.jpg",
    "https://files.catbox.moe/s8yhxr.jpg",
]
STICKERS = [
    "CAACAgUAAyEFAASQje-AAAI92mkOFHmOlyKv0vEpoJE6S7ZInIuPAALbFQACSZmpVI0wvAnbSnk9HgQ",
    "CAACAgQAAyEFAASQje-AAAI92GkOFFx4j5i7GwlGsRbvXBaZbgquAAIoFQACir5JU9xIMA-J9yY7HgQ",
    "CAACAgQAAyEFAASQje-AAAI91mkOFEeMiZrau4LoUgHQAuhfVUNoAAJbHQACmKWIUVKzS9qKs-juHgQ",
    "CAACAgUAAyEFAASQje-AAAI91GkOFDevrsTZ_JzDdyHdsu2VhsvHAAJ2EwAC_xfYVo5iQw7a3JPfHgQ",
    "CAACAgUAAyEFAASQje-AAAI90mkOFCn95GwjE62nWBG2o9H-FK15AAJgFQACJ_uwVMGj96qQgd3hHgQ",
    "CAACAgQAAyEFAASQje-AAAI90GkOFCDWtQkvBiumJxSoedz0NqvLAAIzFAAC9ED4UX1Ta6URzlyIHgQ",
]
HELP_IMG_URL = "https://files.catbox.moe/a6sz5r.jpg"
PING_VID_URL = "https://files.catbox.moe/qibmue.mp4"
PLAYLIST_IMG_URL = "https://files.catbox.moe/h9dan0.jpg"
STATS_VID_URL = "https://files.catbox.moe/a6sz5r.jpg"
TELEGRAM_AUDIO_URL = "https://files.catbox.moe/s8yhxr.jpg"
TELEGRAM_VIDEO_URL = "https://files.catbox.moe/a6sz5r.jpg"
STREAM_IMG_URL = "https://files.catbox.moe/h9dan0.jpg"
SOUNCLOUD_IMG_URL = "https://files.catbox.moe/a6sz5r.jpg"
YOUTUBE_IMG_URL = "https://files.catbox.moe/a6sz5r.jpg"
SPOTIFY_ARTIST_IMG_URL = SPOTIFY_ALBUM_IMG_URL = SPOTIFY_PLAYLIST_IMG_URL = YOUTUBE_IMG_URL

# ── Helpers ────────────────────────────────────────────────────────────
def time_to_seconds(time: str) -> int:
    return sum(int(x) * 60**i for i, x in enumerate(reversed(time.split(":"))))

DURATION_LIMIT = time_to_seconds(f"{DURATION_LIMIT_MIN}:00")

# ───── Bot Search Messages (Single Line) ───── #
# {0} = user mention/name
AYU = [
    "𝐅𝐢𝐧𝐝𝐢𝐧𝐠 𝐘𝐨𝐮𝐫 𝐒𝐨𝐧𝐠 ꨄ︎ {0} ",
    "𝐒𝐞𝐚𝐫𝐜𝐡𝐢𝐧𝐠 𝐁𝐞𝐬𝐭 𝐓𝐫𝐚𝐜𝐤 ♡ {0} ",
    "𝐋𝐨𝐚𝐝𝐢𝐧𝐠 𝐌𝐮𝐬𝐢𝐜 ✦ {0} ",
    "𝐘𝐨𝐮𝐫 𝐕𝐢𝐛𝐞 𝐈𝐬 𝐂𝐨𝐦𝐢𝐧𝐠 ꨄ︎ {0} ",
    "𝐏𝐥𝐚𝐲𝐢𝐧𝐠 𝐒𝐨𝐨𝐧 𝐁𝐚𝐛𝐲 ♡ {0} ",
    "𝐆𝐞𝐭𝐭𝐢𝐧𝐠 𝐑𝐞𝐚𝐝𝐲 𝐅𝐨𝐫 𝐘𝐨𝐮 ✦ {0} ",
    "𝐇𝐨𝐥𝐝 𝐎𝐧 𝐁𝐚𝐛𝐞 ꨄ︎ {0} ",
    "𝐌𝐮𝐬𝐢𝐜 𝐋𝐨𝐚𝐝𝐢𝐧𝐠 𝐅𝐨𝐫 ♡ {0} ",
    "𝐀𝐥𝐦𝐨𝐬𝐭 𝐑𝐞𝐚𝐝𝐲 𝐉𝐚𝐚𝐧 ꨄ︎ {0} ",
    "𝐏𝐫𝐞𝐩𝐚𝐫𝐢𝐧𝐠 𝐘𝐨𝐮𝐫 𝐓𝐫𝐚𝐜𝐤 ✦ {0} ",
]

AYUV = [
    "💌✨ ʜᴇʏ {0} 💞🌸\n\n🎶 ɪ'ᴍ {1} 💖 ʏᴏᴜʀ ᴘᴏᴡᴇʀꜰᴜʟ ᴍᴜꜱɪᴄ ʙᴏᴛ 🎧🔥\n\n┣━━━━━━━━━━━━━━━⧫\n┃ 🌟 ꜱᴛʀᴇᴀᴍ ᴍᴜꜱɪᴄ ɪɴ ᴠᴄ\n┃ 🎵 ʏᴏᴜᴛᴜʙᴇ • ꜱᴘᴏᴛɪꜰʏ • ᴊɪᴏꜱᴀᴀᴠɴ\n┃ ⚡ ꜰᴀꜱᴛ & ꜱᴍᴏᴏᴛʜ ᴘʟᴀʏʙᴀᴄᴋ\n┃ 💫 24x7 ᴍᴜꜱɪᴄ ᴠɪʙᴇꜱ\n┗━━━━━━━━━━━━━━━⧫\n\n💖 ᴊᴜꜱᴛ ᴀᴅᴅ ᴍᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ & ꜱᴛᴀʀᴛ ᴛʜᴇ ᴘᴀʀᴛʏ 🎉",

    "🌹✨ ᴡᴇʟᴄᴏᴍᴇ {0} 💕\n\n🎧 {1} ɪꜱ ʜᴇʀᴇ ᴛᴏ ᴍᴀᴋᴇ ʏᴏᴜʀ ᴠᴄ ᴀᴡᴇꜱᴏᴍᴇ 💫🔥\n\n┣━━━━━━━━━━━━━━━⧫\n┃ 🎶 ʜɪɢʜ Qᴜᴀʟɪᴛʏ ᴍᴜꜱɪᴄ\n┃ 🚀 ꜰᴀꜱᴛ ꜱᴛʀᴇᴀᴍɪɴɢ\n┃ 💞 ᴍᴜʟᴛɪ-ᴘʟᴀᴛꜰᴏʀᴍ ꜱᴜᴘᴘᴏʀᴛ\n┃ 🌸 ꜱᴍᴀʀᴛ & ᴇᴀꜱʏ ᴄᴏᴍᴍᴀɴᴅꜱ\n┗━━━━━━━━━━━━━━━⧫\n\n✨ ᴛʏᴘᴇ /play ᴀɴᴅ ᴇɴᴊᴏʏ ɴᴏɴ-ꜱᴛᴏᴘ ᴍᴜꜱɪᴄ 🎵🦋"
]

# ── Runtime structures ──────────────────────────────────────────────────────
BANNED_USERS = filters.user()
adminlist, lyrical, votemode, autoclean, confirmer = {}, {}, {}, [], {}

# ── Minimal validation ──────────────────────────────────────────────────────
if SUPPORT_CHANNEL and not re.match(r"^https?://", SUPPORT_CHANNEL):
    raise SystemExit("[ERROR] - Invalid SUPPORT_CHANNEL URL. Must start with https://")

if SUPPORT_CHAT and not re.match(r"^https?://", SUPPORT_CHAT):
    raise SystemExit("[ERROR] - Invalid SUPPORT_CHAT URL. Must start with https://")

if not COOKIE_URL:
    COOKIE_URL = None

# Only allow these cookie link formats
if COOKIE_URL and not re.match(r"^https://(batbin\.me|pastebin\.com)/[A-Za-z0-9]+$", COOKIE_URL):
    raise SystemExit("[ERROR] - Invalid COOKIE_URL. Use https://batbin.me/<id> or https://pastebin.com/<id>")
    
    
print("""
╔════════════════════════════════════╗
║🎵 𝗩𝗜𝗦𝗛𝗔𝗟 𝗠𝗨𝗦𝗜𝗖 𝗕𝗢𝗧 𝗣𝗥𝗘𝗠𝗜𝗨𝗠 𝗘𝗗𝗜𝗧𝗜𝗢𝗡  
║       ✦ 𝗖𝗼𝗻𝗳𝗶𝗴 𝗟𝗼𝗮𝗱𝗲𝗱 𝗦𝘂𝗰𝗰𝗲𝘀𝘀! ✦   
╚════════════════════════════════════╝
""")

# ═══════════════════════════════════════════════════════════
#         🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
