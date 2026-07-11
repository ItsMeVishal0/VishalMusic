from pyrogram import filters
from VISHALMUSIC import app
from VISHALMUSIC.utils.admin_filters import admin_filter


@app.on_message(filters.command("id"))
async def id_cmd(_, message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user
        txt = f"{user.mention}'s ID: `{user.id}`\nChat ID: `{message.chat.id}`"
        if message.reply_to_message.forward_from_chat:
            txt += f"\nForwarded from: `{message.reply_to_message.forward_from_chat.id}`"
        await message.reply_text(txt)
    else:
        await message.reply_text(f"Your ID: `{message.from_user.id}`\nChat ID: `{message.chat.id}`")
