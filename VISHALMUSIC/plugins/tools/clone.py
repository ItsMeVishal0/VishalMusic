# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   GitHub : github.com/ItsMeVishal0/VishalMusic
#   Developer : @ItsMeVishalBots | Telegram
#   Module : Clone System (/clone, /clones, /unclone)
# ═══════════════════════════════════════════════════════════
# Clone system: user /clone <BOT_TOKEN> dalta hai → us token se
# naya bot process spawn hota hai (same source, shared DB). Us bot
# ka owner = command dene wala. Master restart par saare running
# clones khud wapas start ho jaate hain.
# ═══════════════════════════════════════════════════════════

import asyncio
import os
import signal
import subprocess
import sys
from datetime import datetime

import aiohttp
from pyrogram import Client, filters
from pyrogram.types import Message

from VISHALMUSIC import LOGGER, app
from VISHALMUSIC.core.mongo import mongodb
from VISHALMUSIC.misc import SUDOERS
from VISHALMUSIC.utils.decorators.language import language

clones_col = mongodb.clones
BASE_PORT = 3001


def _alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
    except Exception:
        return False
    # zombie processes (<defunct>) "alive" dikhte hain lekin chale nahi —
    # resurrection unhe skip na kare isliye zombie check karo.
    try:
        with open(f"/proc/{pid}/stat") as _st:
            state = _st.read().split()[2]
            if state == "Z":
                return False
    except Exception:
        pass
    return True


async def _validate_token(token: str):
    """Bot API getMe se token check (username + bot id)."""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.telegram.org/bot{token}/getMe", timeout=10
            ) as resp:
                data = await resp.json()
                if data.get("ok"):
                    u = data["result"]
                    return u.get("username"), u.get("id")
    except Exception as e:
        LOGGER("VISHALMUSIC.clone").warning(f"validate token error: {e}")
    return None, None


def spawn_clone_process(token: str, username: str, port: int) -> int:
    """Naya clone bot process spawn karo — env override se naya token.
    load_dotenv() existing env vars override nahi karta, isliye ye naya
    BOT_TOKEN automatically .env wale token ko beat karega."""
    env = {
        **os.environ,
        "BOT_TOKEN": token,
        "CLONE_BOT": "1",
        "PORT": str(port),
        # Unique assistant storage files per clone → no .session corruption
        "ASSISTANT_CLIENT_SUFFIX": f"_{username}",
    }
    logf = open(f"clone_{username}.log", "a", encoding="utf-8")
    proc = subprocess.Popen(
        [sys.executable, "-m", "VISHALMUSIC"],
        cwd=os.getcwd(),
        env=env,
        stdout=logf,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )
    return proc.pid


async def _free_port() -> int:
    used = set()
    async for doc in clones_col.find({"status": "running"}):
        if doc.get("port"):
            used.add(int(doc["port"]))
    p = BASE_PORT
    while p in used:
        p += 1
    return p


async def resurrect_clones() -> None:
    """Master restart par saare 'running' clones wapas spawn karo."""
    if os.environ.get("CLONE_BOT") == "1":
        return
    try:
        async for doc in clones_col.find({"status": "running"}):
            pid = doc.get("pid")
            if pid and _alive(int(pid)):
                continue
            try:
                port = int(doc.get("port") or await _free_port())
                new_pid = spawn_clone_process(doc["token"], doc["username"], port)
                await clones_col.update_one(
                    {"_id": doc["_id"]},
                    {"$set": {"pid": new_pid, "port": port, "status": "running"}},
                )
                LOGGER("VISHALMUSIC.clone").info(
                    f"clone resurrected: @{doc['username']} (pid {new_pid})"
                )
            except Exception as e:
                LOGGER("VISHALMUSIC.clone").error(
                    f"resurrect @{doc['username']} failed: {e}"
                )
    except Exception as e:
        LOGGER("VISHALMUSIC.clone").warning(f"resurrect_clones error: {e}")


@app.on_message(filters.command("clone") & filters.private & ~filters.bot)
@language
async def clone_cmd(client: Client, message: Message, _):
    cmd = message.command
    if len(cmd) < 2:
        return await message.reply_text(
            "  🤖 𝗖𝗟𝗢𝗡𝗘 𝗬𝗢𝗨𝗥 𝗕𝗢𝗧\n\n"
            "⚡ 𝗨𝘀𝗲 : \"/clone BOT_TOKEN\"\n\n"
            "🔹 🌺 Create a new bot using 𝗕𝗼𝘁𝗙𝗮𝘁𝗵𝗲𝗿\n"
            "  ↳ 🤖 @BotFather\n\n"
            "🔹 ❤️ Send \"/newbot\"\n"
            "  ↳ 🔑 Copy your 𝗕𝗼𝘁 𝗧𝗼𝗸𝗲𝗻\n\n"
            "🔹 💐Send \"/clone\" here\n"
            "  ↳ 🚀 Your 𝗖𝗹𝗼𝗻𝗲 𝗕𝗼𝘁 will be created instantly!\n\n"
            "━━━━━━━━━━━━━━━━━━\n\n"
            "🗑️ 𝗧𝗼 𝗥𝗲𝗺𝗼𝘃𝗲 𝗬𝗼𝘂𝗿 𝗖𝗹𝗼𝗻𝗲\n"
            "  ↳ \"/unclone\""
        )

    token = cmd[1].strip()
    status = await message.reply_text("🔍 ᴛᴏᴋᴇɴ ᴄʜᴇᴄᴋ ʜᴏ ʀᴀʜᴀ ʜᴀɪ...")

    username, bot_id = await _validate_token(token)
    if not username:
        return await status.edit_text("❌ ɪɴᴠᴀʟɪᴅ ᴛᴏᴋᴇɴ — @BotFather se sahi token bhejo.")

    dup = await clones_col.find_one({"$or": [{"token": token}, {"username": username}]})
    if dup:
        return await status.edit_text(f"❌ @{username} ᴘᴇʜʟᴇ sᴇ ʀᴇɢɪsᴛᴇʀᴇᴅ ʜᴀɪ.")

    mine = await clones_col.count_documents({"owner_id": message.from_user.id})
    if mine >= 1:
        return await status.edit_text(
            "❌ ᴀᴀᴘ ᴇᴋ ᴄʟᴏɴᴇ ᴘᴇʜʟᴇ sᴇ ʙᴀɴᴀ ᴄʜᴜᴋᴇ ʜᴏ — /unclone kar ke naya banao."
        )

    port = await _free_port()
    try:
        new_pid = spawn_clone_process(token, username, port)
    except Exception as e:
        return await status.edit_text(f"❌ ᴄʟᴏɴᴇ sᴛᴀʀᴛ ɴʜɪ ʜᴜᴀ: {e}")

    await clones_col.insert_one(
        {
            "username": username,
            "bot_id": bot_id,
            "token": token,
            "owner_id": message.from_user.id,
            "pid": new_pid,
            "port": port,
            "status": "running",
            "created_at": datetime.utcnow().isoformat(),
        }
    )

    # Clone ka owner = command dene wala (turant set — /start ka wait nahi)
    try:
        owner_doc = await mongodb[f"owner_{username}"].find_one({})
        if owner_doc:
            await mongodb[f"owner_{username}"].update_one(
                {"_id": owner_doc["_id"]}, {"$set": {"owner": message.from_user.id}}
            )
        else:
            await mongodb[f"owner_{username}"].insert_one({"owner": message.from_user.id})
    except Exception:
        pass

    return await status.edit_text(
        f"✅ ᴄʟᴏɴᴇ ʙᴏᴛ ʙᴀɴ ɢʏᴀ!\n\n"
        f"🤖 @{username}\n"
        f"👤 ᴏᴡɴᴇʀ : ᴛᴜᴍ\n"
        f"🔄 sᴛᴀᴛᴜs : ʀᴜɴɴɪɴɢ\n\n"
        f"Ab us bot ko DM me /start karo — saare features chalenge. 🚀"
    )


@app.on_message(filters.command("clones") & filters.private)
@language
async def clones_list(client: Client, message: Message, _):
    if message.from_user.id not in SUDOERS:
        return
    text = "📋 ᴄʟᴏɴᴇ ʙᴏᴛs :\n\n"
    count = 0
    async for doc in clones_col.find():
        count += 1
        alive = _alive(int(doc.get("pid") or 0)) if doc.get("pid") else False
        st = "🟢" if doc.get("status") == "running" and alive else "🔴"
        text += f"{st} @{doc['username']} | ᴘɪᴅ: {doc.get('pid')} | ᴏᴡɴᴇʀ: {doc.get('owner_id')}\n"
    if count == 0:
        text += "ᴋᴏɪ ᴄʟᴏɴᴇ ɴʜɪ ʜᴀɪ."
    await message.reply_text(text)


@app.on_message(filters.command("unclone") & filters.private)
@language
async def unclone_cmd(client: Client, message: Message, _):
    if message.from_user.id not in SUDOERS:
        return
    cmd = message.command
    if len(cmd) < 2:
        return await message.reply_text("Usᴇ : <code>/unclone username</code>")
    username = cmd[1].strip().lstrip("@").lower()
    doc = await clones_col.find_one({"username": username})
    if not doc:
        return await message.reply_text("❌ ᴄʟᴏɴᴇ ɴʜɪ ᴍɪʟᴀ.")
    pid = doc.get("pid")
    if pid:
        try:
            os.kill(int(pid), signal.SIGKILL)
        except Exception:
            pass
    await clones_col.update_one({"_id": doc["_id"]}, {"$set": {"status": "stopped"}})
    await message.reply_text(f"🛑 @{username} ᴋᴀ ᴄʟᴏɴᴇ ʙᴀɴᴅ ᴋᴀʀ ᴅɪʏᴀ.")


# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
