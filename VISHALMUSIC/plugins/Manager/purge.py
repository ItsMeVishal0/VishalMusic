import asyncio
from pyrogram import Client, filters
from pyrogram.enums import ChatType
from pyrogram.errors import MessageDeleteForbidden, RPCError, FloodWait
from pyrogram.types import Message

from VISHALMUSIC import app
from VISHALMUSIC.utils.admin_filters import admin_filter


def divide_chunks(l: list, n: int = 100):
    for i in range(0, len(l), n):
        yield l[i: i + n]


@app.on_message(filters.command("purge") & admin_filter)
async def purge(app: Client, msg: Message):
    if msg.chat.type != ChatType.SUPERGROUP:
        return await msg.reply("**ɪ ᴄᴀɴ'ᴛ ᴘᴜʀɢᴇ ᴍᴇssᴀɢᴇs ɪɴ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ. ᴘʟᴇᴀsᴇ ᴄᴏɴᴠᴇʀᴛ ɪᴛ ᴛᴏ ᴀ sᴜᴘᴇʀɢʀᴏᴜᴘ.**")

    if not msg.reply_to_message:
        return await msg.reply("**ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ sᴛᴀʀᴛ ᴘᴜʀɢᴇ!**")

    message_ids = list(range(msg.reply_to_message.id, msg.id))
    m_list = list(divide_chunks(message_ids))

    try:
        for plist in m_list:
            try:
                await app.delete_messages(chat_id=msg.chat.id, message_ids=plist, revoke=True)
                await asyncio.sleep(0.5)
            except FloodWait as e:
                await asyncio.sleep(e.value)
        await msg.delete()
    except MessageDeleteForbidden:
        await msg.reply("**ɪ ᴄᴀɴ'ᴛ ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs ɪɴ ᴛʜɪs ᴄʜᴀᴛ.**")
    except RPCError as e:
        await msg.reply(f"**ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ:**\n<code>{e}</code>")


@app.on_message(filters.command("del") & admin_filter)
async def delete_msg(app: Client, msg: Message):
    if not msg.reply_to_message:
        return await msg.reply("**ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ᴅᴇʟᴇᴛᴇ ɪᴛ.**")
    try:
        await msg.reply_to_message.delete()
        await msg.delete()
    except Exception as e:
        await msg.reply(f"**ᴇʀʀᴏʀ:** `{e}`")


@app.on_message(filters.command("spurge") & admin_filter)
async def spurge(app: Client, msg: Message):
    if msg.chat.type != ChatType.SUPERGROUP:
        return await msg.reply("**ɪ ᴄᴀɴ'ᴛ ᴘᴜʀɢᴇ ᴍᴇssᴀɢᴇs ɪɴ ᴀ ʙᴀsɪᴄ ɢʀᴏᴜᴘ. ᴘʟᴇᴀsᴇ ᴄᴏɴᴠᴇʀᴛ ɪᴛ ᴛᴏ ᴀ sᴜᴘᴇʀɢʀᴏᴜᴘ.**")

    if not msg.reply_to_message:
        return await msg.reply("**ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ sᴛᴀʀᴛ ᴘᴜʀɢᴇ!**")

    message_ids = list(range(msg.reply_to_message.id, msg.id))
    m_list = list(divide_chunks(message_ids))

    try:
        for plist in m_list:
            try:
                await app.delete_messages(chat_id=msg.chat.id, message_ids=plist, revoke=True)
                await asyncio.sleep(0.5)
            except FloodWait as e:
                await asyncio.sleep(e.value)
        await msg.delete()
    except MessageDeleteForbidden:
        await msg.reply("**ɪ ᴄᴀɴ'ᴛ ᴅᴇʟᴇᴛᴇ ᴍᴇssᴀɢᴇs ɪɴ ᴛʜɪs ᴄʜᴀᴛ.**")
    except RPCError as e:
        await msg.reply(f"**ᴇʀʀᴏʀ ᴏᴄᴄᴜʀʀᴇᴅ:**\n<code>{e}</code>")
