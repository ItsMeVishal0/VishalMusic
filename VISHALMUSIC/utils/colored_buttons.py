# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   GitHub : github.com/ItsMeVishal0/VishalMusic
#   Developer : @ItsMeVishalBots | Telegram
#   Module : Colored Inline Buttons (Telegram Bot API Direct)
# ═══════════════════════════════════════════════════════════

"""
Telegram Bot API 9.4+ Colored Buttons Implementation
────────────────────────────────────────────────────

Since February 9, 2026, Telegram supports colored inline buttons via Bot API.
This module implements colored buttons using direct HTTP calls to Bot API.

Supported Styles:
  • "primary" - Blue (recommended for main actions)
  • "success" - Green (recommended for positive actions)  
  • "danger"  - Red (recommended for destructive actions)
  • None      - Default app-specific style

Note: Pyrogram doesn't support 'style' parameter yet, so we use direct Bot API calls.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Union

import aiohttp
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import config

logger = logging.getLogger(__name__)

# Global session for connection pooling
_session: Optional[aiohttp.ClientSession] = None


# ═══════════════════════════════════════════════════════════
#  HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════

def styled_button(
    text: str,
    callback_data: str = None,
    url: str = None,
    style: str = None
) -> Dict[str, str]:
    """Create a button dictionary with optional style.
    
    Args:
        text: Button label text
        callback_data: Data to send in callback query (1-64 bytes)
        url: HTTP/tg:// URL to open when pressed
        style: Color style - "primary" (blue), "success" (green), "danger" (red)
    
    Returns:
        Button dictionary compatible with Bot API and our helper functions
    
    Example:
        >>> styled_button("Click Me", callback_data="btn_clicked", style="primary")
        {'text': 'Click Me', 'callback_data': 'btn_clicked', 'style': 'primary'}
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
    """Convert button dicts to Pyrogram InlineKeyboardMarkup (WITHOUT colors).
    
    This is the FALLBACK function for when Bot API calls fail.
    It creates standard Pyrogram buttons without colored styles.
    
    Args:
        buttons: 2D list of button dictionaries from styled_button()
        
    Returns:
        InlineKeyboardMarkup for use with Pyrogram methods
        
    Example:
        >>> buttons = [[styled_button("Test", callback_data="test", style="primary")]]
        >>> markup = buttons_to_inline_markup(buttons)
        >>> await message.reply_text("Hello", reply_markup=markup)
    """
    keyboard = []
    
    for row in buttons:
        button_row = []
        for btn_dict in row:
            # Create Pyrogram button (ignore 'style' - not supported)
            kwargs = {"text": btn_dict["text"]}
            
            if "callback_data" in btn_dict:
                kwargs["callback_data"] = btn_dict["callback_data"]
            if "url" in btn_dict:
                kwargs["url"] = btn_dict["url"]
            
            button_row.append(InlineKeyboardButton(**kwargs))
        
        keyboard.append(button_row)
    
    return InlineKeyboardMarkup(keyboard)


async def _get_session() -> aiohttp.ClientSession:
    """Get or create aiohttp session for Bot API calls."""
    global _session
    
    if _session is None or _session.closed:
        _session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10),
            connector=aiohttp.TCPConnector(limit=100, limit_per_host=30)
        )
    
    return _session


def _build_inline_keyboard(buttons: List[List[Dict]]) -> List[List[Dict]]:
    """Build inline_keyboard array for Bot API with style support.
    
    Args:
        buttons: 2D list of button dicts from styled_button()
        
    Returns:
        Bot API compatible inline_keyboard array
    """
    inline_keyboard = []
    
    for row in buttons:
        button_row = []
        for btn_dict in row:
            # Copy button dict and include 'style' if present
            api_button = {"text": btn_dict["text"]}
            
            if "callback_data" in btn_dict:
                api_button["callback_data"] = btn_dict["callback_data"]
            if "url" in btn_dict:
                api_button["url"] = btn_dict["url"]
            if "style" in btn_dict:
                api_button["style"] = btn_dict["style"]  # ← Color magic happens here!
            
            button_row.append(api_button)
        
        inline_keyboard.append(button_row)
    
    return inline_keyboard


async def _bot_api_call(method: str, data: Dict) -> Optional[Dict]:
    """Make POST request to Telegram Bot API.
    
    Args:
        method: Bot API method name (e.g., 'sendMessage', 'editMessageText')
        data: Request payload
        
    Returns:
        Response dict if successful, None if failed
    """
    url = f"https://api.telegram.org/bot{config.BOT_TOKEN}/{method}"
    session = await _get_session()
    
    try:
        async with session.post(url, json=data) as response:
            if response.status == 200:
                result = await response.json()
                if result.get("ok"):
                    return result.get("result")
                else:
                    logger.debug(f"Bot API {method} returned ok=false: {result.get('description')}")
            else:
                logger.debug(f"Bot API {method} failed: HTTP {response.status}")
    
    except asyncio.TimeoutError:
        logger.debug(f"Bot API {method} timeout")
    except Exception as e:
        logger.debug(f"Bot API {method} error: {e}")
    
    return None


# ═══════════════════════════════════════════════════════════
#  PUBLIC COLORED BUTTON FUNCTIONS
# ═══════════════════════════════════════════════════════════

async def send_message_colored(
    chat_id: Union[int, str],
    text: str,
    reply_markup: List[List[Dict]],
    parse_mode: str = "HTML",
    disable_web_page_preview: bool = False
) -> Optional[Dict]:
    """Send message with colored buttons via Bot API.
    
    Args:
        chat_id: Target chat ID
        text: Message text
        reply_markup: 2D list of button dicts from styled_button()
        parse_mode: Text parse mode (HTML/Markdown)
        disable_web_page_preview: Disable link previews
        
    Returns:
        Message dict if successful, None if failed (use Pyrogram fallback)
        
    Example:
        >>> buttons = [[
        ...     styled_button("✅ Confirm", callback_data="confirm", style="success"),
        ...     styled_button("❌ Cancel", callback_data="cancel", style="danger")
        ... ]]
        >>> result = await send_message_colored(chat_id, "Choose:", buttons)
        >>> if not result:
        ...     await message.reply_text("Choose:", reply_markup=buttons_to_inline_markup(buttons))
    """
    data = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": disable_web_page_preview,
        "reply_markup": {"inline_keyboard": _build_inline_keyboard(reply_markup)}
    }
    
    return await _bot_api_call("sendMessage", data)


async def send_photo_colored(
    chat_id: Union[int, str],
    photo: str,
    caption: str = None,
    reply_markup: List[List[Dict]] = None,
    parse_mode: str = "HTML"
) -> Optional[Dict]:
    """Send photo with colored buttons via Bot API.
    
    Args:
        chat_id: Target chat ID
        photo: Photo file_id or HTTP URL
        caption: Photo caption
        reply_markup: 2D list of button dicts from styled_button()
        parse_mode: Caption parse mode
        
    Returns:
        Message dict if successful, None if failed (use Pyrogram fallback)
    """
    data = {
        "chat_id": chat_id,
        "photo": photo,
        "parse_mode": parse_mode
    }
    
    if caption:
        data["caption"] = caption
    
    if reply_markup:
        data["reply_markup"] = {"inline_keyboard": _build_inline_keyboard(reply_markup)}
    
    return await _bot_api_call("sendPhoto", data)


async def edit_message_text_colored(
    chat_id: Union[int, str],
    message_id: int,
    text: str,
    reply_markup: List[List[Dict]] = None,
    parse_mode: str = "HTML",
    disable_web_page_preview: bool = False
) -> Optional[Dict]:
    """Edit message text with colored buttons via Bot API.
    
    Args:
        chat_id: Target chat ID
        message_id: Message ID to edit
        text: New text
        reply_markup: 2D list of button dicts from styled_button()
        parse_mode: Text parse mode
        disable_web_page_preview: Disable link previews
        
    Returns:
        Message dict if successful, None if failed (use Pyrogram fallback)
    """
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": disable_web_page_preview
    }
    
    if reply_markup:
        data["reply_markup"] = {"inline_keyboard": _build_inline_keyboard(reply_markup)}
    
    return await _bot_api_call("editMessageText", data)


async def edit_message_caption_colored(
    chat_id: Union[int, str],
    message_id: int,
    caption: str,
    reply_markup: List[List[Dict]] = None,
    parse_mode: str = "HTML"
) -> Optional[Dict]:
    """Edit message caption with colored buttons via Bot API.
    
    Args:
        chat_id: Target chat ID
        message_id: Message ID to edit
        caption: New caption
        reply_markup: 2D list of button dicts from styled_button()
        parse_mode: Caption parse mode
        
    Returns:
        Message dict if successful, None if failed (use Pyrogram fallback)
    """
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "caption": caption,
        "parse_mode": parse_mode
    }
    
    if reply_markup:
        data["reply_markup"] = {"inline_keyboard": _build_inline_keyboard(reply_markup)}
    
    return await _bot_api_call("editMessageCaption", data)


async def edit_reply_markup_colored(
    chat_id: Union[int, str],
    message_id: int,
    reply_markup: List[List[Dict]]
) -> Optional[Dict]:
    """Edit only message buttons (reply markup) via Bot API.
    
    Args:
        chat_id: Target chat ID
        message_id: Message ID to edit
        reply_markup: 2D list of button dicts from styled_button()
        
    Returns:
        Message dict if successful, None if failed (use Pyrogram fallback)
    """
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "reply_markup": {"inline_keyboard": _build_inline_keyboard(reply_markup)}
    }
    
    return await _bot_api_call("editMessageReplyMarkup", data)


async def edit_message_media_colored(
    chat_id: Union[int, str],
    message_id: int,
    media: Dict,
    reply_markup: List[List[Dict]] = None
) -> Optional[Dict]:
    """Edit message media with colored buttons via Bot API.
    
    Args:
        chat_id: Target chat ID
        message_id: Message ID to edit
        media: Media object (e.g., {"type": "photo", "media": "file_id"})
        reply_markup: 2D list of button dicts from styled_button()
        
    Returns:
        Message dict if successful, None if failed (use Pyrogram fallback)
    """
    data = {
        "chat_id": chat_id,
        "message_id": message_id,
        "media": media
    }
    
    if reply_markup:
        data["reply_markup"] = {"inline_keyboard": _build_inline_keyboard(reply_markup)}
    
    return await _bot_api_call("editMessageMedia", data)


# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
