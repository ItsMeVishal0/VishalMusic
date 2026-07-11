import re
from typing import Union

from pyrogram import Client, filters, types
from pyrogram.types import Message

from VISHALMUSIC import app
from VISHALMUSIC.utils.database import get_lang
from VISHALMUSIC.utils.decorators.language import LanguageStart, languageCB
from VISHALMUSIC.utils.inline.help import (
    action_sub_menu,
    first_page,
    help_back_markup,
    private_help_panel,
    second_page,
)
from VISHALMUSIC.utils.inline.start import private_panel
from VISHALMUSIC.utils.colored_buttons import send_photo_colored, edit_message_caption_colored, edit_message_text_colored, send_message_colored
from config import BANNED_USERS, HELP_IMG_URL, SUPPORT_CHAT
from strings import get_string, helpers

# ────────────────────────────────────────────────  /help entrypoints ──

@app.on_message(filters.command(["help"]) & filters.private & ~BANNED_USERS)
@app.on_callback_query(filters.regex("open_help") & ~BANNED_USERS)
@LanguageStart
async def helper_private(client: Client, update: Union[Message, types.CallbackQuery], _):
    is_cb = isinstance(update, types.CallbackQuery)
    language = await get_lang(update.from_user.id)
    _ = get_string(language)

    keyboard = first_page(_)
    caption = _["help_1"].format(SUPPORT_CHAT)

    if is_cb:
        await update.answer()
        await edit_message_caption_colored(update.message.chat.id, update.message.id, caption, reply_markup=keyboard)
    else:
        await update.delete()
        await send_photo_colored(
            chat_id=update.chat.id,
            photo=HELP_IMG_URL,
            caption=caption,
            reply_markup=keyboard,
        )

# ────────────────────────────────────────────────  group /help notice ─

@app.on_message(filters.command(["help"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def help_com_group(client: Client, message: Message, _):
    keyboard = private_help_panel(_)
    await send_message_colored(
        message.chat.id,
        _["help_2"],
        reply_markup=keyboard,
        disable_web_page_preview=True,
    )

# ────────────────────────────────────────────────  main help buttons ──

@app.on_callback_query(filters.regex(r"help_callback hb(\d+)_p(\d+)") & ~BANNED_USERS)
@languageCB
async def helper_cb(client: Client, CallbackQuery: types.CallbackQuery, _):
    match = re.match(r"help_callback hb(\d+)_p(\d+)", CallbackQuery.data)
    if not match:
        return await CallbackQuery.answer("Invalid callback.", show_alert=True)

    number = int(match.group(1))
    current_page = int(match.group(2))

    #── Action (1) gets its own sub-menu
    if number == 1:
        await edit_message_text_colored(
            CallbackQuery.message.chat.id, CallbackQuery.message.id,
            _["S_B_M"],
            reply_markup=action_sub_menu(_, current_page),
            disable_web_page_preview=True,
        )
        return

    #── All other categories
    help_text = getattr(helpers, f"HELP_{number}", None)
    if not help_text:
        return await CallbackQuery.answer("Invalid help topic.", show_alert=True)

    await edit_message_text_colored(CallbackQuery.message.chat.id, CallbackQuery.message.id, 
        help_text,
        reply_markup=help_back_markup(_, current_page),
        disable_web_page_preview=True
    )

# ─────────────────────────────────────────  pagination callbacks ─────

@app.on_callback_query(filters.regex(r"help_next_(\d+)") & ~BANNED_USERS)
@languageCB
async def help_next_cb(client: Client, CallbackQuery: types.CallbackQuery, _):
    if CallbackQuery.data == "help_next_2":
        await edit_message_text_colored(CallbackQuery.message.chat.id, CallbackQuery.message.id, 
            _["help_1"].format(SUPPORT_CHAT),
            reply_markup=second_page(_),
            disable_web_page_preview=True
        )
    else:
        await CallbackQuery.answer("No more pages.", show_alert=True)

@app.on_callback_query(filters.regex(r"help_prev_(\d+)") & ~BANNED_USERS)
@languageCB
async def help_prev_cb(client: Client, CallbackQuery: types.CallbackQuery, _):
    if CallbackQuery.data == "help_prev_1":
        await edit_message_text_colored(CallbackQuery.message.chat.id, CallbackQuery.message.id, 
            _["help_1"].format(SUPPORT_CHAT),
            reply_markup=first_page(_),
            disable_web_page_preview=True
        )
    else:
        await CallbackQuery.answer("No previous page.", show_alert=True)

@app.on_callback_query(filters.regex(r"help_back_(\d+)") & ~BANNED_USERS)
@languageCB
async def help_back_cb(client: Client, CallbackQuery: types.CallbackQuery, _):
    page = CallbackQuery.data.split("_")[-1]
    if page == "1":
        keyboard = first_page(_)
    elif page == "2":
        keyboard = second_page(_)
    else:
        return await CallbackQuery.answer("Invalid page.", show_alert=True)

    await edit_message_text_colored(CallbackQuery.message.chat.id, CallbackQuery.message.id, 
        _["help_1"].format(SUPPORT_CHAT),
        reply_markup=keyboard,
        disable_web_page_preview=True
    )

# ────────────────────────────────────────  sub-topic buttons (Action) ─

@app.on_callback_query(filters.regex("action_prom_1") & ~BANNED_USERS)
@languageCB
async def action_prom_cb(client: Client, CallbackQuery: types.CallbackQuery, _):
    await edit_message_text_colored(CallbackQuery.message.chat.id, CallbackQuery.message.id, 
        helpers.HELP_1_PROMO,
        reply_markup=help_back_markup(_, 1),
        disable_web_page_preview=True
    )

@app.on_callback_query(filters.regex("action_pun_1") & ~BANNED_USERS)
@languageCB
async def action_pun_cb(client: Client, CallbackQuery: types.CallbackQuery, _):
    await edit_message_text_colored(CallbackQuery.message.chat.id, CallbackQuery.message.id, 
        helpers.HELP_1_PUNISH,
        reply_markup=help_back_markup(_, 1),
        disable_web_page_preview=True
    )

# ────────────────────────────────────────────────  back to start panel ─

@app.on_callback_query(filters.regex("back_to_main") & ~BANNED_USERS)
@languageCB
async def back_to_main_cb(client: Client, CallbackQuery: types.CallbackQuery, _):
    out = private_panel(_)
    await edit_message_caption_colored(
        CallbackQuery.message.chat.id, CallbackQuery.message.id,
        _["start_2"].format(
            CallbackQuery.from_user.mention, app.mention
        ),
        reply_markup=out,
    )
