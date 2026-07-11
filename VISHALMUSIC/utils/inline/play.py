# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   GitHub : github.com/ItsMeVishal0/VishalMusic
#   Developer : @ItsMeVishalBots | Telegram
#   Module : Inline Play Buttons (Colored)
# ═══════════════════════════════════════════════════════════

import time
from VISHALMUSIC.utils.colored_buttons import styled_button
from VISHALMUSIC.utils.formatters import time_to_seconds

LAST_UPDATE_TIME = {}
UPDATE_INTERVAL = 8  # seconds between progress bar updates


def should_update_progress(chat_id: int) -> bool:
    now = time.time()
    last = LAST_UPDATE_TIME.get(chat_id, 0)
    if now - last >= UPDATE_INTERVAL:
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


def autoplay_button(chat_id: int, status: bool) -> dict:
    if status:
        return styled_button("🔁 ᴀᴜᴛᴏᴘʟᴀʏ : ᴏɴ ✅", callback_data=f"AUTOPLAY_TOGGLE {chat_id}", style="success")
    else:
        return styled_button("🔁 ᴀᴜᴛᴏᴘʟᴀʏ : ᴏғғ ❌", callback_data=f"AUTOPLAY_TOGGLE {chat_id}", style="danger")


def control_buttons(_, chat_id):
    return [[
        styled_button(text="▷", callback_data=f"ADMIN Resume|{chat_id}", style="success"),
        styled_button(text="II", callback_data=f"ADMIN Pause|{chat_id}", style="primary"),
        styled_button(text="↻", callback_data=f"ADMIN Replay|{chat_id}", style="primary"),
        styled_button(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style="primary"),
        styled_button(text="▢", callback_data=f"ADMIN Stop|{chat_id}", style="danger"),
    ]]


def stream_markup(_, chat_id, autoplay_status: bool = False):
    """Stream 'Now Playing' buttons with colors."""
    return (
        control_buttons(_, chat_id)
        + [[autoplay_button(chat_id, autoplay_status)]]
        + [[styled_button(text=_["CLOSE_BUTTON"], callback_data="close", style="danger")]]
    )


def stream_markup_timer(_, chat_id, played, dur, autoplay_status: bool = False):
    """Stream buttons with progress bar and colors. Returns None if not time to update yet."""
    if not should_update_progress(chat_id):
        return None

    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    bar = generate_progress_bar(played_sec, duration_sec)

    return (
        [[styled_button(f"{played} {bar} {dur}", callback_data="GetTimer", style="success")]]
        + control_buttons(_, chat_id)
        + [[autoplay_button(chat_id, autoplay_status)]]
        + [[styled_button(text=_["CLOSE_BUTTON"], callback_data="close", style="danger")]]
    )


def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    buttons = [
        [
            styled_button(
                text=_["P_B_1"],
                callback_data=f"VishalPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}",
                style="primary",
            ),
            styled_button(
                text=_["P_B_2"],
                callback_data=f"VishalPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}",
                style="primary",
            ),
        ],
        [
            styled_button(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style="danger",
            ),
        ],
    ]
    return buttons


def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    return [
        [
            styled_button(
                text=_["P_B_3"],
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}",
                style="primary",
            )
        ],
        [
            styled_button(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style="danger",
            )
        ],
    ]


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    short_query = query[:20]
    return [
        [
            styled_button(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
                style="primary",
            ),
            styled_button(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
                style="primary",
            ),
        ],
        [
            styled_button(
                text="◁",
                callback_data=f"slider B|{query_type}|{short_query}|{user_id}|{channel}|{fplay}",
                style="primary",
            ),
            styled_button(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {short_query}|{user_id}",
                style="danger",
            ),
            styled_button(
                text="▷",
                callback_data=f"slider F|{query_type}|{short_query}|{user_id}|{channel}|{fplay}",
                style="primary",
            ),
        ],
    ]


# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════


def track_markup(_, videoid, user_id, channel, fplay):
    """Single track confirmation buttons."""
    return [
        [
            styled_button(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
                style="primary",
            ),
            styled_button(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
                style="primary",
            ),
        ],
        [
            styled_button(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style="danger",
            ),
        ],
    ]
