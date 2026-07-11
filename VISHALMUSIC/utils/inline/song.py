from VISHALMUSIC.utils.colored_buttons import styled_button


def song_markup(_, vidid):
    buttons = [
        [
            styled_button(text=_["SG_B_2"], callback_data=f"song_helper audio|{vidid}", style="primary"),
            styled_button(text=_["SG_B_3"], callback_data=f"song_helper video|{vidid}", style="primary"),
        ],
        [
            styled_button(text=_["CLOSE_BUTTON"], callback_data="close", style="danger"),
        ],
    ]
    return buttons
