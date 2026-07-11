from typing import Union
from VISHALMUSIC.utils.colored_buttons import styled_button


def queue_markup(
    _,
    DURATION,
    CPLAY,
    videoid,
    played: Union[bool, int] = None,
    dur: Union[bool, int] = None,
):
    not_dur = [
        [
            styled_button(
                text=_["QU_B_1"],
                callback_data=f"GetQueued {CPLAY}|{videoid}",
                style="primary",
            ),
            styled_button(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
                style="danger",
            ),
        ]
    ]
    dur_buttons = [
        [
            styled_button(
                text=_["QU_B_2"].format(played, dur),
                callback_data="GetTimer",
            )
        ],
        [
            styled_button(
                text=_["QU_B_1"],
                callback_data=f"GetQueued {CPLAY}|{videoid}",
                style="primary",
            ),
            styled_button(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
                style="danger",
            ),
        ],
    ]
    return not_dur if DURATION == "Unknown" else dur_buttons


def queue_back_markup(_, CPLAY):
    return [
        [
            styled_button(
                text=_["BACK_BUTTON"],
                callback_data=f"queue_back_timer {CPLAY}",
                style="primary",
            ),
            styled_button(
                text=_["CLOSE_BUTTON"],
                callback_data="close",
                style="danger",
            ),
        ]
    ]


def aq_markup(_, chat_id):
    buttons = [
        [
            styled_button(text="▷", callback_data=f"ADMIN Resume|{chat_id}", style="success"),
            styled_button(text="II", callback_data=f"ADMIN Pause|{chat_id}", style="primary"),
            styled_button(text="‣‣I", callback_data=f"ADMIN Skip|{chat_id}", style="primary"),
            styled_button(text="▢", callback_data=f"ADMIN Stop|{chat_id}", style="danger"),
        ],
        [styled_button(text=_["CLOSE_BUTTON"], callback_data="close", style="danger")],
    ]
    return buttons
