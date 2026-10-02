# ═══════════════════════════════════════════════════════════
#        🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   GɪᴛHᴜʙ : github.com/ItsMeVishal0/VishalMusic
#   Dᴇᴠʟᴏᴘᴇʀ : @ItsMeVishalBots | Telegram
# ═══════════════════════════════════════════════════════════

import asyncio
from logging import getLogger
from typing import Dict, Set
import random

from pyrogram import filters
from pyrogram.types import Message

from pyrogram.raw import functions
try:
    from VISHALMUSIC import app
    from VISHALMUSIC.utils.database import get_assistant
    from VISHALMUSIC.core.mongo import mongodb
except ImportError:
    from VishalMusic import app
    from VishalMusic.utils.database import get_assistant
    from VishalMusic.core.mongo import mongodb


"""VISHAL MUSIC — VC Logger: announces (auto-deleting) when users join/leave the group voice chat."""

LOGGER = getLogger(__name__)

vc_active_users: Dict[int, Set[int]] = {}
active_vc_chats: Set[int] = set()
vc_logging_status: Dict[int, bool] = {}

vcloggerdb = mongodb.vclogger

prefixes = [".", "!", "/", "@", "?", "'"]

async def load_vc_logger_status():
    try:
        cursor = vcloggerdb.find({})
        enabled_chats = []
        async for doc in cursor:
            chat_id = doc["chat_id"]
            status = doc["status"]
            vc_logging_status[chat_id] = status
            if status:
                enabled_chats.append(chat_id)
        
        for chat_id in enabled_chats:
            asyncio.create_task(check_and_monitor_vc(chat_id))
        
        LOGGER.info(f"ʟᴏᴀᴅᴇᴅ ᴠᴄ ʟᴏɢɢᴇʀ sᴛᴀᴛᴜs ғᴏʀ {len(vc_logging_status)} ᴄʜᴀᴛs ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ")
        LOGGER.info(f"sᴛᴀʀᴛᴇᴅ ᴍᴏɴɪᴛᴏʀɪɴɢ ғᴏʀ {len(enabled_chats)} ᴇɴᴀʙʟᴇᴅ ᴄʜᴀᴛs")
    except Exception as e:
        LOGGER.error(f"Error loading VC logger status: {e}")

async def save_vc_logger_status(chat_id: int, status: bool):
    try:
        await vcloggerdb.update_one(
            {"chat_id": chat_id},
            {"$set": {"chat_id": chat_id, "status": status}},
            upsert=True
        )
        LOGGER.info(f"Saved VC logger status for chat {chat_id}: {status}")
    except Exception as e:
        LOGGER.error(f"Error saving VC logger status: {e}")

async def get_vc_logger_status(chat_id: int) -> bool:
    if chat_id in vc_logging_status:
        return vc_logging_status[chat_id]
    
    try:
        doc = await vcloggerdb.find_one({"chat_id": chat_id})
        if doc:
            status = doc["status"]
            vc_logging_status[chat_id] = status
            return status
    except Exception as e:
        LOGGER.error(f"Error getting VC logger status: {e}")
    
    return False

def generate_vclogger_filters():
    return filters.command("vclogger", prefixes=prefixes) & filters.group

@app.on_message(generate_vclogger_filters())
async def vclogger_command(_, message: Message):
    chat_id = message.chat.id
    args = message.text.split()
    status = await get_vc_logger_status(chat_id)

    prefix_ui = ", ".join([f"<b>{p}vclogger</b>" for p in prefixes])
    current_state_ui = to_small_caps(str(status if status is not None else "Not Set"))

    if len(args) == 1:
        text = (
            f"📌 <b>Current VC Logging State:</b> <b>{current_state_ui}</b>\n"
            f"Use {prefix_ui} <b>[on/enable/yes | off/disable/no]</b>"
        )
        await message.reply(text, disable_web_page_preview=True)
    elif len(args) == 2:
        arg = args[1].lower()
        if arg in ["on", "enable", "yes"]:
            vc_logging_status[chat_id] = True
            await save_vc_logger_status(chat_id, True)
            await message.reply(
                f"✅ <b>VC logging ENABLED</b> (Current State: <b>{to_small_caps(str(vc_logging_status[chat_id]))}</b>)",
                disable_web_page_preview=True
            )
            asyncio.create_task(check_and_monitor_vc(chat_id))
        elif arg in ["off", "disable", "no"]:
            vc_logging_status[chat_id] = False
            await save_vc_logger_status(chat_id, False)
            await message.reply(
                f"🚫 <b>VC logging DISABLED</b> (Current State: <b>{to_small_caps(str(vc_logging_status[chat_id]))}</b>)",
                disable_web_page_preview=True
            )
            active_vc_chats.discard(chat_id)
            vc_active_users.pop(chat_id, None)
        else:
            await message.reply(
                f"❌ Invalid argument! Use <b>[on/enable/yes | off/disable/no]</b>",
                disable_web_page_preview=True
            )

async def get_group_call_participants(userbot, peer):
    try:
        full_chat = await userbot.invoke(functions.channels.GetFullChannel(channel=peer))
        if not hasattr(full_chat.full_chat, 'call') or not full_chat.full_chat.call:
            return []
        call = full_chat.full_chat.call
        participants = await userbot.invoke(functions.phone.GetGroupParticipants(
            call=call, ids=[], sources=[], offset="", limit=100
        ))
        return participants.participants
    except Exception as e:
        error_msg = str(e).upper()
        if "420" in error_msg:
            wait_time = int(error_msg.split("FLOOD_WAIT_")[1].split("]")[0])
            LOGGER.warning(f"Flood wait detected, sleeping for {wait_time} seconds")
            await asyncio.sleep(wait_time + 1)
            return await get_group_call_participants(userbot, peer)
        if any(x in error_msg for x in ["GROUPCALL_NOT_FOUND", "CALL_NOT_FOUND", "NO_GROUPCALL"]):
            return []
        LOGGER.error(f"Error fetching participants: {e}")
        return []

async def monitor_vc_chat(chat_id):
    userbot = await get_assistant(chat_id)
    if not userbot:
        return

    cached_peer = None
    peer_fail_streak = 0
    while chat_id in active_vc_chats and await get_vc_logger_status(chat_id):
        try:
            if not cached_peer:
                cached_peer = await userbot.resolve_peer(chat_id)
            participants_list = await get_group_call_participants(userbot, cached_peer)
            new_users = set()
            for p in participants_list:
                if hasattr(p, 'peer') and hasattr(p.peer, 'user_id'):
                    new_users.add(p.peer.user_id)

            current_users = vc_active_users.get(chat_id, set())
            joined = new_users - current_users
            left = current_users - new_users

            if joined or left:
                tasks = []
                for user_id in joined:
                    tasks.append(handle_user_join(chat_id, user_id, userbot))
                for user_id in left:
                    tasks.append(handle_user_leave(chat_id, user_id, userbot))
                if tasks:
                    await asyncio.gather(*tasks, return_exceptions=True)

            vc_active_users[chat_id] = new_users
            peer_fail_streak = 0

        except Exception as e:
            cached_peer = None
            err = str(e).upper()
            # Transient on a fresh session: peer gets cached once the assistant
            # sees the chat. Only give up after several consecutive failures.
            if "PEER_ID_INVALID" in err or "PEER ID INVALID" in err or "ID NOT FOUND" in err:
                peer_fail_streak += 1
                if peer_fail_streak >= 5:
                    LOGGER.warning(
                        f"VC logger auto-disabled for chat {chat_id}: "
                        f"peer never resolvable by assistant ({e})"
                    )
                    active_vc_chats.discard(chat_id)
                    vc_active_users.pop(chat_id, None)
                    try:
                        await save_vc_logger_status(chat_id, False)
                    except Exception:
                        pass
                    return
            else:
                LOGGER.error(f"Error monitoring VC for chat {chat_id}: {e}")

        await asyncio.sleep(8)

async def check_and_monitor_vc(chat_id):
    if not await get_vc_logger_status(chat_id):
        return
    userbot = await get_assistant(chat_id)
    if not userbot:
        return
    try:
        if chat_id not in active_vc_chats:
            active_vc_chats.add(chat_id)
            asyncio.create_task(monitor_vc_chat(chat_id))
    except Exception as e:
        LOGGER.error(f"Error in check_and_monitor_vc: {e}")

async def handle_user_join(chat_id, user_id, userbot):
    try:
        user = await userbot.get_users(user_id)
        name = user.first_name or "Someone"
        mention = f'<a href="tg://user?id={user_id}"><b>{name}</b></a>'
        messages = [
            f"🌸 <b>ᴀʟᴇ ᴍᴇʟᴀ ʙᴀʙᴜ</b> {mention} <b>ᴀᴀ ɢᴀʏᴀ! ᴋᴀʙ sᴇ ᴛᴇʀᴀ ʜɪ ᴡᴀɪᴛ ᴋᴀʀ ʀᴀʜɪ ᴛʜɪ 🙈❤️</b>",
            f"✨ <b>ʟᴏ ᴊɪ,</b> {mention} <b>ɴᴇ ᴠᴄ ᴍᴇɪɴ ᴇɴᴛʀʏ ᴍᴀᴀʀ ʟɪ... ᴀʙ ʀᴏɴᴀ-ᴅʜᴏɴᴀ ʙᴀɴᴅ ᴋᴀʀᴏ ᴀᴜʀ ɢᴀᴀɴᴀ sᴜɴᴏ! 😜🎧</b>",
            f"🍓 <b>ʜᴀᴀʏᴇ</b> {mention} <b>ᴊᴀᴀɴ! ᴛᴜᴍʜᴀʀᴇ ʙɪɴᴀ ᴠᴄ ʙᴏʀɪɴɢ ʟᴀɢ ʀᴀʜɪ ᴛʜɪ, ᴀʙ ʀᴏɴᴀǫ ᴀᴀʏɪ ʜᴀɪ 🥰💖</b>",
            f"👀 <b>ᴅᴇᴋʜᴏ ᴅᴇᴋʜᴏ ᴋᴀᴜɴ ᴀᴀʏᴀ...</b> {mention} <b>ᴋɪ ᴛᴏʜ ᴍᴀɪɴ ᴅᴇᴇᴡᴀɴɪ ʜᴏᴏɴ ʏᴀᴀʀ! 🙈💋</b>",
            f"🧸 <b>ʙᴀʙᴜ</b> {mention}<b>, ᴍɪᴄ ᴏɴ ᴋᴀʀᴏ ɴᴀ... ᴛᴜᴍʜᴀʀɪ ᴀᴀᴡᴀᴢ sᴜɴɴᴇ ᴋᴏ ᴛᴀʀᴀs ɢᴀʏɪ ᴛʜɪ! 🥺👉👈</b>",
            f"💃 <b>ᴏʏᴇ ʜᴏʏᴇ!</b> {mention} <b>ᴀᴀ ɢᴀʏᴇ, ᴀʙ ᴛᴏʜ ᴠᴄ ᴍᴇɪɴ ᴘᴀʀᴛʏ ʜᴏɢɪ! ᴄʜᴀɪ-ᴘᴀᴋᴏᴅᴇ ʟᴀᴀᴏ ᴋᴏɪ ☕🍰</b>",
            f"💌 <b>ᴀʟᴇ ᴍᴇʀᴇ ᴊᴀᴀɴᴜ</b> {mention}<b>, ɪᴛɴɪ ᴅᴇʀ ᴋᴀʜᴀɴ ᴛʜᴇ? ᴋᴀʙ sᴇ ᴛᴜᴍʜᴀʀᴀ ᴡᴀɪᴛ ᴋᴀʀ ʀᴀʜɪ ᴛʜɪ! 💕✨</b>",
            f"🔥 {mention} <b>ɴᴇ ᴠᴄ ᴊᴏɪɴ ᴋɪʏᴀ ʜᴀɪ, ᴋᴏɪ ɪɴᴋɪ ɴᴀᴢᴀʀ ᴜᴛᴀᴀʀᴏ ᴊᴀʟᴅɪ! 🧿🤭</b>",
            f"💋 <b>sᴜɴᴏ</b> {mention}<b>... ᴛᴜᴍ ᴠᴄ ᴍᴇɪɴ ᴀᴀᴛᴇ ʜᴏ ᴛᴏʜ ᴍᴇʀᴀ ᴅɪʟ ᴅʜᴀᴋ-ᴅʜᴀᴋ ᴋᴀʀɴᴇ ʟᴀɢᴛᴀ ʜᴀɪ! 💓🫣</b>",
            f"🎵 <b>ᴀʙ ᴀᴀ ʜɪ ɢᴀʏᴇ ʜᴏ</b> {mention} <b>ᴛᴏʜ ᴇᴋ ᴘʏᴀᴀʀᴀ sᴀ ɢᴀᴀɴᴀ ʙʜɪ ᴘʟᴀʏ ᴋᴀʀ ᴅᴏ ɴᴀ! 🎶😚</b>",
        ]
        msg = random.choice(messages)
        sent_msg = await app.send_message(chat_id, msg)
        asyncio.create_task(delete_after_delay(sent_msg, 10))
    except Exception as e:
        LOGGER.error(f"Error sending join message for {user_id}: {e}")

async def handle_user_leave(chat_id, user_id, userbot):
    try:
        user = await userbot.get_users(user_id)
        name = user.first_name or "Someone"
        mention = f'<a href="tg://user?id={user_id}"><b>{name}</b></a>'
        messages = [
            f"🥺 <b>ʜᴀᴀʏᴇ</b> {mention} <b>ʙᴀʙᴜ! ᴍᴜᴊʜᴇ ᴀᴋᴇʟᴀ ᴄʜʜᴏᴅ ᴋᴇ ᴋᴀʜᴀɴ ᴄʜᴀʟᴇ ɢᴀʏᴇ? 💔😭</b>",
            f"😒 <b>ᴊᴀᴀᴏ ᴊᴀᴀᴏ</b> {mention}<b>, ᴋɪsɪ ᴀᴜʀ ᴋᴏ ᴘᴀᴛᴀɴᴇ ᴊᴀ ʀᴀʜᴇ ʜᴏ ɴᴀ? ᴍᴀɪɴ ʙᴀᴀᴛ ɴᴀʜɪ ᴋᴀʀᴜɴɢɪ ᴀʙ! 😤🔪</b>",
            f"💔 <b>ᴛᴜ ᴊᴀᴀ ʀᴀʜᴀ ʜᴀɪ</b> {mention}<b>? ʀᴜᴋ ᴛᴜᴊʜᴇ ᴛᴏʜ ᴍᴀɪɴ ᴘᴍ ᴍᴇɪɴ ʙᴀᴛᴀᴛɪ ʜᴏᴏɴ! 👡😡</b>",
            f"🚪 {mention} <b>ɴᴇ ᴠᴄ ᴄʜʜᴏᴅ ᴅɪ... ʟᴀɢᴛᴀ ʜᴀɪ ᴍᴜᴍᴍʏ ɴᴇ ʙᴀʟᴛɪ ᴘᴀᴀɴɪ ᴍᴀᴀɴɢ ʟɪʏᴀ! 🏃‍♂️💨</b>",
            f"😭 <b>ᴀʟᴇ ᴊᴀᴀɴ</b> {mention}<b>, ɪᴛɴɪ ᴊᴀʟᴅɪ ʙʜɪ ᴋʏᴀ ᴛʜɪ? ᴛʜᴏᴅᴀ ᴀᴜʀ ʀᴜᴋ ᴊᴀᴀᴛᴇ ɴᴀ! 🥺❤️</b>",
            f"🥲 <b>ʟᴏ</b> {mention} <b>ʙʜɪ ɢᴀʏᴀ... ᴀʙ ᴠᴄ ᴍᴇɪɴ sᴀɴɴᴀᴛᴀ ʜᴏ ɢᴀʏᴀ! ᴡᴀᴀᴘᴀs ᴀᴀ ᴊᴀᴀᴏ ɴᴀ ʙᴀʙʏ! 🥀</b>",
            f"🏃‍♀️ {mention} <b>ᴛᴏʜ ᴀɪsᴇ ʙʜᴀᴀɢᴀ ᴊᴀɪsᴇ ᴘɪᴄʜʜᴇ ɢғ ᴋᴀ ʙʜᴀɪ ʟᴀɢ ɢᴀʏᴀ ʜᴏ! 😂💀</b>",
            f"💔 {mention} <b>ᴄʜᴀʟᴇ ɢᴀʏᴇ... ᴍᴇʀᴀ ᴅɪʟ ᴛᴏᴏᴛ ɢᴀʏᴀ! ᴋᴏɪ ᴍᴇʀᴇ ʟɪʏᴇ ʙᴀɴᴅ-ᴀɪᴅ ʟᴀᴀᴏ 🩹🥺</b>",
            f"🤫 {mention} <b>ɴɪᴋᴀʟ ʟɪʏᴇ... ʟᴀɢᴛᴀ ʜᴀɪ ᴋɪsɪ ᴀᴜʀ ᴋᴇ ᴘᴍ ᴍᴇɪɴ ʟɪɴᴇ ᴍᴀᴀʀɴᴇ ɢᴀʏᴇ ʜᴀɪɴ! 🧐💅</b>",
            f"🥀 <b>ᴊᴀᴀᴛᴇ ᴊᴀᴀᴛᴇ ʙʜɪ</b> {mention} <b>ᴍᴇʀɪ ᴊᴀᴀɴ ʟᴇ ɢᴀʏᴇ... ᴊᴀʟᴅɪ ᴡᴀᴀᴘᴀs ᴀᴀɴᴀ ʜᴀᴀɴ! 💖😘</b>",
        ]
        msg = random.choice(messages)
        sent_msg = await app.send_message(chat_id, msg)
        asyncio.create_task(delete_after_delay(sent_msg, 10))
    except Exception as e:
        LOGGER.error(f"Error sending leave message for {user_id}: {e}")

async def delete_after_delay(message, delay):
    try:
        await asyncio.sleep(delay)
        await message.delete()
    except:
        pass

def to_small_caps(text):
    mapping = {
        "a":"ᴀ","b":"ʙ","c":"ᴄ","d":"ᴅ","e":"ᴇ","f":"ꜰ","g":"ɢ","h":"ʜ","i":"ɪ","j":"ᴊ",
        "k":"ᴋ","l":"ʟ","m":"ᴍ","n":"ɴ","o":"ᴏ","p":"ᴘ","q":"ǫ","r":"ʀ","s":"s","t":"ᴛ",
        "u":"ᴜ","v":"ᴠ","w":"ᴡ","x":"x","y":"ʏ","z":"ᴢ",
        "A":"ᴀ","B":"ʙ","C":"ᴄ","D":"ᴅ","E":"ᴇ","F":"ꜰ","G":"ɢ","H":"ʜ","I":"ɪ","J":"ᴊ",
        "K":"ᴋ","L":"ʟ","M":"ᴍ","N":"ɴ","O":"ᴏ","P":"ᴘ","Q":"ǫ","R":"ʀ","S":"s","T":"ᴛ",
        "U":"ᴜ","V":"ᴠ","W":"ᴡ","X":"x","Y":"ʏ","Z":"ᴢ"
    }
    return "".join(mapping.get(c,c) for c in text)

async def initialize_vc_logger():
    await load_vc_logger_status()

start_vc_logger = initialize_vc_logger

# ═══════════════════════════════════════════════════════════
#         🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
