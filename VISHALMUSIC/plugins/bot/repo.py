from pyrogram import filters
from VISHALMUSIC import app
from VISHALMUSIC.utils.colored_buttons import (
    styled_button, 
    buttons_to_inline_markup,
    send_photo_colored
)
from config import BOT_USERNAME

repo_caption = """**
🚀 ᴄʟᴏɴᴇ ᴀɴᴅ ᴅᴇᴘʟᴏʏ – 🚀

➤ ᴅᴇᴘʟᴏʏ ᴇᴀsɪʟʏ ᴏɴ ʜᴇʀᴏᴋᴜ ᴡɪᴛʜᴏᴜᴛ ᴇʀʀᴏʀꜱ  
➤ ɴᴏ ʜᴇʀᴏᴋᴜ ʙᴀɴ ɪꜱꜱᴜᴇ  
➤ ɴᴏ ɪᴅ ʙᴀɴ ɪꜱꜱᴜᴇ   
➤ ᴜɴʟɪᴍɪᴛᴇᴅ ᴅʏɴᴏꜱ  
➤ ʀᴜɴ 24/7 ʟᴀɢ ꜰʀᴇᴇ

ɪꜰ ʏᴏᴜ ꜰᴀᴄᴇ ᴀɴʏ ᴘʀᴏʙʟᴇᴍ, ꜱᴇɴᴅ ꜱꜱ ɪɴ ꜱᴜᴘᴘᴏʀᴛ
**"""

@app.on_message(filters.command("repo"))
async def show_repo(_, msg):
    buttons = [
        [styled_button("➕ ᴀᴅᴅ ᴍᴇ ʙᴀʙʏ ✨", url=f"https://t.me/{BOT_USERNAME}?startgroup=true", style="success")],
        [
            styled_button("👑 ᴏᴡɴᴇʀ", url="https://t.me/Its_me_Vishall", style="primary"),
            styled_button("💬 ꜱᴜᴘᴘᴏʀᴛ", url="https://t.me/Its_me_Vishall", style="primary"),
        ],
        [
            styled_button("🛠️ ꜱᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ", url="https://t.me/Its_me_Vishall", style="primary"),
            styled_button("🎵 ɢɪᴛʜᴜʙ", url="https://github.com/ItsMeVishal0/VishalMusic", style="primary"),
        ],
    ]

    try:
        await send_photo_colored(
            chat_id=msg.chat.id,
            photo="https://files.catbox.moe/a6sz5r.jpg",
            caption=repo_caption,
            reply_markup=buttons,
        )
    except:
        pass
