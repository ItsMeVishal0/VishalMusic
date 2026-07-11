import asyncio
import os

from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import CallbackQuery, InputMediaPhoto, Message

import config
from VISHALMUSIC import app
from VISHALMUSIC.misc import db
from VISHALMUSIC.utils import VISHALBIN, get_channeplayCB, seconds_to_min
from VISHALMUSIC.utils.database import get_cmode, is_active_chat, is_music_playing
from VISHALMUSIC.utils.decorators.language import language, languageCB
from VISHALMUSIC.utils.colored_buttons import send_photo_colored, edit_message_text_colored, edit_message_media_colored, edit_reply_markup_colored, buttons_to_inline_markup
from VISHALMUSIC.utils.inline import queue_back_markup, queue_markup
from config import BANNED_USERS

basic = {}


def get_image(videoid):
    if os.path.isfile(f"cache/{videoid}.png"):
        return f"cache/{videoid}.png"
    else:
        return config.YOUTUBE_IMG_URL


def get_duration(playing):
    file_path = playing[0]["file"]
    if "index_" in file_path or "live_" in file_path:
        return "Unknown"
    duration_seconds = int(playing[0]["seconds"])
    if duration_seconds == 0:
        return "Unknown"
    else:
        return "Inline"


@app.on_message(
    filters.command(["queue", "cqueue", "player", "cplayer", "playing", "cplaying"])
    & filters.group
    & ~BANNED_USERS
)
@language
async def get_queue(client, message: Message, _):
    if message.command[0][0] == "c":
        chat_id = await get_cmode(message.chat.id)
        if chat_id is None:
            return await message.reply_text(_["setting_7"])
        try:
            await app.get_chat(chat_id)
        except:
            return await message.reply_text(_["cplay_4"])
        cplay = True
    else:
        chat_id = message.chat.id
        cplay = False
    if not await is_active_chat(chat_id):
        return await message.reply_text(_["general_5"])
    got = db.get(chat_id)
    if not got:
        return await message.reply_text(_["queue_2"])
    file = got[0]["file"]
    videoid = got[0]["vidid"]
    user = got[0]["by"]
    title = (got[0]["title"]).title()
    typo = (got[0]["streamtype"]).title()
    DUR = get_duration(got)
    if "live_" in file:
        IMAGE = get_image(videoid)
    elif "vid_" in file:
        IMAGE = get_image(videoid)
    elif "index_" in file:
        IMAGE = config.STREAM_IMG_URL
    else:
        if videoid == "telegram":
            IMAGE = (
                config.TELEGRAM_AUDIO_URL
                if typo == "Audio"
                else config.TELEGRAM_VIDEO_URL
            )
        elif videoid == "soundcloud":
            IMAGE = config.SOUNCLOUD_IMG_URL
        else:
            IMAGE = get_image(videoid)
    send = _["queue_6"] if DUR == "Unknown" else _["queue_7"]
    cap = _["queue_8"].format(app.mention, title, typo, user, send)
    upl = (
        queue_markup(_, DUR, "c" if cplay else "g", videoid)
        if DUR == "Unknown"
        else queue_markup(
            _,
            DUR,
            "c" if cplay else "g",
            videoid,
            seconds_to_min(got[0]["played"]),
            got[0]["dur"],
        )
    )
    basic[videoid] = True
    mystic_data = await send_photo_colored(chat_id=message.chat.id, photo=IMAGE, caption=cap, reply_markup=upl)
    if mystic_data and mystic_data.get("message_id"):
        try:
            mystic = await app.get_messages(message.chat.id, mystic_data["message_id"])
        except:
            mystic = mystic_data
    else:
        mystic = await message.reply_photo(IMAGE, caption=cap, reply_markup=buttons_to_inline_markup(upl))
    if DUR != "Unknown":
        try:
            while db[chat_id][0]["vidid"] == videoid:
                await asyncio.sleep(5)
                if await is_active_chat(chat_id):
                    if basic[videoid]:
                        if await is_music_playing(chat_id):
                            try:
                                buttons = queue_markup(
                                    _,
                                    DUR,
                                    "c" if cplay else "g",
                                    videoid,
                                    seconds_to_min(db[chat_id][0]["played"]),
                                    db[chat_id][0]["dur"],
                                )
                                if isinstance(mystic, dict):
                                    m_chat = mystic.get("chat", {}).get("id", message.chat.id)
                                    m_msg = mystic.get("message_id")
                                    r = await edit_reply_markup_colored(chat_id=m_chat, message_id=m_msg, reply_markup=buttons)
                                    if not r:
                                        try:
                                            await app.edit_message_reply_markup(m_chat, m_msg, reply_markup=buttons_to_inline_markup(buttons))
                                        except:
                                            pass
                                else:
                                    r = await edit_reply_markup_colored(chat_id=mystic.chat.id, message_id=mystic.id, reply_markup=buttons)
                                    if not r:
                                        await mystic.edit_reply_markup(reply_markup=buttons_to_inline_markup(buttons))
                            except FloodWait:
                                pass
                        else:
                            pass
                    else:
                        break
                else:
                    break
        except:
            return


@app.on_callback_query(filters.regex("GetTimer") & ~BANNED_USERS)
async def quite_timer(client, CallbackQuery: CallbackQuery):
    try:
        await CallbackQuery.answer()
    except:
        pass


@app.on_callback_query(filters.regex("GetQueued") & ~BANNED_USERS)
@languageCB
async def queued_tracks(client, CallbackQuery: CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    callback_request = callback_data.split(None, 1)[1]
    what, videoid = callback_request.split("|")
    try:
        chat_id, channel = await get_channeplayCB(_, what, CallbackQuery)
    except:
        return
    if not await is_active_chat(chat_id):
        return await CallbackQuery.answer(_["general_5"], show_alert=True)
    got = db.get(chat_id)
    if not got:
        return await CallbackQuery.answer(_["queue_2"], show_alert=True)
    if len(got) == 1:
        return await CallbackQuery.answer(_["queue_5"], show_alert=True)
    await CallbackQuery.answer()
    basic[videoid] = False
    buttons = queue_back_markup(_, what)
    med = InputMediaPhoto(
        media="https://files.catbox.moe/o9bo13.jpg",
        caption=_["queue_1"], 
    )
    await CallbackQuery.edit_message_media(media=med)
    j = 0
    msg = ""
    for x in got:
        j += 1
        if j == 1:
            msg += f'Streaming :\n\n✨ Title : {x["title"]}\nDuration : {x["dur"]}\nBy : {x["by"]}\n\n'
        elif j == 2:
            msg += f'Queued :\n\n✨ Title : {x["title"]}\nDuration : {x["dur"]}\nBy : {x["by"]}\n\n'
        else:
            msg += f'✨ Title : {x["title"]}\nDuration : {x["dur"]}\nBy : {x["by"]}\n\n'
    if "Queued" in msg:
        if len(msg) < 700:
            await asyncio.sleep(1)
            return await edit_message_text_colored(chat_id=CallbackQuery.message.chat.id, message_id=CallbackQuery.message.id, text=msg, reply_markup=buttons)
        if "✨" in msg:
            msg = msg.replace("✨", "")
        link = await VISHALBIN(msg)
        med = {"type": "photo", "media": link, "caption": _["queue_3"].format(link)}
        await edit_message_media_colored(chat_id=CallbackQuery.message.chat.id, message_id=CallbackQuery.message.id, media=med, reply_markup=buttons)
    else:
        await asyncio.sleep(1)
        return await edit_message_text_colored(chat_id=CallbackQuery.message.chat.id, message_id=CallbackQuery.message.id, text=msg, reply_markup=buttons)


@app.on_callback_query(filters.regex("queue_back_timer") & ~BANNED_USERS)
@languageCB
async def queue_back(client, CallbackQuery: CallbackQuery, _):
    callback_data = CallbackQuery.data.strip()
    cplay = callback_data.split(None, 1)[1]
    try:
        chat_id, channel = await get_channeplayCB(_, cplay, CallbackQuery)
    except:
        return
    if not await is_active_chat(chat_id):
        return await CallbackQuery.answer(_["general_5"], show_alert=True)
    got = db.get(chat_id)
    if not got:
        return await CallbackQuery.answer(_["queue_2"], show_alert=True)
    await CallbackQuery.answer(_["set_cb_5"], show_alert=True)
    file = got[0]["file"]
    videoid = got[0]["vidid"]
    user = got[0]["by"]
    title = (got[0]["title"]).title()
    typo = (got[0]["streamtype"]).title()
    DUR = get_duration(got)
    if "live_" in file:
        IMAGE = get_image(videoid)
    elif "vid_" in file:
        IMAGE = get_image(videoid)
    elif "index_" in file:
        IMAGE = config.STREAM_IMG_URL
    else:
        if videoid == "telegram":
            IMAGE = (
                config.TELEGRAM_AUDIO_URL
                if typo == "Audio"
                else config.TELEGRAM_VIDEO_URL
            )
        elif videoid == "soundcloud":
            IMAGE = config.SOUNCLOUD_IMG_URL
        else:
            IMAGE = get_image(videoid)
    send = _["queue_6"] if DUR == "Unknown" else _["queue_7"]
    cap = _["queue_8"].format(app.mention, title, typo, user, send)
    upl = (
        queue_markup(_, DUR, cplay, videoid)
        if DUR == "Unknown"
        else queue_markup(
            _,
            DUR,
            cplay,
            videoid,
            seconds_to_min(got[0]["played"]),
            got[0]["dur"],
        )
    )
    basic[videoid] = True

    med = {"type": "photo", "media": IMAGE, "caption": cap}
    mystic_data = await edit_message_media_colored(chat_id=CallbackQuery.message.chat.id, message_id=CallbackQuery.message.id, media=med, reply_markup=upl)
    if mystic_data and mystic_data.get("message_id"):
        try:
            mystic = await app.get_messages(CallbackQuery.message.chat.id, mystic_data["message_id"])
        except:
            mystic = mystic_data
    else:
        mystic = await CallbackQuery.edit_message_media(media=InputMediaPhoto(media=IMAGE, caption=cap), reply_markup=buttons_to_inline_markup(upl))
    if DUR != "Unknown":
        try:
            while db[chat_id][0]["vidid"] == videoid:
                await asyncio.sleep(5)
                if await is_active_chat(chat_id):
                    if basic[videoid]:
                        if await is_music_playing(chat_id):
                            try:
                                buttons = queue_markup(
                                    _,
                                    DUR,
                                    cplay,
                                    videoid,
                                    seconds_to_min(db[chat_id][0]["played"]),
                                    db[chat_id][0]["dur"],
                                )
                                if isinstance(mystic, dict):
                                    m_chat = mystic.get("chat", {}).get("id", CallbackQuery.message.chat.id)
                                    m_msg = mystic.get("message_id")
                                    r = await edit_reply_markup_colored(chat_id=m_chat, message_id=m_msg, reply_markup=buttons)
                                    if not r:
                                        try:
                                            await app.edit_message_reply_markup(m_chat, m_msg, reply_markup=buttons_to_inline_markup(buttons))
                                        except:
                                            pass
                                else:
                                    r = await edit_reply_markup_colored(chat_id=mystic.chat.id, message_id=mystic.id, reply_markup=buttons)
                                    if not r:
                                        await mystic.edit_reply_markup(reply_markup=buttons_to_inline_markup(buttons))
                            except FloodWait:
                                pass
                        else:
                            pass
                    else:
                        break
                else:
                    break
        except:
            return
