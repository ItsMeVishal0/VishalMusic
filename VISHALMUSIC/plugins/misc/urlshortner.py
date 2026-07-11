from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction, ParseMode
from VISHALMUSIC import app
from VISHALMUSIC.utils.colored_buttons import styled_button, send_message_colored
import pyshorteners
import httpx


shortener = pyshorteners.Shortener()


@app.on_message(filters.command("short"))
async def short_urls(bot: Client, message: Message):
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    if len(message.command) < 2:
        return await message.reply_text(
            "❌ Please provide a link to shorten.\n\n**Example:** `/short https://example.com`",
            parse_mode=ParseMode.MARKDOWN
        )

    link = message.command[1]

    try:
        tiny = shortener.tinyurl.short(link)
        dagd = shortener.dagd.short(link)
        clck = shortener.clckru.short(link)

        buttons = [
            [styled_button("🔗 TinyURL", url=tiny)],
            [styled_button("🔗 Dagd", url=dagd), styled_button("🔗 Clck.ru", url=clck)],
        ]

        await send_message_colored(chat_id=message.chat.id, text="🔍 Here are your shortened URLs:", reply_markup=buttons)

    except Exception as e:
        print(f"Shortener error: {e}")
        await message.reply_text("❌ Failed to shorten the link. It might already be shortened or invalid.")


@app.on_message(filters.command("unshort"))
async def unshort_url(bot: Client, message: Message):
    await bot.send_chat_action(message.chat.id, ChatAction.TYPING)

    if len(message.command) < 2:
        return await message.reply_text(
            "❌ Please provide a shortened link.\n\n**Example:** `/unshort https://bit.ly/example`",
            parse_mode=ParseMode.MARKDOWN
        )

    short_link = message.command[1]

    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
            response = await client.get(short_link)
            final_url = str(response.url)

        buttons = [[styled_button("🔗 View Final URL", url=final_url)]]
        await send_message_colored(chat_id=message.chat.id, text=f"✅ **Unshortened URL:**\n`{final_url}`", reply_markup=buttons)

    except Exception as e:
        print(f"Unshortener error: {e}")
        await message.reply_text("❌ Failed to unshorten the link. It may be broken or invalid.")
