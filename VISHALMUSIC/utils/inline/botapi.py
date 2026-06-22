"""
Direct Bot API calls for colored inline buttons (style field)
Telegram Bot API 8.3+ supports: constructive (green), destructive (red), secondary (blue)
"""
import json
import aiohttp
from config import BOT_TOKEN

BOT_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


async def send_photo_colored(chat_id, photo, caption, reply_markup_dict, parse_mode="HTML"):
    """
    Send photo with colored inline buttons using Bot API directly.
    
    reply_markup_dict format:
    {"inline_keyboard": [[{"text":"..","callback_data":"..","style":"constructive"}]]}
    
    style values:
      "constructive" = green
      "destructive" = red  
      "secondary" = blue/grey
      (no style) = default
    """
    data = {
        "chat_id": chat_id,
        "photo": photo,
        "caption": caption,
        "parse_mode": parse_mode,
        "reply_markup": json.dumps(reply_markup_dict),
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BOT_API_URL}/sendPhoto", data=data) as resp:
            return await resp.json()


async def edit_markup_colored(chat_id, message_id, reply_markup_dict):
    """
    Edit message reply markup with colored buttons.
    """
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reply_markup": json.dumps(reply_markup_dict),
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{BOT_API_URL}/editMessageReplyMarkup", data=data) as resp:
            return await resp.json()


def colored_stream_markup(_, chat_id, autoplay_status: bool = False):
    """
    Stream control markup with colored buttons.
    Green = Resume, Skip | Blue = Pause, Replay | Red = Stop, Close
    """
    ap_text = "🔁 ᴀᴜᴛᴏᴘʟᴀʏ : ᴏɴ ✅" if autoplay_status else "🔁 ᴀᴜᴛᴏᴘʟᴀʏ : ᴏғғ ❌"
    return {
        "inline_keyboard": [
            [
                {"text": "▷", "callback_data": f"ADMIN Resume|{chat_id}", "style": "constructive"},
                {"text": "II", "callback_data": f"ADMIN Pause|{chat_id}", "style": "secondary"},
                {"text": "↻", "callback_data": f"ADMIN Replay|{chat_id}", "style": "secondary"},
                {"text": "‣‣I", "callback_data": f"ADMIN Skip|{chat_id}", "style": "constructive"},
                {"text": "▢", "callback_data": f"ADMIN Stop|{chat_id}", "style": "destructive"},
            ],
            [{"text": ap_text, "callback_data": f"AUTOPLAY_TOGGLE {chat_id}"}],
            [{"text": _["CLOSE_BUTTON"], "callback_data": "close", "style": "destructive"}],
        ]
    }


def colored_stream_markup_timer(_, chat_id, played, dur, autoplay_status: bool = False):
    """
    Timer + colored stream control markup.
    """
    from VISHALMUSIC.utils.inline.play import should_update_progress, generate_progress_bar
    from VISHALMUSIC.utils.formatters import time_to_seconds

    if not should_update_progress(chat_id):
        return None

    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    bar = generate_progress_bar(played_sec, duration_sec)
    ap_text = "🔁 ᴀᴜᴛᴏᴘʟᴀʏ : ᴏɴ ✅" if autoplay_status else "🔁 ᴀᴜᴛᴏᴘʟᴀʏ : ᴏғғ ❌"

    return {
        "inline_keyboard": [
            [{"text": f"{played} {bar} {dur}", "callback_data": "GetTimer"}],
            [
                {"text": "▷", "callback_data": f"ADMIN Resume|{chat_id}", "style": "constructive"},
                {"text": "II", "callback_data": f"ADMIN Pause|{chat_id}", "style": "secondary"},
                {"text": "↻", "callback_data": f"ADMIN Replay|{chat_id}", "style": "secondary"},
                {"text": "‣‣I", "callback_data": f"ADMIN Skip|{chat_id}", "style": "constructive"},
                {"text": "▢", "callback_data": f"ADMIN Stop|{chat_id}", "style": "destructive"},
            ],
            [{"text": ap_text, "callback_data": f"AUTOPLAY_TOGGLE {chat_id}"}],
            [{"text": _["CLOSE_BUTTON"], "callback_data": "close", "style": "destructive"}],
        ]
    }
