# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   GitHub : github.com/ItsMeVishal0/VishalMusic
#   Developer : @ItsMeVishalBots | Telegram
#   Module : Stream Handler (Colored Buttons)
# ═══════════════════════════════════════════════════════════

import asyncio
import os
from random import randint
from typing import Union

import config
from VISHALMUSIC import Carbon, YouTube, app
from VISHALMUSIC.core.call import VISHAL
from VISHALMUSIC.misc import db
from VISHALMUSIC.utils.stream.autoplay import is_autoplay_on
from VISHALMUSIC.utils.database import add_active_video_chat, is_active_chat
from VISHALMUSIC.utils.exceptions import AssistantErr
from VISHALMUSIC.utils.inline import aq_markup, close_markup, stream_markup
from VISHALMUSIC.utils.colored_buttons import (
    send_photo_colored,
    send_message_colored,
    edit_message_text_colored,
    buttons_to_inline_markup,
)
from VISHALMUSIC.utils.pastebin import VISHALBIN
from VISHALMUSIC.utils.stream.queue import put_queue, put_queue_index
from VISHALMUSIC.utils.thumbnails import get_thumb
from VISHALMUSIC.utils.errors import capture_internal_err


def _store_mystic(chat_id, run, markup_type, caption=None):
    """Safely store mystic message reference — guards against race conditions."""
    try:
        playlist = db.get(chat_id)
        if not playlist or not isinstance(playlist, list) or len(playlist) == 0:
            # Queue was cleared while photo was being sent — store for later
            if chat_id not in db or not isinstance(db.get(chat_id), list):
                db[chat_id] = [{}]
            if len(db[chat_id]) == 0:
                db[chat_id].append({})
        db[chat_id][0]["mystic"] = run
        db[chat_id][0]["markup"] = markup_type
        if caption:
            db[chat_id][0]["base_caption"] = caption
    except Exception:
        pass


async def _send_or_fallback_photo(_, original_chat_id, img, caption, colored_buttons, db_ref, chat_id, markup_type):
    """Send photo with colored buttons via Bot API, fallback to Pyrogram if it fails."""
    run_data = await send_photo_colored(
        chat_id=original_chat_id,
        photo=img,
        caption=caption,
        reply_markup=colored_buttons,
    )
    if run_data and run_data.get("message_id"):
        try:
            run = await app.get_messages(original_chat_id, run_data["message_id"])
            _store_mystic(chat_id, run, markup_type, caption)
        except Exception:
            _store_mystic(chat_id, run_data, markup_type, caption)
    else:
        # Fallback to Pyrogram (no button colors)
        try:
            run = await app.send_photo(
                original_chat_id,
                photo=img,
                caption=caption,
                reply_markup=buttons_to_inline_markup(colored_buttons),
            )
            _store_mystic(chat_id, run, markup_type, caption)
        except Exception:
            pass


async def _send_or_fallback_message(chat_id, text, colored_buttons):
    """Send message with colored buttons via Bot API, fallback to Pyrogram if it fails."""
    result = await send_message_colored(
        chat_id=chat_id,
        text=text,
        reply_markup=colored_buttons,
    )
    if result and result.get("message_id"):
        try:
            return await app.get_messages(chat_id, result["message_id"])
        except Exception:
            return result
    return await app.send_message(
        chat_id=chat_id,
        text=text,
        reply_markup=buttons_to_inline_markup(colored_buttons),
    )


@capture_internal_err
async def stream(
    _,
    mystic,
    user_id,
    result,
    chat_id,
    user_name,
    original_chat_id,
    video: Union[bool, str] = None,
    streamtype: Union[bool, str] = None,
    spotify: Union[bool, str] = None,
    forceplay: Union[bool, str] = None,
) -> None:
    if not result:
        return

    forceplay = bool(forceplay)
    is_video = bool(video)

    if forceplay:
        await VISHAL.force_stop_stream(chat_id)

    if streamtype == "playlist":
        msg = f"{_['play_19']}\n\n"
        count = 0
        position = 0

        # ── LIGHTNING-FAST: fetch all playlist details in parallel ──────────────
        limited = list(result)[:config.PLAYLIST_FETCH_LIMIT]

        async def _fetch_details(search):
            try:
                return await YouTube.details(search, videoid=search)
            except Exception:
                return None

        details_list = await asyncio.gather(*[_fetch_details(s) for s in limited])
        # ────────────────────────────────────────────────────────────────────────

        for details in details_list:
            if details is None:
                continue
            title, duration_min, duration_sec, thumbnail, vidid = details

            if str(duration_min) == "None":
                continue
            if duration_sec and duration_sec > config.DURATION_LIMIT:
                continue

            if await is_active_chat(chat_id):
                await put_queue(
                    chat_id,
                    original_chat_id,
                    f"vid_{vidid}",
                    title,
                    duration_min,
                    user_name,
                    vidid,
                    user_id,
                    "video" if is_video else "audio",
                )
                position = len(db.get(chat_id)) - 1
                count += 1
                msg += f"{count}. {title[:70]}\n"
                msg += f"{_['play_20']} {position}\n\n"
            else:
                if not forceplay:
                    db[chat_id] = []
                thumb_task = asyncio.create_task(get_thumb(vidid))
                try:
                    file_path, direct = await YouTube.download(
                        vidid, mystic, video=is_video, videoid=vidid
                    )
                except Exception:
                    thumb_task.cancel()
                    raise AssistantErr(_["play_14"])
                if not file_path:
                    thumb_task.cancel()
                    raise AssistantErr(_["play_14"])

                await VISHAL.join_call(
                    chat_id,
                    original_chat_id,
                    file_path,
                    video=is_video,
                    image=thumbnail,
                )
                if not await is_active_chat(chat_id):
                    thumb_task.cancel()
                    raise AssistantErr(_["call_6"])
                await put_queue(
                    chat_id,
                    original_chat_id,
                    file_path if direct else f"vid_{vidid}",
                    title,
                    duration_min,
                    user_name,
                    vidid,
                    user_id,
                    "video" if is_video else "audio",
                    forceplay=forceplay,
                )
                try:
                    img = await thumb_task
                except Exception:
                    img = await get_thumb(vidid)
                ap_status = await is_autoplay_on(chat_id)
                colored_buttons = stream_markup(_, chat_id, autoplay_status=ap_status)
                caption = _["stream_1"].format(
                    f"https://t.me/{app.username}?start=info_{vidid}",
                    title[:23],
                    duration_min,
                    user_name,
                )
                await _send_or_fallback_photo(_, original_chat_id, img, caption, colored_buttons, None, chat_id, "stream")

        if count == 0:
            return
        link = await VISHALBIN(msg)
        lines = msg.count("\n")
        car = os.linesep.join(msg.split(os.linesep)[:17]) if lines >= 17 else msg
        try:
            carbon = await Carbon.generate(car, randint(100, 10000000))
            playlist_photo = carbon
        except Exception:
            playlist_photo = config.PLAYLIST_IMG_URL
        upl = close_markup(_)
        final_position = len(db.get(chat_id) or []) - 1
        if final_position < 0:
            final_position = 0
        return await _send_or_fallback_photo(
            _,
            original_chat_id,
            playlist_photo,
            _["play_21"].format(final_position, link),
            upl,
            None,
            chat_id,
            "close",
        )

    elif streamtype == "youtube":
        link = result["link"]
        vidid = result["vidid"]
        title = (result["title"]).title()
        duration_min = result["duration_min"]
        thumbnail = result["thumb"]

        thumb_task = asyncio.create_task(get_thumb(vidid))

        try:
            file_path, direct = await YouTube.download(
                vidid, mystic, video=is_video, videoid=vidid
            )
        except Exception:
            thumb_task.cancel()
            raise AssistantErr(_["play_14"])
        if not file_path:
            thumb_task.cancel()
            raise AssistantErr(_["play_14"])

        if await is_active_chat(chat_id):
            thumb_task.cancel()
            await put_queue(
                chat_id,
                original_chat_id,
                file_path if direct else f"vid_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if is_video else "audio",
            )
            position = len(db.get(chat_id)) - 1
            button = aq_markup(_, chat_id)
            await _send_or_fallback_message(
                original_chat_id,
                _["queue_4"].format(position, title[:27], duration_min, user_name),
                button,
            )
        else:
            if not forceplay:
                db[chat_id] = []
            await VISHAL.join_call(
                chat_id,
                original_chat_id,
                file_path,
                video=is_video,
                image=thumbnail,
            )
            if not await is_active_chat(chat_id):
                thumb_task.cancel()
                raise AssistantErr(_["call_6"])
            await put_queue(
                chat_id,
                original_chat_id,
                file_path if direct else f"vid_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if is_video else "audio",
                forceplay=forceplay,
            )
            try:
                img = await thumb_task
            except Exception:
                img = await get_thumb(vidid)
            ap_status = await is_autoplay_on(chat_id)
            colored_buttons = stream_markup(_, chat_id, autoplay_status=ap_status)
            caption = _["stream_1"].format(
                f"https://t.me/{app.username}?start=info_{vidid}",
                title[:23],
                duration_min,
                user_name,
            )
            await _send_or_fallback_photo(_, original_chat_id, img, caption, colored_buttons, None, chat_id, "stream")

    elif streamtype == "soundcloud":
        file_path = result["filepath"]
        title = result["title"]
        duration_min = result["duration_min"]
        if not file_path:
            raise AssistantErr(_["play_14"])

        if await is_active_chat(chat_id):
            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                streamtype,
                user_id,
                "audio",
            )
            position = len(db.get(chat_id)) - 1
            button = aq_markup(_, chat_id)
            await _send_or_fallback_message(
                original_chat_id,
                _["queue_4"].format(position, title[:27], duration_min, user_name),
                button,
            )
        else:
            if not forceplay:
                db[chat_id] = []
            await VISHAL.join_call(chat_id, original_chat_id, file_path, video=False)
            if not await is_active_chat(chat_id):
                raise AssistantErr(_["call_6"])
            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                streamtype,
                user_id,
                "audio",
                forceplay=forceplay,
            )
            ap_status = await is_autoplay_on(chat_id)
            colored_buttons = stream_markup(_, chat_id, autoplay_status=ap_status)
            caption = _["stream_1"].format(
                config.SUPPORT_CHAT, title[:23], duration_min, user_name
            )
            await _send_or_fallback_photo(
                _,
                original_chat_id,
                config.SOUNCLOUD_IMG_URL,
                caption,
                colored_buttons,
                None,
                chat_id,
                "tg",
            )

    elif streamtype == "telegram":
        file_path = result["path"]
        link = result["link"]
        title = (result["title"]).title()
        duration_min = result["dur"]
        if not file_path:
            raise AssistantErr(_["play_14"])

        if await is_active_chat(chat_id):
            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                streamtype,
                user_id,
                "video" if is_video else "audio",
            )
            position = len(db.get(chat_id)) - 1
            button = aq_markup(_, chat_id)
            await _send_or_fallback_message(
                original_chat_id,
                _["queue_4"].format(position, title[:27], duration_min, user_name),
                button,
            )
        else:
            if not forceplay:
                db[chat_id] = []
            await VISHAL.join_call(chat_id, original_chat_id, file_path, video=is_video)
            if not await is_active_chat(chat_id):
                raise AssistantErr(_["call_6"])
            await put_queue(
                chat_id,
                original_chat_id,
                file_path,
                title,
                duration_min,
                user_name,
                streamtype,
                user_id,
                "video" if is_video else "audio",
                forceplay=forceplay,
            )
            if is_video:
                await add_active_video_chat(chat_id)
            ap_status = await is_autoplay_on(chat_id)
            colored_buttons = stream_markup(_, chat_id, autoplay_status=ap_status)
            caption = _["stream_1"].format(link, title[:23], duration_min, user_name)
            await _send_or_fallback_photo(
                _,
                original_chat_id,
                config.TELEGRAM_VIDEO_URL if is_video else config.TELEGRAM_AUDIO_URL,
                caption,
                colored_buttons,
                None,
                chat_id,
                "tg",
            )

    elif streamtype == "live":
        link = result["link"]
        vidid = result["vidid"]
        title = (result["title"]).title()
        thumbnail = result["thumb"]
        duration_min = "Live Track"

        if await is_active_chat(chat_id):
            await put_queue(
                chat_id,
                original_chat_id,
                f"live_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if is_video else "audio",
            )
            position = len(db.get(chat_id)) - 1
            button = aq_markup(_, chat_id)
            await _send_or_fallback_message(
                original_chat_id,
                _["queue_4"].format(position, title[:27], duration_min, user_name),
                button,
            )
        else:
            if not forceplay:
                db[chat_id] = []
            thumb_task = asyncio.create_task(get_thumb(vidid))
            n, file_path = await YouTube.video(link)
            if n == 0:
                thumb_task.cancel()
                raise AssistantErr(_["str_3"])
            if not file_path:
                thumb_task.cancel()
                raise AssistantErr(_["play_14"])

            await VISHAL.join_call(
                chat_id,
                original_chat_id,
                file_path,
                video=is_video,
                image=thumbnail or None,
            )
            await put_queue(
                chat_id,
                original_chat_id,
                f"live_{vidid}",
                title,
                duration_min,
                user_name,
                vidid,
                user_id,
                "video" if is_video else "audio",
                forceplay=forceplay,
            )
            try:
                img = await thumb_task
            except Exception:
                img = await get_thumb(vidid)
            ap_status = await is_autoplay_on(chat_id)
            colored_buttons = stream_markup(_, chat_id, autoplay_status=ap_status)
            caption = _["stream_1"].format(
                f"https://t.me/{app.username}?start=info_{vidid}",
                title[:23],
                duration_min,
                user_name,
            )
            await _send_or_fallback_photo(_, original_chat_id, img, caption, colored_buttons, None, chat_id, "tg")

    elif streamtype == "index":
        link = result
        title = "ɪɴᴅᴇx ᴏʀ ᴍ3ᴜ8 ʟɪɴᴋ"
        duration_min = "00:00"

        if await is_active_chat(chat_id):
            await put_queue_index(
                chat_id,
                original_chat_id,
                "index_url",
                title,
                duration_min,
                user_name,
                link,
                "video" if is_video else "audio",
            )
            position = len(db.get(chat_id)) - 1
            button = aq_markup(_, chat_id)
            await _send_or_fallback_message(
                original_chat_id,
                _["queue_4"].format(position, title[:27], duration_min, user_name),
                button,
            )
        else:
            if not forceplay:
                db[chat_id] = []
            await VISHAL.join_call(
                chat_id,
                original_chat_id,
                link,
                video=is_video,
            )
            await put_queue_index(
                chat_id,
                original_chat_id,
                "index_url",
                title,
                duration_min,
                user_name,
                link,
                "video" if is_video else "audio",
                forceplay=forceplay,
            )
            ap_status = await is_autoplay_on(chat_id)
            colored_buttons = stream_markup(_, chat_id, autoplay_status=ap_status)
            caption = _["stream_2"].format(user_name)
            await _send_or_fallback_photo(
                _,
                original_chat_id,
                config.STREAM_IMG_URL,
                caption,
                colored_buttons,
                None,
                chat_id,
                "tg",
            )
            await mystic.delete()


# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
