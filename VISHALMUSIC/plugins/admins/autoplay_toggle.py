from pyrogram import filters
from pyrogram.types import CallbackQuery

from VISHALMUSIC import app
from VISHALMUSIC.utils.stream.autoplay import toggle_autoplay
from VISHALMUSIC.utils.decorators import ActualAdminCB
from VISHALMUSIC.utils.colored_buttons import styled_button, edit_reply_markup_colored
from strings import get_string
from VISHALMUSIC.utils.database import get_lang


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

    label = _["autoplay_1"] if new_status else _["autoplay_2"]
    style = "success" if new_status else "danger"
    toggle_btn = styled_button(label, callback_data=f"AUTOPLAY_TOGGLE {chat_id}", style=style)

    try:
        close_btn = styled_button(_["CLOSE_BUTTON"], callback_data="close", style="danger")
        control_row = [
            styled_button("▷", callback_data=f"ADMIN Resume|{chat_id}", style="success"),
            styled_button("II", callback_data=f"ADMIN Pause|{chat_id}", style="primary"),
            styled_button("↻", callback_data=f"ADMIN Replay|{chat_id}", style="primary"),
            styled_button("‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style="primary"),
            styled_button("▢", callback_data=f"ADMIN Stop|{chat_id}", style="danger"),
        ]
        new_markup = [control_row, [toggle_btn], [close_btn]]
        await edit_reply_markup_colored(callback.message.chat.id, callback.message.id, reply_markup=new_markup)
    except Exception:
        pass

    await callback.answer(alert_text, show_alert=True)
