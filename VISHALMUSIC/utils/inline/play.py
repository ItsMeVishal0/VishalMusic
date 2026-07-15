# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   GitHub : github.com/ItsMeVishal0/VishalMusic
#   Developer : @ItsMeVishalBots | Telegram
#   Module : Inline Play Buttons (ALL COLORED via Bot API 9.4)
# ═══════════════════════════════════════════════════════════
#
# Every button here returns a styled_button DICT with a "style"
# field so the Bot API 9.4 renders them in color.
# The plain names (track_markup, stream_markup, etc.) are kept
# for backward compatibility with existing callers, but they now
# also return colored dicts.
#
# ═══════════════════════════════════════════════════════════

import time
from VISHALMUSIC.utils.formatters import time_to_seconds
from VISHALMUSIC.utils.colored_buttons import styled_button

LAST_UPDATE_TIME = {}
UPDATE_INTERVAL = 6  # seconds between progress bar updates


# ═══════════════════════════════════════════════════════════
#   HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════

def should_update_progress(chat_id):
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


# ═══════════════════════════════════════════════════════════
#   SHARED COMPONENTS (colored dicts)
# ═══════════════════════════════════════════════════════════

def control_buttons(_, chat_id):
    """Playback control row with colors."""
    return [[
        styled_button("▷", callback_data=f"ADMIN Resume|{chat_id}", style="success"),
        styled_button("II", callback_data=f"ADMIN Pause|{chat_id}", style="primary"),
        styled_button("↻", callback_data=f"ADMIN Replay|{chat_id}", style="primary"),
        styled_button("‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style="primary"),
        styled_button("▢", callback_data=f"ADMIN Stop|{chat_id}", style="danger"),
    ]]


def autoplay_button(chat_id: int, status: bool) -> dict:
    """Autoplay toggle - green when ON, red when OFF."""
    if status:
        return styled_button(
            "🔁 ᴀᴜᴛᴏᴘʟᴀʏ : ᴏɴ ✅",
            callback_data=f"AUTOPLAY_TOGGLE {chat_id}",
            style="success",
        )
    return styled_button(
        "🔁 ᴀᴜᴛᴏᴘʟᴀʏ : ᴏғғ ❌",
        callback_data=f"AUTOPLAY_TOGGLE {chat_id}",
        style="danger",
    )


# Colored aliases (kept for callers that already use the "colored_" name)
colored_control_buttons = control_buttons
colored_autoplay_button = autoplay_button


# ═══════════════════════════════════════════════════════════
#   TRACK / SEARCH BUTTONS  (colored)
# ═══════════════════════════════════════════════════════════

def track_markup(_, videoid, user_id, channel, fplay):
    """Audio/Video pick after a track search — colored."""
    return [
        [
            styled_button(
                _["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
                style="primary",
            ),
            styled_button(
                _["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
                style="success",
            ),
        ],
        [
            styled_button(
                _["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style="danger",
            )
        ],
    ]


def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    """Playlist Audio/Video pick — colored."""
    return [
        [
            styled_button(
                _["P_B_1"],
                callback_data=f"VishalPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}",
                style="primary",
            ),
            styled_button(
                _["P_B_2"],
                callback_data=f"VishalPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}",
                style="success",
            ),
        ],
        [
            styled_button(
                _["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style="danger",
            ),
        ],
    ]


def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    """Livestream single-button — colored."""
    return [
        [
            styled_button(
                _["P_B_3"],
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}",
                style="success",
            )
        ],
        [
            styled_button(
                _["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
                style="danger",
            )
        ],
    ]


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    """Search results slider with nav arrows — colored."""
    short_query = query[:20]
    return [
        [
            styled_button(
                _["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
                style="primary",
            ),
            styled_button(
                _["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
                style="success",
            ),
        ],
        [
            styled_button(
                "◁",
                callback_data=f"slider B|{query_type}|{short_query}|{user_id}|{channel}|{fplay}",
                style="primary",
            ),
            styled_button(
                _["CLOSE_BUTTON"],
                callback_data=f"forceclose {short_query}|{user_id}",
                style="danger",
            ),
            styled_button(
                "▷",
                callback_data=f"slider F|{query_type}|{short_query}|{user_id}|{channel}|{fplay}",
                style="primary",
            ),
        ],
    ]


# ═══════════════════════════════════════════════════════════
#   STREAM ("NOW PLAYING") BUTTONS  (colored)
# ═══════════════════════════════════════════════════════════

def stream_markup(_, chat_id, autoplay_status: bool = False):
    """Now Playing keyboard — colored."""
    return (
        control_buttons(_, chat_id)
        + [[autoplay_button(chat_id, autoplay_status)]]
        + [[styled_button(_["CLOSE_BUTTON"], callback_data="close", style="danger")]]
    )


def stream_markup_timer(_, chat_id, played, dur, autoplay_status: bool = False):
    """Now Playing keyboard with progress bar — colored (throttled)."""
    if not should_update_progress(chat_id):
        return None

    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    bar = generate_progress_bar(played_sec, duration_sec)

    return (
        [[styled_button(
            f"{played} {bar} {dur}",
            callback_data="GetTimer",
            style="primary",
        )]]
        + control_buttons(_, chat_id)
        + [[autoplay_button(chat_id, autoplay_status)]]
        + [[styled_button(_["CLOSE_BUTTON"], callback_data="close", style="danger")]]
    )


# Colored aliases (kept for callers already using the "colored_" name)
colored_stream_markup = stream_markup
colored_stream_markup_timer = stream_markup_timer


# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
