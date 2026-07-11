from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.errors import RPCError
from pyrogram.types import Message
from VISHALMUSIC import app
from VISHALMUSIC.utils.admin_filters import admin_filter


def is_group(message: Message) -> bool:
    return message.chat.type not in (ChatType.PRIVATE, ChatType.BOT)

async def has_permission(user_id: int, chat_id: int, permission: str) -> bool:
    try:
        member = await app.get_chat_member(chat_id, user_id)
        return bool(getattr(getattr(member, "privileges", None), permission, False) or getattr(member, "status", "") in ("creator",))
    except Exception:
        return False


@app.on_message(filters.command("pin") & admin_filter)
async def pin_message(_, message: Message):
    if not is_group(message):
        return await message.reply_text("**ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴡᴏʀᴋs ᴏɴʟʏ ɪɴ ɢʀᴏᴜᴘs!**")
    if not await has_permission(message.from_user.id, message.chat.id, "can_pin_messages"):
        return await message.reply_text("**ʏᴏᴜ ʟᴀᴄᴋ ᴘɪɴ ᴘᴇʀᴍɪssɪᴏɴ.**")
    if not message.reply_to_message:
        return await message.reply_text("**ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴘɪɴ ɪᴛ.**")
    try:
        await app.pin_chat_message(message.chat.id, message.reply_to_message.id)
        await message.reply_text("**ᴘɪɴɴᴇᴅ! ✅**")
    except RPCError as e:
        await message.reply_text(f"**ғᴀɪʟᴇᴅ:** `{e}`")


@app.on_message(filters.command("unpin") & admin_filter)
async def unpin_message(_, message: Message):
    if not is_group(message):
        return await message.reply_text("**ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴡᴏʀᴋs ᴏɴʟʏ ɪɴ ɢʀᴏᴜᴘs!**")
    if not await has_permission(message.from_user.id, message.chat.id, "can_pin_messages"):
        return await message.reply_text("**ʏᴏᴜ ʟᴀᴄᴋ ᴘɪɴ ᴘᴇʀᴍɪssɪᴏɴ.**")
    if not message.reply_to_message:
        return await message.reply_text("**ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴜɴᴘɪɴ ɪᴛ.**")
    try:
        await app.unpin_chat_message(message.chat.id, message.reply_to_message.id)
        await message.reply_text("**ᴜɴᴘɪɴɴᴇᴅ! ✅**")
    except RPCError as e:
        await message.reply_text(f"**ғᴀɪʟᴇᴅ:** `{e}`")


@app.on_message(filters.command("setphoto") & admin_filter)
async def set_group_photo(_, message: Message):
    if not is_group(message):
        return await message.reply_text("**ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴡᴏʀᴋs ᴏɴʟʏ ɪɴ ɢʀᴏᴜᴘs!**")
    if not await has_permission(message.from_user.id, message.chat.id, "can_change_info"):
        return await message.reply_text("**ʏᴏᴜ ʟᴀᴄᴋ ᴘᴇʀᴍɪssɪᴏɴ.**")
    if not message.reply_to_message or not message.reply_to_message.photo:
        return await message.reply_text("**ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴘʜᴏᴛᴏ ᴛᴏ sᴇᴛ ɪᴛ ᴀs ɢʀᴏᴜᴘ ᴘʜᴏᴛᴏ.**")
    try:
        await app.set_chat_photo(message.chat.id, message.reply_to_message.photo.file_id)
        await message.reply_text("**ɢʀᴏᴜᴘ ᴘʜᴏᴛᴏ ᴜᴘᴅᴀᴛᴇᴅ! ✅**")
    except RPCError as e:
        await message.reply_text(f"**ғᴀɪʟᴇᴅ:** `{e}`")


@app.on_message(filters.command("removephoto") & admin_filter)
async def remove_group_photo(_, message: Message):
    if not is_group(message):
        return await message.reply_text("**ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴡᴏʀᴋs ᴏɴʟʏ ɪɴ ɢʀᴏᴜᴘs!**")
    if not await has_permission(message.from_user.id, message.chat.id, "can_change_info"):
        return await message.reply_text("**ʏᴏᴜ ʟᴀᴄᴋ ᴘᴇʀᴍɪssɪᴏɴ.**")
    try:
        await app.delete_chat_photo(message.chat.id)
        await message.reply_text("**ɢʀᴏᴜᴘ ᴘʜᴏᴛᴏ ʀᴇᴍᴏᴠᴇᴅ! ✅**")
    except Exception as e:
        await message.reply_text(f"**ғᴀɪʟᴇᴅ:** `{e}`")


@app.on_message(filters.command("settitle") & admin_filter)
async def set_group_title(_, message: Message):
    if not is_group(message):
        return await message.reply_text("**ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴡᴏʀᴋs ᴏɴʟʏ ɪɴ ɢʀᴏᴜᴘs!**")
    if not await has_permission(message.from_user.id, message.chat.id, "can_change_info"):
        return await message.reply_text("**ʏᴏᴜ ʟᴀᴄᴋ ᴘᴇʀᴍɪssɪᴏɴ.**")
    if len(message.command) < 2:
        return await message.reply_text("**ᴜsᴀɢᴇ:** `/settitle ɴᴇᴡ ᴛɪᴛʟᴇ`")
    title = message.text.split(None, 1)[1]
    try:
        await app.set_chat_title(message.chat.id, title)
        await message.reply_text(f"**ᴛɪᴛʟᴇ ᴄʜᴀɴɢᴇᴅ ᴛᴏ:** {title}")
    except RPCError as e:
        await message.reply_text(f"**ғᴀɪʟᴇᴅ:** `{e}`")


@app.on_message(filters.command("setdiscription") & admin_filter)
async def set_group_description(_, message: Message):
    if not is_group(message):
        return await message.reply_text("**ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴡᴏʀᴋs ᴏɴʟʏ ɪɴ ɢʀᴏᴜᴘs!**")
    if not await has_permission(message.from_user.id, message.chat.id, "can_change_info"):
        return await message.reply_text("**ʏᴏᴜ ʟᴀᴄᴋ ᴘᴇʀᴍɪssɪᴏɴ.**")
    if len(message.command) < 2:
        return await message.reply_text("**ᴜsᴀɢᴇ:** `/setdiscription ᴛᴇxᴛ`")
    desc = message.text.split(None, 1)[1]
    try:
        await app.set_chat_description(message.chat.id, desc)
        await message.reply_text("**ᴅᴇsᴄʀɪᴘᴛɪᴏɴ ᴜᴘᴅᴀᴛᴇᴅ! ✅**")
    except RPCError as e:
        await message.reply_text(f"**ғᴀɪʟᴇᴅ:** `{e}`")
