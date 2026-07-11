from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.errors import RPCError
from VISHALMUSIC import app


@app.on_message(filters.command(["info", "userinfo", "whois"]))
async def info_cmd(client, message):
    if message.reply_to_message:
        user = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            user = await client.get_users(message.command[1])
        except RPCError:
            return await message.reply_text("User not found.")
    else:
        user = message.from_user

    pp = user.photo.big_file_id if user.photo else None
    uname = f"@{user.username}" if user.username else "None"
    txt = (
        f"**User Info:**\n"
        f" ID: `{user.id}`\n"
        f" Name: {user.mention}\n"
        f" Username: {uname}\n"
        f" DC: {user.dc_id if hasattr(user, 'dc_id') else 'N/A'}"
    )
    if pp:
        await message.reply_photo(pp, caption=txt)
    else:
        await message.reply_text(txt)
