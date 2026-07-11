import random
from pyrogram import Client, filters, enums
from VISHALMUSIC import app
from VISHALMUSIC.utils.colored_buttons import styled_button, edit_message_text_colored
from config import BOT_USERNAME


@app.on_message(filters.command(["genpassword", "genpw"]))
async def password(bot, message):
    processing = await message.reply_text("Pʀᴏᴄᴇꜱꜱɪɴɢ...")

    characters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890!@#$%^&*()_+"
    
    if len(message.command) > 1:
        input_length = message.text.split(" ", 1)[1]
    else:
        input_length = random.choice(["5", "6", "7", "8", "9", "10", "12", "14"])

    try:
        length = int(input_length)
        if length < 1:
            raise ValueError("Length must be positive.")
    except ValueError:
        return await processing.edit_text("Please enter a valid positive number for the password length.")

    generated_password = "".join(random.choices(characters, k=length))

    reply_text = (
        f"<b>Lɪᴍɪᴛ:</b> {length}\n"
        f"<b>Pᴀꜱꜱᴡᴏʀᴅ:</b> <code>{generated_password}</code>"
    )

    buttons = [[styled_button("𝗔𝗗𝗗 𝗠𝗘", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")]]

    await edit_message_text_colored(
        chat_id=processing.chat.id,
        message_id=processing.id,
        text=reply_text,
        reply_markup=buttons,
    )
