import asyncio

from pyrogram import filters

from VISHALMUSIC import YouTube, app
from VISHALMUSIC.utils.channelplay import get_channeplayCB
from VISHALMUSIC.utils.decorators.language import languageCB
from VISHALMUSIC.utils.errors import capture_callback_err
from VISHALMUSIC.utils.stream.stream import stream
from VISHALMUSIC.plugins.play.play import start_search_animation, get_search_msg_and_frames
from config import BANNED_USERS


@app.on_callback_query(filters.regex("LiveStream") & ~BANNED_USERS)
@languageCB
@capture_callback_err
async def play_live_stream(client, CallbackQuery, _):
    data = CallbackQuery.data.strip().split(None, 1)[1]
    vidid, user_id, mode, cplay, fplay = data.split("|")

    if CallbackQuery.from_user.id != int(user_id):
        try:
            return await CallbackQuery.answer(_["playcb_1"], show_alert=True)
        except Exception:
            return

    try:
        chat_id, channel = await get_channeplayCB(_, cplay, CallbackQuery)
    except Exception:
        return

    is_video = (mode == "v")
    forceplay = (fplay == "f")
    user_name = CallbackQuery.from_user.first_name

    try:
        await CallbackQuery.message.delete()
    except Exception:
        pass
    try:
        await CallbackQuery.answer()
    except Exception:
        pass

    mystic_text, anim_frames = get_search_msg_and_frames(_, channel, CallbackQuery.from_user.mention)
    mystic = await CallbackQuery.message.reply_text(mystic_text)

    # Start animation
    anim_task = None
    if anim_frames:
        anim_task = asyncio.create_task(start_search_animation(mystic, anim_frames))
    _original_edit = mystic.edit_text
    _original_delete = mystic.delete

    async def _animated_edit(*args, **kwargs):
        if anim_task and not anim_task.done():
            anim_task.cancel()
            try:
                await anim_task
            except asyncio.CancelledError:
                pass
        return await _original_edit(*args, **kwargs)

    async def _animated_delete(*args, **kwargs):
        if anim_task and not anim_task.done():
            anim_task.cancel()
            try:
                await anim_task
            except asyncio.CancelledError:
                pass
        return await _original_delete(*args, **kwargs)

    mystic.edit_text = _animated_edit
    mystic.delete = _animated_delete

    try:
        details, track_id = await YouTube.track("", videoid=vidid)
    except Exception:
        return await mystic.edit_text(_["play_3"])

    if not details.get("duration_min"):
        try:
            await stream(
                _,
                mystic,
                int(user_id),
                details,
                chat_id,
                user_name,
                CallbackQuery.message.chat.id,
                is_video,
                streamtype="live",
                forceplay=forceplay,
            )
        except Exception as e:
            ex_type = type(e).__name__
            err = e if ex_type == "AssistantErr" else _["general_2"].format(ex_type)
            return await mystic.edit_text(err)
    else:
        return await mystic.edit_text("» ɴᴏᴛ ᴀ ʟɪᴠᴇ sᴛʀᴇᴀᴍ.")

    await mystic.delete()
