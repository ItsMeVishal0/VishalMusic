# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   GitHub : github.com/ItsMeVishal0/VishalMusic
#   Developer : @ItsMeVishalBots | Telegram
#   Module : Colored Inline Buttons via Bot API HTTP
# ═══════════════════════════════════════════════════════════

"""
Kurigram/Pyrogram uses MTProto which doesn't support the 'style'
field on buttons yet. This module sends messages via Bot API HTTP
to enable colored inline keyboard buttons.

Styles: "primary" (blue), "success" (green), "danger" (red)
"""

import json
import aiohttp
from typing import List, Optional, Union

import config

BOT_API_URL = f"https://api.telegram.org/bot{config.BOT_TOKEN}"

_session: Optional[aiohttp.ClientSession] = None


async def _get_session() -> aiohttp.ClientSession:
    global _session
    if _session and not _session.closed:
        return _session
    _session = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=30)
    )
    return _session


def styled_button(text: str, callback_data: str = None, url: str = None, style: str = None):
    """Create a button dict with optional style (color).

    style: "primary" (blue), "success" (green), "danger" (red), or None (default)
    """
    btn = {"text": text}
    if callback_data:
        btn["callback_data"] = callback_data
    if url:
        btn["url"] = url
    if style:
        btn["style"] = style
    return btn


async def send_photo_colored(
    chat_id: Union[int, str],
    photo: str,
    caption: str = "",
    reply_markup: List[List[dict]] = None,
    parse_mode: str = "HTML",
) -> Optional[dict]:
    """Send a photo with colored inline keyboard buttons via Bot API HTTP.

    photo: URL string OR local file path
    reply_markup: list of rows, each row is a list of styled_button() dicts
    Returns: the sent message dict from Telegram, or None on failure
    """
    session = await _get_session()

    if reply_markup:
        markup_json = json.dumps({"inline_keyboard": reply_markup})
    else:
        markup_json = None

    # If photo is a local file, upload it via multipart form
    import os
    if photo and os.path.exists(photo):
        try:
            data = aiohttp.FormData()
            data.add_field("chat_id", str(chat_id))
            data.add_field("caption", caption)
            data.add_field("parse_mode", parse_mode)
            if markup_json:
                data.add_field("reply_markup", markup_json)
            data.add_field("photo", open(photo, "rb"), filename=os.path.basename(photo))

            async with session.post(f"{BOT_API_URL}/sendPhoto", data=data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result.get("result")
                return None
        except Exception:
            return None
    else:
        # photo is a URL or file_id
        payload = {
            "chat_id": chat_id,
            "photo": photo,
            "caption": caption,
            "parse_mode": parse_mode,
        }
        if markup_json:
            payload["reply_markup"] = markup_json

        try:
            async with session.post(f"{BOT_API_URL}/sendPhoto", data=payload) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result.get("result")
                return None
        except Exception:
            return None


async def edit_reply_markup_colored(
    chat_id: Union[int, str],
    message_id: int,
    reply_markup: List[List[dict]] = None,
) -> Optional[dict]:
    """Edit an existing message's inline keyboard with colored buttons.

    reply_markup: list of rows, each row is a list of styled_button() dicts
    """
    session = await _get_session()
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps({"inline_keyboard": reply_markup})

    try:
        async with session.post(f"{BOT_API_URL}/editMessageReplyMarkup", data=payload) as resp:
            if resp.status == 200:
                data = await resp.json()
                return data.get("result")
            return None
    except Exception:
        return None


# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
