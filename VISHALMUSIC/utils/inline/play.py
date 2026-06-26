import time
from pyrogram.types import InlineKeyboardButton
from VISHALMUSIC.utils.formatters import time_to_seconds
from VISHALMUSIC.utils.colored_buttons import styled_button

LAST_UPDATE_TIME = {}


def track_markup(_, videoid, user_id, channel, fplay):
    return [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}"
            )
        ],
    ]


def should_update_progress(chat_id):
    now = time.time()
    last = LAST_UPDATE_TIME.get(chat_id, 0)
    if now - last >= 6:
        LAST_UPDATE_TIME[chat_id] = now
        return True
    return False


def generate_progress_bar(played_sec, duration_sec):
    if duration_sec == 0:
        percentage = 0
    else:
        percentage = min((played_sec / duration_sec) * 100, 100)

    bar_length = 8
    filled = int(round(bar_length * (percentage / 100)))
    remaining = bar_length - filled

    if filled > 0:
        if filled == bar_length:
            return "𓂃" * (filled - 1) + "ꨄ"
        else:
            return "𓂃" * (filled - 1) + "ꨄ" + "𓂃" * remaining
    else:
        return "ꨄ" + "𓂃" * remaining


def autoplay_button(chat_id: int, status: bool) -> InlineKeyboardButton:
    if status:
        label = "🔁 ᴀᴜᴛᴏᴘʟᴀʏ : ᴏɴ ✅"
    else:
        label = "🔁 ᴀᴜᴛᴏᴘʟᴀʏ : ᴏғғ ❌"
    return InlineKeyboardButton(
        text=label,
        callback_data=f"AUTOPLAY_TOGGLE {chat_id}",
    )


def control_buttons(_, chat_id):
    return [[
        InlineKeyboardButton(text="▷", callback_data=f"ADMIN Resume|{chat_id}"),
        InlineKeyboardButton(text="II", callback_data=f"ADMIN Pause|{chat_id}"),
        InlineKeyboardButton(text="↻", callback_data=f"ADMIN Replay|{chat_id}"),
        InlineKeyboardButton(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}"),
        InlineKeyboardButton(text="▢", callback_data=f"ADMIN Stop|{chat_id}"),
    ]]


def stream_markup_timer(_, chat_id, played, dur, autoplay_status: bool = False):
    if not should_update_progress(chat_id):
        return None

    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    bar = generate_progress_bar(played_sec, duration_sec)

    return (
        [[InlineKeyboardButton(text=f"{played} {bar} {dur}", callback_data="GetTimer")]]
        + control_buttons(_, chat_id)
        + [[autoplay_button(chat_id, autoplay_status)]]
        + [[InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close")]]
    )


def stream_markup(_, chat_id, autoplay_status: bool = False):
    return (
        control_buttons(_, chat_id)
        + [[autoplay_button(chat_id, autoplay_status)]]
        + [[InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close")]]
    )


def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"VishalPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}"
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"VishalPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}"
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}"
            ),
        ],
    ]
    return buttons


def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    return [
        [
            InlineKeyboardButton(
                text=_["P_B_3"],
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}",
            )
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}"
            )
        ],
    ]


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    short_query = query[:20]
    return [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="◁",
                callback_data=f"slider B|{query_type}|{short_query}|{user_id}|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {short_query}|{user_id}",
            ),
            InlineKeyboardButton(
                text="▷",
                callback_data=f"slider F|{query_type}|{short_query}|{user_id}|{channel}|{fplay}",
            ),
        ],
    ]


# ═══════════════════════════════════════════════════════════
#   COLORED BUTTON VARIANTS (Bot API HTTP - style support)
# ═══════════════════════════════════════════════════════════

def colored_control_buttons(_, chat_id):
    """Control row with colored styles."""
    return [[
        styled_button("▷", callback_data=f"ADMIN Resume|{chat_id}", style="success"),
        styled_button("II", callback_data=f"ADMIN Pause|{chat_id}", style="primary"),
        styled_button("↻", callback_data=f"ADMIN Replay|{chat_id}", style="primary"),
        styled_button("‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style="primary"),
        styled_button("▢", callback_data=f"ADMIN Stop|{chat_id}", style="danger"),
    ]]


def colored_autoplay_button(chat_id: int, status: bool) -> dict:
    if status:
        return styled_button("🔁 ᴀᴜᴛᴏᴘʟᴀʏ : ᴏɴ ✅", callback_data=f"AUTOPLAY_TOGGLE {chat_id}", style="success")
    else:
        return styled_button("🔁 ᴀᴜᴛᴏᴘʟᴀʏ : ᴏғғ ❌", callback_data=f"AUTOPLAY_TOGGLE {chat_id}", style="danger")


def colored_stream_markup(_, chat_id, autoplay_status: bool = False):
    """Stream 'Now Playing' buttons with colors."""
    return (
        colored_control_buttons(_, chat_id)
        + [[colored_autoplay_button(chat_id, autoplay_status)]]
        + [[styled_button(_["CLOSE_BUTTON"], callback_data="close", style="danger")]]
    )


def colored_stream_markup_timer(_, chat_id, played, dur, autoplay_status: bool = False):
    """Stream buttons with progress bar and colors."""
    if not should_update_progress(chat_id):
        return None

    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    bar = generate_progress_bar(played_sec, duration_sec)

    return (
        [[styled_button(f"{played} {bar} {dur}", callback_data="GetTimer")]]
        + colored_control_buttons(_, chat_id)
        + [[colored_autoplay_button(chat_id, autoplay_status)]]
        + [[styled_button(_["CLOSE_BUTTON"], callback_data="close", style="danger")]]
    )
