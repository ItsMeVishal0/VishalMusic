from datetime import datetime
from pyrogram import filters
from pyrogram.types import (
    CallbackQuery,
    Message,
)
from config import OWNER_ID
from VISHALMUSIC import app
from VISHALMUSIC.utils.colored_buttons import styled_button, buttons_to_inline_markup


def extract_bug_content(msg: Message) -> str | None:
    return msg.text.split(None, 1)[1] if msg.text and " " in msg.text else None


def escape_md(text: str) -> str:
    return text.replace('[', '\\[').replace(']', '\\]').replace('`', '\\`')


@app.on_message(filters.command("bug"))
async def report_bug(_, msg: Message):
    if msg.chat.type == "private":
        return await msg.reply_text("**ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ɪs ᴏɴʟʏ ғᴏʀ ɢʀᴏᴜᴘs.**")

    bug_description = extract_bug_content(msg)
    if not bug_description:
        return await msg.reply_text("**ɴᴏ ʙᴜɢ ᴅᴇsᴄʀɪᴘᴛɪᴏɴ ᴘʀᴏᴠɪᴅᴇᴅ. ᴘʟᴇᴀsᴇ sᴘᴇᴄɪғʏ ᴛʜᴇ ʙᴜɢ.**")

    user_id = msg.from_user.id
    user_name = escape_md(msg.from_user.first_name)
    mention = f"[{user_name}](tg://user?id={user_id})"

    chat_reference = (
        f"@{msg.chat.username}/`{msg.chat.id}`"
        if msg.chat.username
        else f"ᴘʀɪᴠᴀᴛᴇ ɢʀᴏᴜᴘ/`{msg.chat.id}`"
    )

    current_date = datetime.utcnow().strftime("%d-%m-%Y")

    bug_report = (
        f"**#ʙᴜɢ ʀᴇᴘᴏʀᴛ**\n"
        f"**ʀᴇᴘᴏʀᴛᴇᴅ ʙʏ:** {mention}\n"
        f"**ᴜsᴇʀ ɪᴅ:** `{user_id}`\n"
        f"**ᴄʜᴀᴛ:** {chat_reference}\n"
        f"**ʙᴜɢ ᴅᴇsᴄʀɪᴘᴛɪᴏɴ:** `{escape_md(bug_description)}`\n"
        f"**ᴅᴀᴛᴇ:** `{current_date}`"
    )

    if user_id == OWNER_ID:
        return await msg.reply_text(
            "**ʏᴏᴜ ᴀʀᴇ ᴛʜᴇ ᴏᴡɴᴇʀ ᴏғ ᴛʜᴇ ʙᴏᴛ. ᴘʟᴇᴀsᴇ ᴀᴅᴅʀᴇss ᴛʜᴇ ʙᴜɢ ᴅɪʀᴇᴄᴛʟʏ.**"
        )

    await send_message_colored(
        chat_id=msg.chat.id,
        text="**ʙᴜɢ ʀᴇᴘᴏʀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!**",
        reply_markup=[[styled_button("ᴄʟᴏsᴇ", callback_data="close_data", style="danger")]],
    )

    # Send report to log group
    buttons = [[styled_button("ᴄʟᴏsᴇ", callback_data="close_send_photo", style="danger")]]
    if msg.chat.username:
        link = f"https://t.me/{msg.chat.username}/{msg.id}"
        buttons.insert(0, [styled_button("ᴠɪᴇᴡ ʙᴜɢ", url=link)])

    await send_message_colored(
        chat_id=-1002077986660,
        text=bug_report,
        reply_markup=buttons,
        parse_mode="Markdown",
        disable_web_page_preview=True,
    )


@app.on_callback_query(filters.regex("close_send_photo"))
async def close_bug_report(_, query: CallbackQuery):
    try:
        member = await app.get_chat_member(query.message.chat.id, query.from_user.id)
        if not member.privileges or not member.privileges.can_delete_messages:
            return await query.answer("ʏᴏᴜ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴘᴇʀᴍɪssɪᴏɴ ᴛᴏ ᴅᴇʟᴇᴛᴇ ᴛʜɪs.", show_alert=True)
    except:
        return await query.answer("ᴄᴏᴜʟᴅ ɴᴏᴛ ᴠᴇʀɪғʏ ᴀᴄᴄᴇss.", show_alert=True)

    await query.message.delete()
