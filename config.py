import re
from os import getenv
from dotenv import load_dotenv
from pyrogram import filters

# Load environment variables from .env file
load_dotenv()

# ── Core bot config ────────────────────────────────────────────────────────────
API_ID = int(getenv("API_ID", 26493077))
API_HASH = getenv("API_HASH", "6586f0276c7748e54684719bdd247d90")
BOT_TOKEN = getenv("BOT_TOKEN")

OWNER_ID = int(getenv("OWNER_ID", 7044783841))
OWNER_USERNAME = getenv("OWNER_USERNAME", "Its_me_Vishall")
BOT_USERNAME = getenv("BOT_USERNAME", "Shrutimusic_bot")
BOT_NAME = getenv("BOT_NAME", "𝐒ʜʀᴜᴛɪ ✘ 𝙼ᴜsɪᴄ˼ ♪")
ASSUSERNAME = getenv("ASSUSERNAME", "𝐒ʜʀᴜᴛɪ ✘ ᴀꜱꜱɪꜱᴛᴀɴᴛ˼")

# ── Database & logging ─────────────────────────────────────────────────────────
MONGO_DB_URI = getenv("MONGO_DB_URI")
LOGGER_ID = int(getenv("LOGGER_ID", -1002425220992))

# ── Limits (durations in min/sec; sizes in bytes) ──────────────────────────────
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 300))
SONG_DOWNLOAD_DURATION = int(getenv("SONG_DOWNLOAD_DURATION", "1200"))
SONG_DOWNLOAD_DURATION_LIMIT = int(getenv("SONG_DOWNLOAD_DURATION_LIMIT", "1800"))
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", "157286400"))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", "1288490189"))
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", "30"))

# ── External APIs ──────────────────────────────────────────────────────────────
COOKIE_URL = getenv("COOKIE_URL")  # required (paste link)
API_URL = getenv("API_URL")        # optional
API_KEY = getenv("API_KEY")        # optional
DEEP_API = getenv("DEEP_API")      # optional

# ── Hosting / deployment ───────────────────────────────────────────────────────
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
HEROKU_API_KEY = getenv("HEROKU_API_KEY")

# ── Git / updates ──────────────────────────────────────────────────────────────
UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/Vishalisback00/VishalXmusic")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "Master")
GIT_TOKEN = getenv("GIT_TOKEN")  # needed if repo is private

# ── Support links ──────────────────────────────────────────────────────────────
SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/ItsMeVishalBots")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/ItsMeVishalSupport")

# ── Assistant auto-leave ───────────────────────────────────────────────────────
AUTO_LEAVING_ASSISTANT = False
AUTO_LEAVE_ASSISTANT_TIME = int(getenv("ASSISTANT_LEAVE_TIME", "3600"))

# ── Debug ──────────────────────────────────────────────────────────────────────
DEBUG_IGNORE_LOG = True

# ── Spotify (optional) ─────────────────────────────────────────────────────────
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "22b6125bfe224587b722d6815002db2b")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "c9c63c6fbf2f467c8bc68624851e9773")

# ── Session strings (optional) ─────────────────────────────────────────────────
STRING1 = getenv("STRING_SESSION")
STRING2 = getenv("STRING_SESSION2")
STRING3 = getenv("STRING_SESSION3")
STRING4 = getenv("STRING_SESSION4")
STRING5 = getenv("STRING_SESSION5")

# ── Media assets ───────────────────────────────────────────────────────────────
START_VIDS = [
    "https://files.catbox.moe/7rie2i.mp4",
    "https://files.catbox.moe/j3ba3f.mp4",
    "https://files.catbox.moe/mfeisv.mp4",
    "https://files.catbox.moe/ot88at.mp4",
    "https://files.catbox.moe/bv29a4.mp4",
    "https://files.catbox.moe/pndpqt.mp4",
    "https://files.catbox.moe/tu8l7e.mp4",
    "https://files.catbox.moe/7ygvch.mp4",
    "https://files.catbox.moe/jh55tl.mp4",
]
STICKERS = [
    "CAACAgUAAx0Cd6nKUAACASBl_rnalOle6g7qS-ry-aZ1ZpVEnwACgg8AAizLEFfI5wfykoCR4h4E",
    "CAACAgUAAx0Cd6nKUAACATJl_rsEJOsaaPSYGhU7bo7iEwL8AAPMDgACu2PYV8Vb8aT4_HUPHgQ",
]
HELP_IMG_URL = "https://files.catbox.moe/yg2vky.jpg"
PING_VID_URL = "https://telegra.ph/file/528d0563175669e123a75.mp4"
PLAYLIST_IMG_URL = "https://files.catbox.moe/xxzlq3.jpg"
STATS_VID_URL = "https://files.catbox.moe/ch7geb.mp4"
TELEGRAM_AUDIO_URL = "https://files.catbox.moe/48shlf.jpg"
TELEGRAM_VIDEO_URL = "https://files.catbox.moe/48shlf.jpg"
STREAM_IMG_URL = "https://files.catbox.moe/48shlf.jpg"
SOUNCLOUD_IMG_URL = "https://files.catbox.moe/48shlf.jpg"
YOUTUBE_IMG_URL = "https://files.catbox.moe/48shlf.jpg"
SPOTIFY_ARTIST_IMG_URL = SPOTIFY_ALBUM_IMG_URL = SPOTIFY_PLAYLIST_IMG_URL = YOUTUBE_IMG_URL

# ── Helpers ────────────────────────────────────────────────────────────────────
def time_to_seconds(time: str) -> int:
    return sum(int(x) * 60**i for i, x in enumerate(reversed(time.split(":"))))

DURATION_LIMIT = time_to_seconds(f"{DURATION_LIMIT_MIN}:00")

# ───── Bot Introduction Messages ───── #
AYU = [
    "❤️", "💞", "🩷", "💋", "🌹", "💫", "💖", "✨", "💘", "💝",
    "💕", "💗", "💓", "💟", "❣️", "🌸", "🌼", "💐", "🪷", "🌺",
    "💎", "🌙", "🌟", "🌈", "🦋", "🥰", "😍", "😘", "😚", "😻",
    "🤍", "💛", "💚", "💙", "💜", "🖤", "🤎", "🩵", "🩶", "💏",
    "💑", "💍", "💌", "💎", "🌹", "💖", "💘", "💝", "💗", "💞",
    "❤️‍🔥", "❤️‍🩹", "💓", "💟", "💃", "🕺", "🎶", "🎵", "🎧", "💫",
    "✨", "🌈", "🌸", "🌺", "🌷", "🌼", "🍀", "🥂", "🍫", "🍓",
    "🍒", "🍑", "🫶", "🤗", "🤭", "🥹", "💃", "🎀", "💄", "💅",
    "🕊️", "🐦", "🌌", "🎇", "🎆", "🌠", "🪩", "🎉", "🎊", "🥳",
    "💞", "💖", "💘", "💝", "💗", "💓", "❤️", "💋", "🌹", "✨",
    "💫", "🌈", "🦋", "💟", "💍", "💎", "🌸", "🥰", "😍", "💌"
]

AYUV = [
    "💌✨ ʜᴇʟʟᴏ {0} 💞🦋\n\n🌹 ɪᴛ'ꜱ ᴍᴇ {1} 💖💫\n\n┏━━━━━━━━━━━━━━━⧫\n┃ 💫 ꜱᴜᴘᴘᴏʀᴛᴇᴅ ᴘʟᴀᴛꜰᴏʀᴍꜱ:\n┃ 🎵 ʏᴏᴜᴛᴜʙᴇ | ꜱᴘᴏᴛɪꜰʏ | ʀᴇꜱꜱᴏ | ᴀᴘᴘʟᴇᴍᴜꜱɪᴄ | ꜱᴏᴜɴᴅᴄʟᴏᴜᴅ 💌\n┃\n┃ 🔥 ᴜᴘᴛɪᴍᴇ : {2} 🌙\n┃ 💖 ꜱᴇʀᴠᴇʀ sᴛᴏʀᴀɢᴇ : {3} 💫\n┃ ⚡ ᴄᴘᴜ ʟᴏᴀᴅ : {4} 💞\n┃ 🩷 ʀᴀᴍ ᴄᴏɴsᴜᴍᴘᴛɪᴏɴ : {5} 🦋\n┃ 🌈 ᴜsᴇʀs : {6} 💌\n┃ 🕊️ ᴄʜᴀᴛs : {7} 💫\n┗━━━━━━━━━━━━━━━⧫\n\n💌 ᴅᴇᴠᴇʟᴏᴩᴇʀ ➪ [»»—⎯⁠⁠⁠⁠‌꯭꯭νιѕнαL𝅃 ₊꯭♡゙꯭. »︎](https://t.me/Its_me_Vishall) 🌹✨",

    "💖🌹 ʜɪ {0} 💫🦋\n\n✨ ɪ'ᴍ {1} 💞 ᴛᴇʟᴇɢʀᴀᴍ ᴍᴜꜱɪᴄ ʙᴏᴛ 🔥\n\n┏━━━━━━━━━━━━━━━⧫\n┃ 🌟 ꜰᴇᴀᴛᴜʀᴇꜱ:\n┃ 🎵 sᴜᴘᴇʀꜰᴀsᴛ ᴠᴄ ᴘʟᴀʏᴇʀ 💌\n┃ 🎶 ᴘʟᴀʏ ᴍᴜꜱɪᴄ & ᴠɪᴅᴇᴏ 💫\n┃ 🌈 ʟɪᴠᴇ ꜱᴛʀᴇᴀᴍɪɴɢ 🕊️\n┃ 🩷 24x7 ᴍᴜꜱɪᴄ ᴄʜɪʟʟ 💖\n┃ 💌 ɴᴏ ᴘʀᴏᴍᴏ 🌹\n┃\n┃ 🔥 ᴜᴘᴛɪᴍᴇ : {2} 💫\n┃ 💖 ꜱᴇʀᴠᴇʀ sᴛᴏʀᴀɢᴇ : {3} 🌈\n┃ ⚡ ᴄᴘᴜ ʟᴏᴀᴅ : {4} 💞\n┃ 🩷 ʀᴀᴍ ᴄᴏɴsᴜᴍᴘᴛɪᴏɴ : {5} 🦋\n┃ 🌹 ᴜsᴇʀs : {6} 💌\n┃ 🕊️ ᴄʜᴀᴛs : {7} 💫\n┗━━━━━━━━━━━━━━━⧫\n\n💌 ᴅᴇᴠᴇʟᴏᴩᴇʀ ➪ [»»—⎯⁠⁠⁠⁠‌꯭꯭νιѕнαL𝅃 ₊꯭♡゙꯭. »](https://t.me/Its_me_Vishall) 💖🌸",
]

# ── Runtime structures ─────────────────────────────────────────────────────────
BANNED_USERS = filters.user()
adminlist, lyrical, votemode, autoclean, confirmer = {}, {}, {}, [], {}

# ── Minimal validation ─────────────────────────────────────────────────────────
if SUPPORT_CHANNEL and not re.match(r"^https?://", SUPPORT_CHANNEL):
    raise SystemExit("[ERROR] - Invalid SUPPORT_CHANNEL URL. Must start with https://")

if SUPPORT_CHAT and not re.match(r"^https?://", SUPPORT_CHAT):
    raise SystemExit("[ERROR] - Invalid SUPPORT_CHAT URL. Must start with https://")

if not COOKIE_URL:
    raise SystemExit("[ERROR] - COOKIE_URL is required.")

# Only allow these cookie link formats
if not re.match(r"^https://(batbin\.me|pastebin\.com)/[A-Za-z0-9]+$", COOKIE_URL):
    raise SystemExit("[ERROR] - Invalid COOKIE_URL. Use https://batbin.me/<id> or https://pastebin.com/<id>")
