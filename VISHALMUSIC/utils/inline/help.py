from VISHALMUSIC import app
from VISHALMUSIC.utils.colored_buttons import styled_button


TOTAL_SECTIONS = 29


def generate_help_buttons(_, start: int, end: int, current_page: int):
    buttons, per_row = [], 3
    for idx, i in enumerate(range(start, end + 1)):
        if idx % per_row == 0:
            buttons.append([])
        buttons[-1].append(
            styled_button(
                text=_[f"H_B_{i}"],
                callback_data=f"help_callback hb{i}_p{current_page}",
                style="primary",
            )
        )
    return buttons


def first_page(_):
    buttons = generate_help_buttons(_, 1, 15, current_page=1)
    buttons.append(
        [
            styled_button(text="๏ ᴍᴇɴᴜ ๏", callback_data="back_to_main", style="primary"),
            styled_button(text="๏ ɴᴇxᴛ ๏", callback_data="help_next_2", style="primary"),
        ]
    )
    return buttons


def second_page(_):
    buttons = generate_help_buttons(_, 16, TOTAL_SECTIONS, current_page=2)
    buttons.append(
        [
            styled_button(text="๏ ʙᴀᴄᴋ ๏", callback_data="help_prev_1", style="primary"),
            styled_button(text="๏ ᴍᴇɴᴜ ๏", callback_data="back_to_main", style="primary"),
        ]
    )
    return buttons


def action_sub_menu(_, current_page: int):
    return [
        [
            styled_button(text=_["H_B_S_1"], callback_data="action_prom_1", style="primary"),
            styled_button(text=_["H_B_S_2"], callback_data="action_pun_1", style="danger"),
        ],
        [
            styled_button(text=_["BACK_BUTTON"], callback_data=f"help_back_{current_page}", style="primary"),
        ],
    ]


def help_back_markup(_, current_page: int):
    return [
        [
            styled_button(text=_["BACK_BUTTON"], callback_data=f"help_back_{current_page}", style="primary"),
            styled_button(text=_["CLOSE_BUTTON"], callback_data="close", style="danger"),
        ],
    ]


def private_help_panel(_):
    return [
        [
            styled_button(text=_["S_B_3"], url=f"https://t.me/{app.username}?start=help"),
        ],
    ]
