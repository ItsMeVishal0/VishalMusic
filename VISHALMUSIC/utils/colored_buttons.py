# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   GitHub : github.com/ItsMeVishal0/VishalMusic
#   Developer : @ItsMeVishalBots | Telegram
#   Module : Colored Inline Buttons (Bot API 9.4+)
# ═══════════════════════════════════════════════════════════

"""
⚠️ CRITICAL: Telegram colored buttons require 2 things:
   1. Telegram client updated AFTER February 9, 2026
   2. Bot API HTTP calls (Kurigram/Pyrogram don't support 'style' field)

This module bypasses Kurigram and sends buttons directly via Telegram Bot API HTTP.

Supported Styles:
  • "primary" - Blue (main actions)
  • "success" - Green (positive actions like confirm)
  • "danger"  - Red (destructive actions like delete)
  • None - Default button color

Example Usage:
    buttons = [[
        styled_button("✅ Yes", callback_data="yes", style="success"),
        styled_button("❌ No", callback_data="no", style="danger")
    ]]
    
    # Try Bot API first (with colors)
    result = await send_message_colored(chat_id, "Choose:", buttons)
    
    # Fallback to Kurigram if Bot API fails (no colors)
    if not result:
        await message.reply_text("Choose:", reply_markup=buttons_to_inline_markup(buttons))
"""

import asyncio
import json
import logging
from typing import Dict, List, Optional, Union

import aiohttp
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import config

logger = logging.getLogger(__name__)

# Telegram Bot API base URL
BOT_API_URL = f"https://api.telegram.org/bot{config.BOT_TOKEN or ''}"

# Global aiohttp session
_session: Optional[aiohttp.ClientSession] = None


# ═══════════════════════════════════════════════════════════
#  CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════

async def _get_session() -> aiohttp.ClientSession:
    """Get or create aiohttp session."""
    global _session
    
    if _session is None or _session.closed:
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        _session = aiohttp.ClientSession(timeout=timeout)
    
    return _session


async def _bot_api_call(method: str, payload: dict) -> Optional[dict]:
    """Make HTTP POST to Telegram Bot API.
    
    Args:
        method: API method (e.g., 'sendMessage')
        payload: JSON payload
        
    Returns:
        Response 'result' field if successful, None otherwise
    """
    if not config.BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not set! Colored buttons will NOT work.")
        return None
    
    url = f"{BOT_API_URL}/{method}"
    session = await _get_session()
    
    try:
        async with session.post(url, json=payload) as resp:
            data = await resp.json()
            
            if data.get("ok"):
                logger.debug(f"✅ Bot API {method} success")
                return data.get("result")
            else:
                error = data.get("description", "Unknown error")
                logger.warning(f"❌ Bot API {method} failed: {error}")
                return None
    
    except asyncio.TimeoutError:
        logger.error(f"⏱️ Bot API {method} timeout")
        return None
    except Exception as e:
        logger.error(f"💥 Bot API {method} exception: {e}")
        return None


def _build_inline_keyboard(buttons: List[List[Dict]]) -> List[List[Dict]]:
    """Convert styled button dicts to Bot API inline_keyboard format.
    
    This preserves the 'style' field which Kurigram doesn't support.
    """
    keyboard = []
    for row in buttons:
        button_row = []
        for btn in row:
            api_btn = {"text": btn["text"]}
            
            if "callback_data" in btn:
                api_btn["callback_data"] = btn["callback_data"]
            if "url" in btn:
                api_btn["url"] = btn["url"]
            if "style" in btn:
                # ⭐ THIS is the magic field for colored buttons!
                api_btn["style"] = btn["style"]
            
            button_row.append(api_btn)
        keyboard.append(button_row)
    
    return keyboard


# ═══════════════════════════════════════════════════════════
#  PUBLIC API - BUTTON CREATION
# ═══════════════════════════════════════════════════════════

def styled_button(
    text: str,
    callback_data: str = None,
    url: str = None,
    style: str = None
) -> Dict[str, str]:
    """Create a colored button dictionary.
    
    Args:
        text: Button label
        callback_data: Callback data (1-64 bytes)
        url: URL to open
        style: "primary" (blue) | "success" (green) | "danger" (red)
    
    Returns:
        Button dict with 'style' field
    """
    btn = {"text": text}
    
    if callback_data:
        btn["callback_data"] = callback_data
    if url:
        btn["url"] = url
    if style and style in ("primary", "success", "danger"):
        btn["style"] = style
    
    return btn


def buttons_to_inline_markup(buttons: List[List[Dict]]) -> InlineKeyboardMarkup:
    """Convert styled buttons to Kurigram InlineKeyboardMarkup (NO COLORS).
    
    Use as FALLBACK when Bot API fails. Buttons will work but WITHOUT colors.
    """
    keyboard = []
    for row in buttons:
        kb_row = []
        for btn in row:
            kwargs = {"text": btn["text"]}
            if "callback_data" in btn:
                kwargs["callback_data"] = btn["callback_data"]
            if "url" in btn:
                kwargs["url"] = btn["url"]
            kb_row.append(InlineKeyboardButton(**kwargs))
        keyboard.append(kb_row)
    
    return InlineKeyboardMarkup(keyboard)


# ═══════════════════════════════════════════════════════════
#  PUBLIC API - SEND/EDIT MESSAGES WITH COLORED BUTTONS
# ═══════════════════════════════════════════════════════════

async def send_message_colored(
    chat_id: Union[int, str],
    text: str,
    reply_markup: List[List[Dict]],
    parse_mode: str = "HTML",
    disable_web_page_preview: bool = False
) -> Optional[Dict]:
    """Send message with COLORED buttons via Bot API HTTP.
    
    Returns None if failed - use Kurigram fallback in that case.
    """
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": disable_web_page_preview,
        "reply_markup": {
            "inline_keyboard": _build_inline_keyboard(reply_markup)
        }
    }
    
    return await _bot_api_call("sendMessage", payload)


async def send_photo_colored(
    chat_id: Union[int, str],
    photo: str,
    caption: str = None,
    reply_markup: List[List[Dict]] = None,
    parse_mode: str = "HTML"
) -> Optional[Dict]:
    """Send photo with COLORED buttons via Bot API HTTP."""
    payload = {
        "chat_id": chat_id,
        "photo": photo,
        "parse_mode": parse_mode
    }
    
    if caption:
        payload["caption"] = caption
    
    if reply_markup:
        payload["reply_markup"] = {
            "inline_keyboard": _build_inline_keyboard(reply_markup)
        }
    
    return await _bot_api_call("sendPhoto", payload)


async def edit_message_text_colored(
    chat_id: Union[int, str],
    message_id: int,
    text: str,
    reply_markup: List[List[Dict]] = None,
    parse_mode: str = "HTML",
    disable_web_page_preview: bool = False
) -> Optional[Dict]:
    """Edit message text + buttons with COLORS via Bot API HTTP."""
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": disable_web_page_preview
    }
    
    if reply_markup:
        payload["reply_markup"] = {
            "inline_keyboard": _build_inline_keyboard(reply_markup)
        }
    
    return await _bot_api_call("editMessageText", payload)


async def edit_message_caption_colored(
    chat_id: Union[int, str],
    message_id: int,
    caption: str,
    reply_markup: List[List[Dict]] = None,
    parse_mode: str = "HTML"
) -> Optional[Dict]:
    """Edit message caption + buttons with COLORS via Bot API HTTP."""
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "caption": caption,
        "parse_mode": parse_mode
    }
    
    if reply_markup:
        payload["reply_markup"] = {
            "inline_keyboard": _build_inline_keyboard(reply_markup)
        }
    
    return await _bot_api_call("editMessageCaption", payload)


async def edit_reply_markup_colored(
    chat_id: Union[int, str],
    message_id: int,
    reply_markup: List[List[Dict]]
) -> Optional[Dict]:
    """Edit ONLY buttons (keeps colors persistent) via Bot API HTTP.
    
    ⭐ Use this in callback handlers to prevent color disappearing on button tap!
    """
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reply_markup": {
            "inline_keyboard": _build_inline_keyboard(reply_markup)
        }
    }
    
    return await _bot_api_call("editMessageReplyMarkup", payload)


async def edit_message_media_colored(
    chat_id: Union[int, str],
    message_id: int,
    media: Dict,
    reply_markup: List[List[Dict]] = None
) -> Optional[Dict]:
    """Edit message media + buttons with COLORS via Bot API HTTP."""
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "media": media
    }
    
    if reply_markup:
        payload["reply_markup"] = {
            "inline_keyboard": _build_inline_keyboard(reply_markup)
        }
    
    return await _bot_api_call("editMessageMedia", payload)


# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
