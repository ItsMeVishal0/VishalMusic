# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   GitHub : github.com/ItsMeVishal0/VishalMusic
#   Developer : @ItsMeVishalBots | Telegram
#   Module : Multi-Language Selection & Settings
# ═══════════════════════════════════════════════════════════

import asyncio
from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import (
    Message,
    CallbackQuery,
)

from VISHALMUSIC import app
from VISHALMUSIC.utils.colored_buttons import styled_button, buttons_to_inline_markup
from VISHALMUSIC.utils.database import get_lang, set_lang
from VISHALMUSIC.utils.decorators import ActualAdminCB, language, languageCB
from config import BANNED_USERS
from strings import get_string, languages_present


def languages_keyboard(_):
    rows = []
    row = []

    # Priority languages first
    priority = ["en", "hi", "cg"]
    ordered_codes = priority + [c for c in languages_present if c not in priority]

    for idx, code in enumerate(ordered_codes):
        if code not in languages_present:
            continue
            row.append(
            styled_button(
                text=languages_present[code],
                callback_data=f"languages:{code}",
                style="primary",
            )
        )
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    rows.append(
        [
            styled_button(text=_["BACK_BUTTON"], callback_data="settingsback_helper", style="primary"),
            styled_button(text=_["CLOSE_BUTTON"], callback_data="close", style="danger"),
        ]
    )

    return rows


@app.on_message(filters.command(["lang", "setlang", "language"]) & ~BANNED_USERS)
@language
async def langs_command(client, message: Message, _):
    keyboard = languages_keyboard(_)
    try:
        await send_message_colored(chat_id=message.chat.id, text=_["lang_1"], reply_markup=keyboard)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await send_message_colored(chat_id=message.chat.id, text=_["lang_1"], reply_markup=keyboard)


@app.on_callback_query(filters.regex("LG") & ~BANNED_USERS)
@languageCB
async def languagecb(client, CallbackQuery: CallbackQuery, _):
    try:
        await CallbackQuery.answer()
    except:
        pass
    keyboard = languages_keyboard(_)
    try:
        await edit_reply_markup_colored(chat_id=CallbackQuery.message.chat.id, message_id=CallbackQuery.message.id, reply_markup=keyboard)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await edit_reply_markup_colored(chat_id=CallbackQuery.message.chat.id, message_id=CallbackQuery.message.id, reply_markup=keyboard)


@app.on_callback_query(filters.regex(r"languages:(.*?)") & ~BANNED_USERS)
@ActualAdminCB
async def language_markup(client, CallbackQuery: CallbackQuery, _):
    lang_code = CallbackQuery.data.split(":")[1]
    old_lang = await get_lang(CallbackQuery.message.chat.id)
    if str(old_lang) == str(lang_code):
        return await CallbackQuery.answer(_["lang_4"], show_alert=True)

    try:
        _ = get_string(lang_code)
        await CallbackQuery.answer(_["lang_2"], show_alert=True)
    except:
        _ = get_string(old_lang)
        return await CallbackQuery.answer(_["lang_3"], show_alert=True)

    await set_lang(CallbackQuery.message.chat.id, lang_code)
    keyboard = languages_keyboard(_)
    try:
        await edit_reply_markup_colored(chat_id=CallbackQuery.message.chat.id, message_id=CallbackQuery.message.id, reply_markup=keyboard)
    except FloodWait as e:
        await asyncio.sleep(e.value)
        await edit_reply_markup_colored(chat_id=CallbackQuery.message.chat.id, message_id=CallbackQuery.message.id, reply_markup=keyboard)

# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
