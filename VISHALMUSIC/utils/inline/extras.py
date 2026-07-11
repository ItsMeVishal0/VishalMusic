from config import SUPPORT_CHAT
from VISHALMUSIC.utils.colored_buttons import styled_button


def botplaylist_markup(_):
    buttons = [
        [
            styled_button(text=_["S_B_4"], url=SUPPORT_CHAT),
            styled_button(text=_["CLOSE_BUTTON"], callback_data="close", style="danger"),
        ],
    ]
    return buttons


def close_markup(_):
    return [
        [
            styled_button(text=_["CLOSE_BUTTON"], callback_data="close", style="danger"),
        ],
    ]


def supp_markup(_):
    return [
        [
            styled_button(text=_["S_B_4"], url=SUPPORT_CHAT),
        ],
    ]
