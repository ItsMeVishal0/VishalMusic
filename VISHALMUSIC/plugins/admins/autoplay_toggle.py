from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from VISHALMUSIC import app
from VISHALMUSIC.utils.autoplay_utils import toggle_autoplay
from VISHALMUSIC.utils.decorators import ActualAdminCB


def _rebuild_markup(original_markup, chat_id: int, new_status: bool):
    if not original_markup or not original_markup.inline_keyboard:
        return original_markup
    new_keyboard = []
    for row in original_markup.inline_keyboard:
        new_row = []
        for btn in row:
            if btn.callback_data and btn.callback_data.startswith("AUTOPLAY_TOGGLE"):
                label = "🔁 ᴀᴜᴛᴏᴘʟᴀʏ : ᴏɴ ✅" if new_status else "🔁 ᴀᴜᴛᴏᴘʟᴀʏ : ᴏғғ ❌"
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
        return await callback.answer("ᴇʀʀᴏʀ: ɪɴᴠᴀʟɪᴅ ᴄʜᴀᴛ.", show_alert=True)

    new_status = await toggle_autoplay(chat_id)

    if new_status:
        alert_text = "🔁 ᴀᴜᴛᴏᴘʟᴀʏ : ᴏɴ ✅\n\nNext song will play automatically!"
    else:
        alert_text = "🔁 ᴀᴜᴛᴏᴘʟᴀʏ : ᴏғғ ❌\n\nAutoplay disabled."

    try:
        updated_markup = _rebuild_markup(callback.message.reply_markup, chat_id, new_status)
        await callback.message.edit_reply_markup(updated_markup)
    except Exception:
        pass

    await callback.answer(alert_text, show_alert=True)
