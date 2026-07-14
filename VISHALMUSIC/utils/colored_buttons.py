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

import asyncio
import json
import logging
import aiohttp
from typing import List, Optional, Union

import config

LOGGER = logging.getLogger(__name__)

if not config.BOT_TOKEN:
    LOGGER.error("❌ BOT_TOKEN is not set! Colors will not work.")
BOT_API_URL = f"https://api.telegram.org/bot{config.BOT_TOKEN or ''}"

_session: Optional[aiohttp.ClientSession] = None


async def _get_session() -> aiohttp.ClientSession:
    global _session
    if _session and not _session.closed:
        return _session
    _session = aiohttp.ClientSession(
        timeout=aiohttp.ClientTimeout(total=30)
    )
    return _session


async def _bot_api_post(endpoint: str, payload: dict, retries: int = 3) -> Optional[dict]:
    if not config.BOT_TOKEN:
        return None
    session = await _get_session()
    last_error = None
    for attempt in range(retries):
        try:
            async with session.post(f"{BOT_API_URL}/{endpoint}", data=payload) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    return result.get("result")
                last_error = f"HTTP {resp.status}"
                LOGGER.warning("Bot API %s attempt %d failed: %s", endpoint, attempt + 1, last_error)
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            last_error = str(e)
            LOGGER.warning("Bot API %s attempt %d error: %s", endpoint, attempt + 1, last_error)
        if attempt < retries - 1:
            await asyncio.sleep(0.5 * (attempt + 1))
    LOGGER.error("Bot API %s failed after %d retries: %s", endpoint, retries, last_error)
    return None


def buttons_to_inline_markup(buttons: List[List[dict]]):
    """Convert dict-style colored buttons back to Pyrogram InlineKeyboardMarkup for fallback."""
    from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    kb = []
    for row in buttons:
        kb_row = []
        for btn in row:
            kwargs = {"text": btn["text"]}
            if "callback_data" in btn:
                kwargs["callback_data"] = btn["callback_data"]
            if "url" in btn:
                kwargs["url"] = btn["url"]
            kb_row.append(InlineKeyboardButton(**kwargs))
        kb.append(kb_row)
    return InlineKeyboardMarkup(kb)


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
    session = await _get_session()

    if reply_markup:
        markup_json = json.dumps({"inline_keyboard": reply_markup})
    else:
        markup_json = None

    import os
    if photo and os.path.exists(photo):
        try:
            data = aiohttp.FormData()
            data.add_field("chat_id", str(chat_id))
            data.add_field("caption", caption)
            data.add_field("parse_mode", parse_mode)
            if markup_json:
                data.add_field("reply_markup", markup_json)
            f = open(photo, "rb")
            data.add_field("photo", f, filename=os.path.basename(photo))

            try:
                async with session.post(f"{BOT_API_URL}/sendPhoto", data=data) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        return result.get("result")
                    return None
            finally:
                f.close()
        except Exception:
            return None
    else:
        payload = {
            "chat_id": chat_id,
            "photo": photo,
            "caption": caption,
            "parse_mode": parse_mode,
        }
        if markup_json:
            payload["reply_markup"] = markup_json

        return await _bot_api_post("sendPhoto", payload)


async def send_message_colored(
    chat_id: Union[int, str],
    text: str,
    reply_markup: List[List[dict]] = None,
    parse_mode: str = "HTML",
    disable_web_page_preview: bool = False,
) -> Optional[dict]:
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": disable_web_page_preview,
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps({"inline_keyboard": reply_markup})
    return await _bot_api_post("sendMessage", payload)


async def edit_message_text_colored(
    chat_id: Union[int, str],
    message_id: int,
    text: str,
    reply_markup: List[List[dict]] = None,
    parse_mode: str = "HTML",
    disable_web_page_preview: bool = False,
) -> Optional[dict]:
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": disable_web_page_preview,
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps({"inline_keyboard": reply_markup})
    return await _bot_api_post("editMessageText", payload)


async def edit_message_caption_colored(
    chat_id: Union[int, str],
    message_id: int,
    caption: str,
    reply_markup: List[List[dict]] = None,
    parse_mode: str = "HTML",
) -> Optional[dict]:
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "caption": caption,
        "parse_mode": parse_mode,
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps({"inline_keyboard": reply_markup})
    return await _bot_api_post("editMessageCaption", payload)


async def edit_message_media_colored(
    chat_id: Union[int, str],
    message_id: int,
    media: dict = None,
    reply_markup: List[List[dict]] = None,
) -> Optional[dict]:
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
    }
    if media:
        payload["media"] = json.dumps(media)
    if reply_markup:
        payload["reply_markup"] = json.dumps({"inline_keyboard": reply_markup})
    return await _bot_api_post("editMessageMedia", payload)


async def edit_reply_markup_colored(
    chat_id: Union[int, str],
    message_id: int,
    reply_markup: List[List[dict]] = None,
) -> Optional[dict]:
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
    }
    if reply_markup:
        payload["reply_markup"] = json.dumps({"inline_keyboard": reply_markup})
    return await _bot_api_post("editMessageReplyMarkup", payload)


# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
