# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   GitHub : github.com/ItsMeVishal0/VishalMusic
#   Developer : @ItsMeVishalBots | Telegram
#   Module : Colored Inline Buttons (Bot API Direct Implementation)
# ═══════════════════════════════════════════════════════════

"""
Telegram Bot API colored buttons implementation.
Uses direct Bot API HTTP calls to support colored buttons.

Styles: "primary" (blue), "success" (green), "danger" (red)
"""

import asyncio
import logging
from typing import List, Optional, Union

import aiohttp
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import config

logger = logging.getLogger(__name__)


def styled_button(text: str, callback_data: str = None, url: str = None, style: str = None):
    """Create a button dict with optional style (color).
    
    Args:
        text: Button text
        callback_data: Callback data for inline queries
        url: URL for link buttons
        style: Button color - "primary" (blue), "success" (green), "danger" (red)
    
    Returns:
        Button dictionary with style field
    """
    btn = {"text": text}
    if callback_data:
        btn["callback_data"] = callback_data
    if url:
        btn["url"] = url
    if style:
        btn["style"] = style
    return btn


def buttons_to_inline_markup(buttons: List[List[dict]]) -> InlineKeyboardMarkup:
    """Convert styled button dicts to Pyrogram InlineKeyboardMarkup (WITHOUT colors).
    
    This is the fallback method - creates standard Pyrogram buttons without colors.
    Use the _colored functions below for actual colored buttons via Bot API.
    
    Args:
        buttons: List of button rows, each containing styled_button dicts
        
    Returns:
        InlineKeyboardMarkup ready for use with Pyrogram
    """
    kb = []
    for row in buttons:
        kb_row = []
        for btn in row:
            kwargs = {"text": btn["text"]}
            if "callback_data" in btn:
                kwargs["callback_data"] = btn["callback_data"]
            if "url" in btn:
                kwargs["url"] = btn["url"]
            # Skip 'style' - standard Pyrogram doesn't support it
            kb_row.append(InlineKeyboardButton(**kwargs))
        kb.append(kb_row)
    return InlineKeyboardMarkup(kb)


# ═══════════════════════════════════════════════════════════
#  BOT API DIRECT IMPLEMENTATION (COLORED BUTTONS)
# ═══════════════════════════════════════════════════════════

_session: Optional[aiohttp.ClientSession] = None


async def _get_session() -> aiohttp.ClientSession:
    """Get or create aiohttp session."""
    global _session
    if _session is None or _session.closed:
        _session = aiohttp.ClientSession()
    return _session


async def _bot_api_post(method: str, data: dict, max_retries: int = 3) -> Optional[dict]:
    """Make a POST request to Telegram Bot API with retries.
    
    Args:
        method: Bot API method name (e.g., 'sendMessage')
        data: Request payload
        max_retries: Maximum number of retry attempts
        
    Returns:
        Response dict if successful, None otherwise
    """
    url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/{method}"
    session = await _get_session()
    
    for attempt in range(1, max_retries + 1):
        try:
            async with session.post(url, json=data, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    if result.get("ok"):
                        return result.get("result")
                    else:
                        logger.warning(f"Bot API {method} returned ok=false: {result.get('description')}")
                        return None
                else:
                    logger.warning(f"Bot API {method} attempt {attempt} failed: HTTP {resp.status}")
        except asyncio.TimeoutError:
            logger.warning(f"Bot API {method} attempt {attempt} timed out")
        except Exception as e:
            logger.warning(f"Bot API {method} attempt {attempt} error: {e}")
        
        if attempt < max_retries:
            await asyncio.sleep(0.5 * attempt)
    
    logger.error(f"Bot API {method} failed after {max_retries} retries")
    return None


async def send_message_colored(chat_id: Union[int, str], text: str, reply_markup: List[List[dict]], 
                               parse_mode: str = "HTML", disable_web_page_preview: bool = False) -> Optional[dict]:
    """Send message with colored buttons via Bot API.
    
    Returns:
        Message dict if successful, None if failed (caller should use Pyrogram fallback)
    """
    inline_keyboard = []
    for row in reply_markup:
        kb_row = []
        for btn in row:
            btn_data = {"text": btn["text"]}
            if "callback_data" in btn:
                btn_data["callback_data"] = btn["callback_data"]
            if "url" in btn:
                btn_data["url"] = btn["url"]
            if "style" in btn:
                btn_data["style"] = btn["style"]
            kb_row.append(btn_data)
        inline_keyboard.append(kb_row)
    
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": disable_web_page_preview,
        "reply_markup": {"inline_keyboard": inline_keyboard}
    }
    
    return await _bot_api_post("sendMessage", data)


async def send_photo_colored(chat_id: Union[int, str], photo: str, caption: str = None,
                             reply_markup: List[List[dict]] = None, parse_mode: str = "HTML") -> Optional[dict]:
    """Send photo with colored buttons via Bot API.
    
    Returns:
        Message dict if successful, None if failed (caller should use Pyrogram fallback)
    """
    data = {
        "chat_id": chat_id,
        "photo": photo,
        "parse_mode": parse_mode,
    }
    
    if caption:
        data["caption"] = caption
    
    if reply_markup:
        inline_keyboard = []
        for row in reply_markup:
            kb_row = []
            for btn in row:
                btn_data = {"text": btn["text"]}
                if "callback_data" in btn:
                    btn_data["callback_data"] = btn["callback_data"]
                if "url" in btn:
                    btn_data["url"] = btn["url"]
                if "style" in btn:
                    btn_data["style"] = btn["style"]
                kb_row.append(btn_data)
            inline_keyboard.append(kb_row)
        data["reply_markup"] = {"inline_keyboard": inline_keyboard}
    
    return await _bot_api_post("sendPhoto", data)


async def edit_message_text_colored(chat_id: Union[int, str], message_id: int, text: str,
                                    reply_markup: List[List[dict]] = None, parse_mode: str = "HTML",
                                    disable_web_page_preview: bool = False) -> Optional[dict]:
    """Edit message text with colored buttons via Bot API.
    
    Returns:
        Message dict if successful, None if failed (caller should use Pyrogram fallback)
    """
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": disable_web_page_preview,
    }
    
    if reply_markup:
        inline_keyboard = []
        for row in reply_markup:
            kb_row = []
            for btn in row:
                btn_data = {"text": btn["text"]}
                if "callback_data" in btn:
                    btn_data["callback_data"] = btn["callback_data"]
                if "url" in btn:
                    btn_data["url"] = btn["url"]
                if "style" in btn:
                    btn_data["style"] = btn["style"]
                kb_row.append(btn_data)
            inline_keyboard.append(kb_row)
        data["reply_markup"] = {"inline_keyboard": inline_keyboard}
    
    return await _bot_api_post("editMessageText", data)


async def edit_message_caption_colored(chat_id: Union[int, str], message_id: int, caption: str,
                                       reply_markup: List[List[dict]] = None, parse_mode: str = "HTML") -> Optional[dict]:
    """Edit message caption with colored buttons via Bot API.
    
    Returns:
        Message dict if successful, None if failed (caller should use Pyrogram fallback)
    """
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "caption": caption,
        "parse_mode": parse_mode,
    }
    
    if reply_markup:
        inline_keyboard = []
        for row in reply_markup:
            kb_row = []
            for btn in row:
                btn_data = {"text": btn["text"]}
                if "callback_data" in btn:
                    btn_data["callback_data"] = btn["callback_data"]
                if "url" in btn:
                    btn_data["url"] = btn["url"]
                if "style" in btn:
                    btn_data["style"] = btn["style"]
                kb_row.append(btn_data)
            inline_keyboard.append(kb_row)
        data["reply_markup"] = {"inline_keyboard": inline_keyboard}
    
    return await _bot_api_post("editMessageCaption", data)


async def edit_reply_markup_colored(chat_id: Union[int, str], message_id: int,
                                   reply_markup: List[List[dict]]) -> Optional[dict]:
    """Edit message reply markup (buttons only) with colored buttons via Bot API.
    
    Returns:
        Message dict if successful, None if failed (caller should use Pyrogram fallback)
    """
    inline_keyboard = []
    for row in reply_markup:
        kb_row = []
        for btn in row:
            btn_data = {"text": btn["text"]}
            if "callback_data" in btn:
                btn_data["callback_data"] = btn["callback_data"]
            if "url" in btn:
                btn_data["url"] = btn["url"]
            if "style" in btn:
                btn_data["style"] = btn["style"]
            kb_row.append(btn_data)
        inline_keyboard.append(kb_row)
    
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reply_markup": {"inline_keyboard": inline_keyboard}
    }
    
    return await _bot_api_post("editMessageReplyMarkup", data)


async def edit_message_media_colored(chat_id: Union[int, str], message_id: int, media: dict,
                                     reply_markup: List[List[dict]] = None) -> Optional[dict]:
    """Edit message media with colored buttons via Bot API.
    
    Returns:
        Message dict if successful, None if failed (caller should use Pyrogram fallback)
    """
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "media": media,
    }
    
    if reply_markup:
        inline_keyboard = []
        for row in reply_markup:
            kb_row = []
            for btn in row:
                btn_data = {"text": btn["text"]}
                if "callback_data" in btn:
                    btn_data["callback_data"] = btn["callback_data"]
                if "url" in btn:
                    btn_data["url"] = btn["url"]
                if "style" in btn:
                    btn_data["style"] = btn["style"]
                kb_row.append(btn_data)
            inline_keyboard.append(kb_row)
        data["reply_markup"] = {"inline_keyboard": inline_keyboard}
    
    return await _bot_api_post("editMessageMedia", data)


# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
