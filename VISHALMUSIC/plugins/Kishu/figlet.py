import pyfiglet
from random import choice
from pyrogram import filters
from pyrogram.types import CallbackQuery
from VISHALMUSIC import app
from VISHALMUSIC.utils.colored_buttons import styled_button, send_message_colored, edit_message_text_colored

import base64

def figle(text: str):
    fonts = pyfiglet.FigletFont.getFonts()
    font = choice(fonts)
    figlet_text = pyfiglet.figlet_format(text, font=font)
    encoded_text = base64.b64encode(text.encode()).decode()
    buttons = [
        [
            styled_button(text="🌀 ᴄʜᴀɴɢᴇ", callback_data=f"figlet_{encoded_text}", style="primary"),
            styled_button(text="❌ ᴄʟᴏsᴇ", callback_data="close_reply", style="danger")
        ]
    ]
    return figlet_text, buttons

@app.on_message(filters.command("figlet"))
async def figlet_command(client, message):
    try:
        text = message.text.split(' ', 1)[1]
    except IndexError:
        return await message.reply_text("✏️ Example:\n`/figlet VISHAL`", quote=True)

    figlet_result, buttons = figle(text)
    await send_message_colored(
        chat_id=message.chat.id,
        text=f"✨ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ғɪɢʟᴇᴛ:\n<pre>{figlet_result}</pre>",
        reply_markup=buttons
    )

@app.on_callback_query(filters.regex(r"^figlet_"))
async def figlet_callback(_, query: CallbackQuery):
    try:
        encoded_text = query.data.split("_", 1)[1]
        text = base64.b64decode(encoded_text).decode()
        figlet_result, buttons = figle(text)
        await edit_message_text_colored(
            chat_id=query.message.chat.id,
            message_id=query.message.id,
            text=f"✨ ʜᴇʀᴇ ɪs ʏᴏᴜʀ ғɪɢʟᴇᴛ:\n<pre>{figlet_result}</pre>",
            reply_markup=buttons
        )
    except Exception as e:
        await query.answer("Error: Cannot update figlet", show_alert=True)

@app.on_callback_query(filters.regex("close_reply"))
async def close_reply(_, query: CallbackQuery):
    try:
        await query.message.delete()
    except:
        await query.answer("❌ Message already deleted.", show_alert=True)
