from pyrogram import filters
from pyrogram.types import Message

from VISHALMUSIC import YouTube, app
from VISHALMUSIC.core.call import VISHAL
from VISHALMUSIC.misc import db
from VISHALMUSIC.utils import AdminRightsCheck, seconds_to_min
from VISHALMUSIC.utils.colored_buttons import send_message_colored, edit_message_text_colored
from VISHALMUSIC.utils.inline import close_markup
from config import BANNED_USERS


@app.on_message(
    filters.command(["seek", "cseek", "seekback", "cseekback"])
    & filters.group
    & ~BANNED_USERS
)
@AdminRightsCheck
async def seek_comm(cli, message: Message, _, chat_id):
    if len(message.command) == 1:
        return await message.reply_text(_["admin_20"])
    query = message.text.split(None, 1)[1].strip()
    if not query.isnumeric():
        return await message.reply_text(_["admin_21"])
    playing = db.get(chat_id)
    if not playing:
        return await message.reply_text(_["queue_2"])
    duration_seconds = int(playing[0]["seconds"])
    if duration_seconds == 0:
        return await message.reply_text(_["admin_22"])
    file_path = playing[0]["file"]
    duration_played = int(playing[0]["played"])
    duration_to_skip = int(query)
    duration = playing[0]["dur"]
    if message.command[0][-2] == "c":
        if (duration_played - duration_to_skip) <= 10:
            return await send_message_colored(
                chat_id=message.chat.id,
                text=_["admin_23"].format(seconds_to_min(duration_played), duration),
                reply_markup=close_markup(_),
            )
        to_seek = duration_played - duration_to_skip + 1
    else:
        if (duration_seconds - (duration_played + duration_to_skip)) <= 10:
            return await send_message_colored(
                chat_id=message.chat.id,
                text=_["admin_23"].format(seconds_to_min(duration_played), duration),
                reply_markup=close_markup(_),
            )
        to_seek = duration_played + duration_to_skip + 1
    mystic = await message.reply_text(_["admin_24"])
    if "vid_" in file_path:
        n, file_path = await YouTube.video(playing[0]["vidid"], True)
        if n == 0:
            return await message.reply_text(_["admin_22"])
    check = (playing[0]).get("speed_path")
    if check:
        file_path = check
    if "index_" in file_path:
        file_path = playing[0]["vidid"]
    try:
        await VISHAL.seek_stream(
            chat_id,
            file_path,
            seconds_to_min(to_seek),
            duration,
            playing[0]["streamtype"],
        )
    except:
        return await edit_message_text_colored(chat_id=mystic.chat.id, message_id=mystic.id, text=_["admin_26"], reply_markup=close_markup(_))
    if message.command[0][-2] == "c":
        db[chat_id][0]["played"] -= duration_to_skip
    else:
        db[chat_id][0]["played"] += duration_to_skip
    await edit_message_text_colored(
        chat_id=mystic.chat.id, message_id=mystic.id,
        text=_["admin_25"].format(seconds_to_min(to_seek), message.from_user.mention),
        reply_markup=close_markup(_),
    )
