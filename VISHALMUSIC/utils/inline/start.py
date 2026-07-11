import config
from VISHALMUSIC import app
from VISHALMUSIC.utils.colored_buttons import styled_button


def start_panel(_):
    buttons = [
        [
            styled_button(text=_["S_B_1"], url=f"https://t.me/{app.username}?startgroup=true"),
            styled_button(text=_["S_B_2"], url=config.SUPPORT_CHANNEL),
        ],
    ]
    return buttons


def private_panel(_):
    buttons = [
        [
            styled_button(text=_["S_B_1"], url=f"https://t.me/{app.username}?startgroup=true"),
        ],
        [
            styled_button(text=_["S_B_7"], url=f"tg://user?id={config.OWNER_ID}"),
            styled_button(text=_["S_B_4"], url=config.SUPPORT_CHAT),
        ],
        [
            styled_button(text=_["S_B_3"], callback_data="open_help", style="primary"),
        ],
    ]
    return buttons
