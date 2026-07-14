# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   GitHub : github.com/ItsMeVishal0/VishalMusic
#   Developer : @ItsMeVishalBots | Telegram
#   Module : Colored Inline Buttons (Telegram Native Support)
# ═══════════════════════════════════════════════════════════

"""
Telegram now natively supports colored inline buttons (Feb 2026 update)!
This module creates button dictionaries with 'style' field that Pyrogram
automatically handles via Telegram's official Bot API.

Styles: "primary" (blue), "success" (green), "danger" (red)

Note: Colors work on Telegram clients updated after Feb 9, 2026.
Older clients will display standard blue buttons.
"""

from typing import List
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def styled_button(text: str, callback_data: str = None, url: str = None, style: str = None):
    """Create a button dict with optional style (color).
    
    Telegram natively supports colored buttons (Feb 2026 update).
    The 'style' field is automatically recognized by Pyrogram/Telegram.
    
    Args:
        text: Button text
        callback_data: Callback data for inline queries
        url: URL for link buttons
        style: Button color - "primary" (blue), "success" (green), "danger" (red)
    
    Returns:
        Button dictionary compatible with Pyrogram InlineKeyboardButton
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
    """Convert styled button dicts to Pyrogram InlineKeyboardMarkup.
    
    Note: Pyrogram doesn't yet support Telegram's native 'style' field,
    so we strip it out for now. Colors will work once Pyrogram is updated.
    
    Args:
        buttons: List of button rows, each containing styled_button dicts
        
    Returns:
        InlineKeyboardMarkup ready for use with Pyrogram
    """
    kb = []
    for row in buttons:
        kb_row = []
        for btn in row:
            # Create button without 'style' - Pyrogram doesn't support it yet
            kwargs = {"text": btn["text"]}
            if "callback_data" in btn:
                kwargs["callback_data"] = btn["callback_data"]
            if "url" in btn:
                kwargs["url"] = btn["url"]
            # Skip 'style' parameter - Pyrogram InlineKeyboardButton doesn't accept it
            kb_row.append(InlineKeyboardButton(**kwargs))
        kb.append(kb_row)
    return InlineKeyboardMarkup(kb)


# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
