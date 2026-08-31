from pyrogram import filters
import random
import requests
from VISHALMUSIC import app
from VISHALMUSIC.utils.colored_buttons import (
    styled_button,
    smart_send_media,
)

SUPPORT_CHAT = "ItsMeVishalSupport"
SUPPORT_BTN = [[styled_button("ꜱᴜᴘᴘᴏʀᴛ", url=f"https://t.me/{SUPPORT_CHAT}", style="primary")]]

CUTE_VIDEO = "https://files.catbox.moe/qibmue.mp4"


@app.on_message(filters.command("wish"))
async def wish(_, m):
    if len(m.command) < 2:
        return await m.reply_text("❌ ᴀᴅᴅ ʏᴏᴜʀ ᴡɪꜱʜ ʙᴀʙʏ 🥀!")

    try:
        api = requests.get("https://nekos.best/api/v2/happy").json()
        url = api["results"][0]["url"]
    except Exception:
        return await m.reply_text("⚠️ Couldn't fetch animation, try again later.")

    text = m.text.split(None, 1)[1]
    wish_count = random.randint(1, 100)
    name = m.from_user.first_name or "User"

    caption = (
        f"✨ ʜᴇʏ {name}!\n"
        f"🪄 ʏᴏᴜʀ ᴡɪꜱʜ: {text}\n"
        f"📊 ᴘᴏꜱꜱɪʙɪʟɪᴛʏ: {wish_count}%"
    )

    await smart_send_media(
        chat_id=m.chat.id,
        method="sendAnimation",
        media_field="animation",
        media_value=url,
        caption=caption,
        reply_markup=SUPPORT_BTN,
    )


@app.on_message(filters.command("cute"))
async def cute(_, message):
    user = message.reply_to_message.from_user if message.reply_to_message else message.from_user
    mention = f"[{user.first_name}](tg://user?id={user.id})"
    percent = random.randint(1, 100)

    caption = f"🍑 {mention} ɪꜱ {percent}% ᴄᴜᴛᴇ ʙᴀʙʏ 🥀"

    await smart_send_media(
        chat_id=message.chat.id,
        method="sendDocument",
        media_field="document",
        media_value=CUTE_VIDEO,
        caption=caption,
        parse_mode="MARKDOWN",
        reply_markup=SUPPORT_BTN,
        reply_to_message_id=message.reply_to_message.message_id if message.reply_to_message else None,
    )
