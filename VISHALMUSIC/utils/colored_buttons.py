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
        logger.warning("⚠️ BOT_TOKEN not set! Colored buttons will NOT work.")
        return None
    
    # Build URL dynamically to get fresh BOT_TOKEN
    url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/{method}"
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
    """Send photo with COLORED buttons via Bot API HTTP.
    
    Supports:
    - file_id (string starting with any non-http char)
    - HTTP URL (http:// or https://)
    - Local file path (uploads as multipart/form-data)
    """
    
    # Check if photo is URL or file_id
    is_url = photo.startswith("http://") or photo.startswith("https://")
    is_local_file = not is_url and ("/" in photo or "\\" in photo)
    
    if is_local_file:
        # Upload local file as multipart/form-data
        return await _send_photo_with_file(chat_id, photo, caption, reply_markup, parse_mode)
    else:
        # Use JSON for URL or file_id
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


async def _send_photo_with_file(
    chat_id: Union[int, str],
    file_path: str,
    caption: str = None,
    reply_markup: List[List[Dict]] = None,
    parse_mode: str = "HTML"
) -> Optional[Dict]:
    """Send photo by uploading local file with multipart/form-data."""
    import os
    
    if not os.path.exists(file_path):
        logger.error(f"❌ Photo file not found: {file_path}")
        return None
    
    if not config.BOT_TOKEN:
        logger.error("❌ BOT_TOKEN not set!")
        return None
    
    url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/sendPhoto"
    session = await _get_session()
    
    # Open file safely with `with` to prevent handle leak
    try:
        with open(file_path, "rb") as fh:
            file_bytes = fh.read()
    except Exception as e:
        logger.error(f"❌ Failed reading photo file {file_path}: {e}")
        return None
    
    try:
        # Build form data
        form = aiohttp.FormData()
        form.add_field("chat_id", str(chat_id))
        form.add_field(
            "photo",
            file_bytes,
            filename=os.path.basename(file_path),
            content_type="application/octet-stream",
        )
        
        if caption:
            form.add_field("caption", caption)
        
        # Try with parse_mode first
        if parse_mode:
            form.add_field("parse_mode", parse_mode)
        
        if reply_markup:
            import json as json_lib
            reply_markup_json = json_lib.dumps({
                "inline_keyboard": _build_inline_keyboard(reply_markup)
            })
            form.add_field("reply_markup", reply_markup_json)
        
        async with session.post(url, data=form) as resp:
            data = await resp.json()
            
            if data.get("ok"):
                logger.debug(f"✅ Bot API sendPhoto (file upload) success")
                return data.get("result")
            else:
                error = data.get("description", "Unknown error")
                
                # If parse error, retry without parse_mode
                if "can't parse entities" in error and parse_mode:
                    logger.warning(f"⚠️ HTML parse error, retrying without parse_mode")
                    return await _send_photo_with_file(chat_id, file_path, caption, reply_markup, parse_mode=None)
                
                logger.warning(f"❌ Bot API sendPhoto (file upload) failed: {error}")
                return None
    
    except asyncio.TimeoutError:
        logger.error(f"⏱️ Bot API sendPhoto timeout")
        return None
    except Exception as e:
        logger.error(f"💥 Bot API sendPhoto exception: {e}")
        return None


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
    caption: str = None,
    reply_markup: List[List[Dict]] = None,
    parse_mode: str = "HTML"
) -> Optional[Dict]:
    """Edit message caption + buttons with COLORS via Bot API HTTP."""
    payload = {
        "chat_id": chat_id,
        "message_id": message_id,
        "parse_mode": parse_mode
    }
    
    if caption:
        payload["caption"] = caption
    
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
#  SMART WRAPPERS — Bot API first (colors), Pyrogram fallback
#  ⭐ Use these EVERYWHERE. They guarantee delivery even if Bot API fails.
# ═══════════════════════════════════════════════════════════

async def smart_send_message(
    chat_id: Union[int, str],
    text: str,
    reply_markup: Optional[List[List[Dict]]] = None,
    parse_mode: str = "HTML",
    disable_web_page_preview: bool = False,
):
    """Send a message with colored buttons. Falls back to Pyrogram on failure."""
    from VISHALMUSIC import app
    from pyrogram import enums

    # Try Bot API first
    try:
        data = await send_message_colored(
            chat_id, text,
            reply_markup=reply_markup or [],
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
        )
        if data and data.get("message_id"):
            try:
                return await app.get_messages(chat_id, data["message_id"])
            except Exception:
                return data
    except Exception as e:
        logger.debug(f"smart_send_message Bot API path failed: {e}")

    # Pyrogram fallback (no colors but delivery guaranteed)
    return await app.send_message(
        chat_id=chat_id,
        text=text,
        parse_mode=enums.ParseMode.HTML if parse_mode == "HTML" else enums.ParseMode.MARKDOWN,
        disable_web_page_preview=disable_web_page_preview,
        reply_markup=buttons_to_inline_markup(reply_markup) if reply_markup else None,
    )


async def smart_send_photo(
    chat_id: Union[int, str],
    photo: str,
    caption: Optional[str] = None,
    reply_markup: Optional[List[List[Dict]]] = None,
    parse_mode: str = "HTML",
):
    """Send a photo with colored buttons. Falls back to Pyrogram on failure."""
    from VISHALMUSIC import app
    from pyrogram import enums

    try:
        data = await send_photo_colored(
            chat_id=chat_id,
            photo=photo,
            caption=caption,
            reply_markup=reply_markup or [],
            parse_mode=parse_mode,
        )
        if data and data.get("message_id"):
            try:
                return await app.get_messages(chat_id, data["message_id"])
            except Exception:
                return data
    except Exception as e:
        logger.debug(f"smart_send_photo Bot API path failed: {e}")

    return await app.send_photo(
        chat_id=chat_id,
        photo=photo,
        caption=caption,
        parse_mode=enums.ParseMode.HTML if parse_mode == "HTML" else enums.ParseMode.MARKDOWN,
        reply_markup=buttons_to_inline_markup(reply_markup) if reply_markup else None,
    )


async def smart_edit_message_text(
    chat_id: Union[int, str],
    message_id: int,
    text: str,
    reply_markup: Optional[List[List[Dict]]] = None,
    parse_mode: str = "HTML",
    disable_web_page_preview: bool = False,
):
    """Edit a text message with colored buttons. Falls back to Pyrogram on failure."""
    from VISHALMUSIC import app
    from pyrogram import enums

    try:
        data = await edit_message_text_colored(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
            disable_web_page_preview=disable_web_page_preview,
        )
        if data:
            return data
    except Exception as e:
        logger.debug(f"smart_edit_message_text Bot API path failed: {e}")

    try:
        return await app.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            parse_mode=enums.ParseMode.HTML if parse_mode == "HTML" else enums.ParseMode.MARKDOWN,
            disable_web_page_preview=disable_web_page_preview,
            reply_markup=buttons_to_inline_markup(reply_markup) if reply_markup else None,
        )
    except Exception as e:
        logger.warning(f"smart_edit_message_text both paths failed: {e}")
        return None


async def smart_edit_message_caption(
    chat_id: Union[int, str],
    message_id: int,
    caption: str,
    reply_markup: Optional[List[List[Dict]]] = None,
    parse_mode: str = "HTML",
):
    """Edit caption + buttons. Falls back to Pyrogram on failure."""
    from VISHALMUSIC import app
    from pyrogram import enums

    try:
        data = await edit_message_caption_colored(
            chat_id=chat_id,
            message_id=message_id,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
        )
        if data:
            return data
    except Exception as e:
        logger.debug(f"smart_edit_message_caption Bot API path failed: {e}")

    try:
        return await app.edit_message_caption(
            chat_id=chat_id,
            message_id=message_id,
            caption=caption,
            parse_mode=enums.ParseMode.HTML if parse_mode == "HTML" else enums.ParseMode.MARKDOWN,
            reply_markup=buttons_to_inline_markup(reply_markup) if reply_markup else None,
        )
    except Exception as e:
        logger.warning(f"smart_edit_message_caption both paths failed: {e}")
        return None


# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
