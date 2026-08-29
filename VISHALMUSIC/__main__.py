# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   GitHub : github.com/ItsMeVishal0/VishalMusic
#   Developer : @ItsMeVishalBots | Telegram
#   Module : Bot Startup, Flask Dashboard & Main Loop
# ═══════════════════════════════════════════════════════════

import asyncio
import importlib
import os
import time
from threading import Thread

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from VISHALMUSIC import LOGGER, app, userbot
from VISHALMUSIC.core.call import VISHAL
from VISHALMUSIC.misc import sudo
from VISHALMUSIC.plugins import ALL_MODULES
from VISHALMUSIC.utils.database import get_banned_users, get_gbanned
from VISHALMUSIC.utils.cookie_handler import fetch_and_store_cookies
from config import BANNED_USERS


async def _cookie_refresh_loop() -> None:
    """Periodically re-fetch YouTube cookies.

    Cookies are fetched only once at startup; YouTube invalidates them over
    time, after which every download silently fails (assistant joins the VC
    but no song ever plays). Refreshing keeps the bot healthy on long uptime.
    """
    hours = float(os.environ.get("COOKIE_REFRESH_HOURS", "12"))
    while True:
        await asyncio.sleep(hours * 3600)
        try:
            await fetch_and_store_cookies()
            LOGGER("VISHALMUSIC").info("ʏᴏᴜᴛᴜʙᴇ ᴄᴏᴏᴋɪᴇs ʀᴇꜰʀᴇꜱʜᴇᴅ ✔")
        except Exception as e:
            LOGGER("VISHALMUSIC").warning(f"⚠️ ᴄᴏᴏᴋɪᴇ ʀᴇꜰʀᴇꜱʜ ꜰᴀɪʟᴇᴅ: {e}")


async def _auto_restart_loop(hours: float) -> None:
    """Optional watchdog: restart the bot process every N hours.

    Long-running bots degrade over time (stale pytgcalls calls, memory
    growth, dropped sessions). A periodic restart is the standard fix.
    Enable by setting AUTO_RESTART_HOURS in the environment (e.g. 24).
    """
    import sys

    while True:
        await asyncio.sleep(hours * 3600)
        LOGGER("VISHALMUSIC").info(f"🔄 ᴀᴜᴛᴏ-ʀᴇꜱᴛᴀʀᴛ ᴀꜰᴛᴇʀ {hours}h ᴏꜰ ᴜᴘᴛɪᴍᴇ...")
        try:
            os.execv(sys.executable, [sys.executable, "-m", "VISHALMUSIC"])
        except Exception as e:
            LOGGER("VISHALMUSIC").error(f"❌ ᴀᴜᴛᴏ-ʀᴇꜱᴛᴀʀᴛ ꜰᴀɪʟᴇᴅ: {e}")
            return


async def init():
    if (
        not config.STRING1
        and not config.STRING2
        and not config.STRING3
        and not config.STRING4
        and not config.STRING5
    ):
        LOGGER(__name__).error("ᴀssɪsᴛᴀɴᴛ sᴇssɪᴏɴ ɴᴏᴛ ғɪʟʟᴇᴅ, ᴘʟᴇᴀsᴇ ғɪʟʟ ᴀ ᴘʏʀᴏɢʀᴀᴍ sᴇssɪᴏɴ...")
        exit()

    # ✅ Try to fetch cookies at startup
    try:
        await fetch_and_store_cookies()
        LOGGER("VISHALMUSIC").info("ʏᴏᴜᴛᴜʙᴇ ᴄᴏᴏᴋɪᴇs ʟᴏᴀᴅᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ✅")
    except Exception as e:
        LOGGER("VISHALMUSIC").warning(f"⚠️ ᴄᴏᴏᴋɪᴇ ᴇʀʀᴏʀ: {e}")

    await sudo()

    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except:
        pass

    await app.start()
    for all_module in ALL_MODULES:
        try:
            importlib.import_module("VISHALMUSIC.plugins" + all_module)
        except Exception as e:
            # One broken plugin (e.g. missing env key) must never kill the bot.
            LOGGER("VISHALMUSIC.plugins").error(
                f"❌ Failed to load module {all_module}: {e}\nBot continues without it."
            )

    LOGGER("VISHALMUSIC.plugins").info("ᴍᴏᴅᴜʟᴇs ʟᴏᴀᴅᴇᴅ...")

    await userbot.start()
    await VISHAL.start()

    # Clone bots (CLONE_BOT=1) log group VC me test NAHI karte — wo shared
    # assistant use karte hain aur log channel ke member nahi hote.
    if os.environ.get("CLONE_BOT") != "1":
        try:
            await VISHAL.stream_call("https://files.catbox.moe/euj0oc.mp4")
        except NoActiveGroupCall:
            LOGGER("VISHALMUSIC").error(
                "ᴘʟᴇᴀsᴇ ᴛᴜʀɴ ᴏɴ ᴛʜᴇ ᴠᴏɪᴄᴇ ᴄʜᴀᴛ ᴏғ ʏᴏᴜʀ ʟᴏɢ ɢʀᴏᴜᴘ/ᴄʜᴀɴɴᴇʟ.\n\nʙᴏᴛ sᴛᴏᴘᴘᴇᴅ..."
            )
            exit()
        except:
            pass

    await VISHAL.decorators()

    # Clone system: master restart par saare running clones wapas spawn karo.
    try:
        from VISHALMUSIC.plugins.tools.clone import resurrect_clones

        await resurrect_clones()
    except Exception as e:
        LOGGER("VISHALMUSIC").warning(f"⚠️ ᴄʟᴏɴᴇ ʀᴇsᴜʀʀᴇᴄᴛɪᴏɴ sᴋɪᴘᴘᴇᴅ: {e}")

    # Long-uptime health: refresh YouTube cookies periodically and optionally
    # auto-restart the process so the bot never silently degrades.
    asyncio.create_task(_cookie_refresh_loop())
    auto_restart_hours = float(os.environ.get("AUTO_RESTART_HOURS", "0"))
    if auto_restart_hours > 0:
        asyncio.create_task(_auto_restart_loop(auto_restart_hours))
        LOGGER("VISHALMUSIC").info(f"🔄 ᴀᴜᴛᴏ-ʀᴇꜱᴛᴀʀᴛ ᴇɴᴀʙʟᴇᴅ: ᴇᴠᴇʀʏ {auto_restart_hours}h")

    LOGGER("VISHALMUSIC").info("✅ Vishal music Bot Started Successfully!")
    await idle()
    await app.stop()
    await userbot.stop()
    LOGGER("VISHALMUSIC").info("sᴛᴏᴘᴘɪɴɢ ᴍᴜsɪᴄ ʙᴏᴛ ...")


# ----------------------🔹 Render Flask Dashboard 🔹----------------------

def keep_alive():
    try:
        from flask import Flask, jsonify
        from pymongo import MongoClient
    except ImportError:
        return

    def run_flask():
        fapp = Flask(__name__)

        try:
            _sync_mongo = MongoClient(config.MONGO_DB_URI, serverSelectionTimeoutMS=3000)
            _sync_db = _sync_mongo.Vishal
        except Exception:
            _sync_db = None

        _start_time = time.time()

        @fapp.route('/')
        def home():
            try:
                uptime_sec = int(time.time() - _start_time)
                hours, remainder = divmod(uptime_sec, 3600)
                minutes, seconds = divmod(remainder, 60)
                uptime_str = f"{hours}h {minutes}m {seconds}s"

                total_users = total_chats = total_banned = total_sudoers = 0
                if _sync_db is not None:
                    try:
                        total_users = _sync_db.tgusersdb.count_documents({})
                        total_chats = _sync_db.chats.count_documents({})
                        total_banned = _sync_db.blockedusers.count_documents({})
                        sudo_data = _sync_db.sudoers.find_one({"sudo": "sudo"})
                        total_sudoers = len(sudo_data.get("sudoers", [])) if sudo_data else 0
                    except Exception as db_error:
                        LOGGER("VISHALMUSIC").warning(f"DB stats error: {db_error}")

                return f"""<!DOCTYPE html>
<html><head><title>Vishal Music Bot</title>
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="refresh" content="30">
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:'Segoe UI',sans-serif;background:linear-gradient(135deg,#0f0c29,#302b63,#24243e);min-height:100vh;color:#fff;padding:20px}}
.c{{max-width:800px;margin:0 auto}}
.h{{text-align:center;padding:30px 0}}
.h h1{{font-size:2.2em;background:linear-gradient(90deg,#7c6cff,#00ff88);-webkit-background-clip:text;-webkit-text-fill-color:transparent}}
.sb{{display:inline-flex;align-items:center;gap:8px;background:rgba(0,255,136,.1);border:1px solid rgba(0,255,136,.3);padding:8px 20px;border-radius:30px;margin-top:15px}}
.dot{{width:10px;height:10px;background:#00ff88;border-radius:50%;animation:p 2s infinite}}
@keyframes p{{0%,100%{{opacity:1}}50%{{opacity:.3}}}}
.sg{{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:15px;margin:30px 0}}
.sc{{background:rgba(255,255,255,.05);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,.08);border-radius:16px;padding:25px 20px;text-align:center;transition:transform .2s}}
.sc:hover{{transform:translateY(-3px)}}
.sc .i{{font-size:1.8em}}.sc .v{{font-size:1.6em;font-weight:bold;margin:8px 0 4px;color:#00ff88}}.sc .l{{color:#888;font-size:.85em}}
.ib{{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:12px;padding:20px;margin-top:20px}}
.ir{{display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid rgba(255,255,255,.05)}}
.ir:last-child{{border:none}}.ir .k{{color:#888}}.ir .vl{{color:#ddd;font-weight:500}}
.f{{text-align:center;margin-top:30px;color:#555;font-size:.8em}}.f a{{color:#7c6cff;text-decoration:none}}
</style></head><body><div class="c">
<div class="h"><h1>🎵 Vishal Music Bot</h1><div class="sb"><span class="dot"></span><span style="color:#00ff88;font-size:.9em">Online & Running</span></div></div>
<div class="sg">
<div class="sc"><div class="i">👥</div><div class="v">{total_users}</div><div class="l">Total Users</div></div>
<div class="sc"><div class="i">💬</div><div class="v">{total_chats}</div><div class="l">Total Chats</div></div>
<div class="sc"><div class="i">🚫</div><div class="v">{total_banned}</div><div class="l">Banned Users</div></div>
<div class="sc"><div class="i">👑</div><div class="v">{total_sudoers}</div><div class="l">Sudo Users</div></div>
</div>
<div class="ib">
<div class="ir"><span class="k">⏱️ Uptime</span><span class="vl">{uptime_str}</span></div>
<div class="ir"><span class="k">🤖 Bot Name</span><span class="vl">{config.BOT_NAME}</span></div>
<div class="ir"><span class="k">👤 Owner</span><span class="vl">@{config.OWNER_USERNAME}</span></div>
<div class="ir"><span class="k">🌍 Languages</span><span class="vl">15 Supported</span></div>
</div>
<div class="f"><p>Auto-refreshes every 30s</p><p style="margin-top:8px"><a href="https://t.me/{config.BOT_USERNAME}">Open Bot</a> • <a href="https://t.me/ItsMeVishalBots">Developer</a></p></div>
</div></body></html>"""
            except Exception as e:
                LOGGER("VISHALMUSIC").error(f"Flask home error: {e}")
                return f"Error: {str(e)}", 500

        @fapp.route('/health')
        def health():
            return "OK", 200

        @fapp.route('/api/stats')
        def api_stats():
            if _sync_db is None:
                return jsonify({"error": "DB not connected", "status": "error"}), 200
            try:
                return jsonify({
                    "users": _sync_db.tgusersdb.count_documents({}),
                    "chats": _sync_db.chats.count_documents({}),
                    "banned": _sync_db.blockedusers.count_documents({}),
                    "uptime": int(time.time() - _start_time),
                    "status": "running"
                })
            except Exception as e:
                LOGGER("VISHALMUSIC").error(f"Flask API stats error: {e}")
                return jsonify({"error": str(e), "status": "error"}), 200

        port = int(os.environ.get("PORT", 3000))
        fapp.run(host="0.0.0.0", port=port)

    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# ----------------------------------------------------------------------

if __name__ == "__main__":
    # Start Flask web server on port 3000 automatically (works on VPS/Local/Render)
    keep_alive()
    asyncio.get_event_loop().run_until_complete(init())

# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
