from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from VISHALMUSIC import app
from VISHALMUSIC.utils.autoplay_utils import toggle_autoplay
from VISHALMUSIC.utils.decorators import ActualAdminCB
from strings import get_string
from VISHALMUSIC.utils.database import get_lang


def _rebuild_markup(original_markup, chat_id: int, new_status: bool, _):
    if not original_markup or not original_markup.inline_keyboard:
        return original_markup
    new_keyboard = []
    for row in original_markup.inline_keyboard:
        new_row = []
        for btn in row:
            if btn.callback_data and btn.callback_data.startswith("AUTOPLAY_TOGGLE"):
                label = _["autoplay_1"] if new_status else _["autoplay_2"]
                new_row.append(
                    InlineKeyboardButton(
                        text=label,
                        callback_data=f"AUTOPLAY_TOGGLE {chat_id}",
                    )
                )
            else:
                new_row.append(btn)
        new_keyboard.append(new_row)
    return InlineKeyboardMarkup(new_keyboard)


@app.on_callback_query(filters.regex(r"^AUTOPLAY_TOGGLE (.+)$"))
@ActualAdminCB
async def autoplay_toggle_callback(client, callback: CallbackQuery, _):
    try:
        chat_id = int(callback.matches[0].group(1))
    except (IndexError, ValueError):
        return await callback.answer(_["autoplay_5"], show_alert=True)

    new_status = await toggle_autoplay(chat_id)

    if new_status:
        alert_text = _["autoplay_3"]
    else:
        alert_text = _["autoplay_4"]

    try:
        updated_markup = _rebuild_markup(callback.message.reply_markup, chat_id, new_status, _)
        await callback.message.edit_reply_markup(updated_markup)
    except Exception:
        pass

    await callback.answer(alert_text, show_alert=True)
