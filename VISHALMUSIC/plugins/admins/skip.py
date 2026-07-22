from pyrogram import filters
from pyrogram.types import Message

import config
from VISHALMUSIC import YouTube, app
from VISHALMUSIC.core.call import VISHAL
from VISHALMUSIC.misc import db
from VISHALMUSIC.utils.database import get_loop
from VISHALMUSIC.utils.stream.autoplay import is_autoplay_on
from VISHALMUSIC.utils.decorators import AdminRightsCheck
from VISHALMUSIC.utils.inline import close_markup
from VISHALMUSIC.utils.inline.play import colored_stream_markup
from VISHALMUSIC.utils.stream.autoclear import auto_clean
from VISHALMUSIC.utils.thumbnails import get_thumb
from VISHALMUSIC.utils.colored_buttons import buttons_to_inline_markup, smart_send_photo
from config import BANNED_USERS


async def _skip_send_photo(chat_id, message, photo, caption, buttons, db_ref, chat_id_ref, markup_type):
    """Send photo with colored buttons via smart wrapper."""
    from VISHALMUSIC.misc import db

    run = await smart_send_photo(
        chat_id=chat_id,
        photo=photo,
        caption=caption,
        reply_markup=buttons,
    )
    try:
        db[chat_id_ref][0]["mystic"] = run
        db[chat_id_ref][0]["markup"] = markup_type
    except Exception:
        pass
    return run


@app.on_message(
    filters.command(["skip", "cskip", "next", "cnext"], prefixes=["/", "!"]) & filters.group & ~BANNED_USERS
)
@AdminRightsCheck
async def skip(cli, message: Message, _, chat_id):
    if not len(message.command) < 2:
        loop = await get_loop(chat_id)
        if loop != 0:
            return await message.reply_text(_["admin_8"])
        state = message.text.split(None, 1)[1].strip()
        if state.isnumeric():
            state = int(state)
            check = db.get(chat_id)
            if check and isinstance(check, list):
                count = len(check)
                if count > 2:
                    count = int(count - 1)
                    if 1 <= state <= count:
                        for x in range(state):
                            popped = None
                            try:
                                popped = check.pop(0) if len(check) > 0 else None
                                if popped is None:
                                    return await message.reply_text(_["admin_12"])
                            except:
                                return await message.reply_text(_["admin_12"])
                            if popped:
                                await auto_clean(popped)
                            if not check or len(check) == 0:
                                try:
                                    await message.reply_text(
                                        text=_["admin_6"].format(
                                            message.from_user.mention,
                                            message.chat.title,
                                        ),
                                        reply_markup=buttons_to_inline_markup(close_markup(_)),
                                    )
                                    await VISHAL.stop_stream(chat_id)
                                except:
                                    return
                                break
                    else:
                        return await message.reply_text(_["admin_11"].format(count))
                else:
                    return await message.reply_text(_["admin_10"])
            else:
                return await message.reply_text(_["queue_2"])
        else:
            return await message.reply_text(_["admin_9"])
    else:
        check = db.get(chat_id)
        popped = None
        if check and isinstance(check, list) and len(check) > 0:
            try:
                popped = check.pop(0)
                if popped:
                    await auto_clean(popped)
                if not check or len(check) == 0:
                    if await is_autoplay_on(chat_id):
                        try:
                            await VISHAL.stop_stream(chat_id)
                            from VISHALMUSIC.utils.database import remove_active_chat, remove_active_video_chat
                            await remove_active_chat(chat_id)
                            await remove_active_video_chat(chat_id)
                            from VISHALMUSIC.utils.stream.autoplay import auto_play_next
                            await auto_play_next(
                                chat_id,
                                popped.get("chat_id", chat_id),
                                popped.get("title", ""),
                                popped.get("vidid", ""),
                            )
                            return
                        except Exception:
                            pass
                    await message.reply_text(
                        text=_["admin_6"].format(
                            message.from_user.mention, message.chat.title
                        ),
                        reply_markup=buttons_to_inline_markup(close_markup(_)),
                    )
                    try:
                        return await VISHAL.stop_stream(chat_id)
                    except:
                        return
            except:
                try:
                    await message.reply_text(
                        text=_["admin_6"].format(
                            message.from_user.mention, message.chat.title
                        ),
                        reply_markup=buttons_to_inline_markup(close_markup(_)),
                    )
                    return await VISHAL.stop_stream(chat_id)
                except:
                    return
        else:
            return await message.reply_text(_["queue_2"])
        
        # Check if check has items before accessing
        if not check or len(check) == 0:
            return await message.reply_text(_["queue_2"])
            
        queued = check[0].get("file")
        title = (check[0].get("title", "")).title()
        user = check[0].get("by", "")
        streamtype = check[0].get("streamtype", "")
        videoid = check[0].get("vidid", "")
        status = True if str(streamtype) == "video" else None
        if db.get(chat_id) and len(db[chat_id]) > 0:
            db[chat_id][0]["played"] = 0
        exis = check[0].get("old_dur") if check and len(check) > 0 else None
        if exis and db.get(chat_id) and len(db[chat_id]) > 0:
            db[chat_id][0]["dur"] = exis
            db[chat_id][0]["seconds"] = check[0].get("old_second", 0) if check and len(check) > 0 else 0
            db[chat_id][0]["speed_path"] = None
            db[chat_id][0]["speed"] = 1.0
    if "live_" in queued:
        n, link = await YouTube.video(videoid, True)
        if n == 0:
            return await message.reply_text(_["admin_7"].format(title))
        try:
            image = await YouTube.thumbnail(videoid, True)
        except:
            image = None
        try:
            await VISHAL.skip_stream(chat_id, link, video=status, image=image)
        except:
            return await message.reply_text(_["call_6"])
        ap_status = await is_autoplay_on(chat_id)
        button = colored_stream_markup(_, chat_id, autoplay_status=ap_status)
        img = await get_thumb(videoid)
        await _skip_send_photo(
            message.chat.id, message, img,
            _["stream_1"].format(f"https://t.me/{app.username}?start=info_{videoid}", title[:23], check[0]["dur"], user),
            button, None, chat_id, "tg",
        )
    elif "vid_" in queued:
        mystic = await message.reply_text(_["call_7"], disable_web_page_preview=True)
        
        # Retry logic for YouTube download failures
        max_retries = 3
        download_success = False
        file_path = None
        direct = False

        for attempt in range(max_retries):
            try:
                file_path, direct = await YouTube.download(videoid, mystic, videoid=True, video=status)
                if file_path:
                    download_success = True
                    break
            except:
                if attempt < max_retries - 1:
                    continue
                else:
                    return await mystic.edit_text(_["call_6"])

        if not download_success or not file_path:
            return await mystic.edit_text(_["call_6"])
        try:
            image = await YouTube.thumbnail(videoid, True)
        except:
            image = None
        try:
            await VISHAL.skip_stream(chat_id, file_path, video=status, image=image)
        except:
            return await mystic.edit_text(_["call_6"])
        ap_status = await is_autoplay_on(chat_id)
        button = colored_stream_markup(_, chat_id, autoplay_status=ap_status)
        img = await get_thumb(videoid)
        await _skip_send_photo(
            message.chat.id, message, img,
            _["stream_1"].format(f"https://t.me/{app.username}?start=info_{videoid}", title[:23], check[0]["dur"], user),
            button, None, chat_id, "stream",
        )
        await mystic.delete()
    elif "index_" in queued:
        try:
            await VISHAL.skip_stream(chat_id, videoid, video=status)
        except:
            return await message.reply_text(_["call_6"])
        ap_status = await is_autoplay_on(chat_id)
        button = colored_stream_markup(_, chat_id, autoplay_status=ap_status)
        await _skip_send_photo(
            message.chat.id, message, config.STREAM_IMG_URL,
            _["stream_2"].format(user),
            button, None, chat_id, "tg",
        )
    else:
        if videoid == "telegram":
            image = None
        elif videoid == "soundcloud":
            image = None
        else:
            try:
                image = await YouTube.thumbnail(videoid, True)
            except:
                image = None
        try:
            await VISHAL.skip_stream(chat_id, queued, video=status, image=image)
        except:
            return await message.reply_text(_["call_6"])
        ap_status = await is_autoplay_on(chat_id)
        if videoid == "telegram":
            button = colored_stream_markup(_, chat_id, autoplay_status=ap_status)
            photo = config.TELEGRAM_AUDIO_URL if str(streamtype) == "audio" else config.TELEGRAM_VIDEO_URL
            await _skip_send_photo(
                message.chat.id, message, photo,
                _["stream_1"].format(config.SUPPORT_CHAT, title[:23], check[0]["dur"], user),
                button, None, chat_id, "tg",
            )
        elif videoid == "soundcloud":
            button = colored_stream_markup(_, chat_id, autoplay_status=ap_status)
            photo = config.SOUNCLOUD_IMG_URL if str(streamtype) == "audio" else config.TELEGRAM_VIDEO_URL
            await _skip_send_photo(
                message.chat.id, message, photo,
                _["stream_1"].format(config.SUPPORT_CHAT, title[:23], check[0]["dur"], user),
                button, None, chat_id, "tg",
            )
        else:
            button = colored_stream_markup(_, chat_id, autoplay_status=ap_status)
            img = await get_thumb(videoid)
            await _skip_send_photo(
                message.chat.id, message, img,
                _["stream_1"].format(f"https://t.me/{app.username}?start=info_{videoid}", title[:23], check[0]["dur"], user),
                button, None, chat_id, "stream",
            )
