from typing import Union
from VISHALMUSIC.utils.colored_buttons import styled_button


def setting_markup(_):
    buttons = [
        [
            styled_button(text=_["ST_B_1"], callback_data="AU", style="primary"),
            styled_button(text=_["ST_B_3"], callback_data="LG", style="primary"),
        ],
        [
            styled_button(text=_["ST_B_2"], callback_data="PM", style="primary"),
        ],
        [
            styled_button(text=_["ST_B_4"], callback_data="VM", style="primary"),
        ],
        [
            styled_button(text=_["CLOSE_BUTTON"], callback_data="close", style="danger"),
        ],
    ]
    return buttons


def vote_mode_markup(_, current, mode: Union[bool, str] = None):
    buttons = [
        [
            styled_button(text="Vᴏᴛɪɴɢ ᴍᴏᴅᴇ ➜", callback_data="VOTEANSWER"),
            styled_button(
                text=_["ST_B_5"] if mode == True else _["ST_B_6"],
                callback_data="VOMODECHANGE",
                style="success" if mode == True else "danger",
            ),
        ],
        [
            styled_button(text="-2", callback_data="FERRARIUDTI M", style="primary"),
            styled_button(text=f"ᴄᴜʀʀᴇɴᴛ : {current}", callback_data="ANSWERVOMODE"),
            styled_button(text="+2", callback_data="FERRARIUDTI A", style="primary"),
        ],
        [
            styled_button(text=_["BACK_BUTTON"], callback_data="settings_helper", style="primary"),
            styled_button(text=_["CLOSE_BUTTON"], callback_data="close", style="danger"),
        ],
    ]
    return buttons


def auth_users_markup(_, status: Union[bool, str] = None):
    buttons = [
        [
            styled_button(text=_["ST_B_7"], callback_data="AUTHANSWER"),
            styled_button(
                text=_["ST_B_8"] if status == True else _["ST_B_9"],
                callback_data="AUTH",
                style="success" if status == True else "danger",
            ),
        ],
        [
            styled_button(text=_["ST_B_1"], callback_data="AUTHLIST", style="primary"),
        ],
        [
            styled_button(text=_["BACK_BUTTON"], callback_data="settings_helper", style="primary"),
            styled_button(text=_["CLOSE_BUTTON"], callback_data="close", style="danger"),
        ],
    ]
    return buttons


def playmode_users_markup(
    _,
    Direct: Union[bool, str] = None,
    Group: Union[bool, str] = None,
    Playtype: Union[bool, str] = None,
):
    buttons = [
        [
            styled_button(text=_["ST_B_10"], callback_data="SEARCHANSWER"),
            styled_button(
                text=_["ST_B_11"] if Direct == True else _["ST_B_12"],
                callback_data="MODECHANGE",
                style="success" if Direct == True else "danger",
            ),
        ],
        [
            styled_button(text=_["ST_B_13"], callback_data="AUTHANSWER"),
            styled_button(
                text=_["ST_B_8"] if Group == True else _["ST_B_9"],
                callback_data="CHANNELMODECHANGE",
                style="success" if Group == True else "danger",
            ),
        ],
        [
            styled_button(text=_["ST_B_14"], callback_data="PLAYTYPEANSWER"),
            styled_button(
                text=_["ST_B_8"] if Playtype == True else _["ST_B_9"],
                callback_data="PLAYTYPECHANGE",
                style="success" if Playtype == True else "danger",
            ),
        ],
        [
            styled_button(text=_["BACK_BUTTON"], callback_data="settings_helper", style="primary"),
            styled_button(text=_["CLOSE_BUTTON"], callback_data="close", style="danger"),
        ],
    ]
    return buttons

def audio_quality_markup(
    _,
    low: Union[bool, str] = None,
    medium: Union[bool, str] = None,
    high: Union[bool, str] = None,
):
    buttons = [
        [
            styled_button(
                text=_["ST_B_8"].format("✅") if low == True else _["ST_B_8"].format(""),
                callback_data="LQA",
                style="success" if low == True else None,
            )
        ],
        [
            styled_button(
                text=_["ST_B_9"].format("✅") if medium == True else _["ST_B_9"].format(""),
                callback_data="MQA",
                style="success" if medium == True else None,
            )
        ],
        [
            styled_button(
                text=_["ST_B_10"].format("✅") if high == True else _["ST_B_10"].format(""),
                callback_data="HQA",
                style="success" if high == True else None,
            )
        ],
        [
            styled_button(text=_["BACK_BUTTON"], callback_data="settingsback_helper", style="primary"),
            styled_button(text=_["CLOSE_BUTTON"], callback_data="close", style="danger"),
        ],
    ]
    return buttons


def video_quality_markup(
    _,
    low: Union[bool, str] = None,
    medium: Union[bool, str] = None,
    high: Union[bool, str] = None,
):
    buttons = [
        [
            styled_button(
                text=_["ST_B_11"].format("✅") if low == True else _["ST_B_11"].format(""),
                callback_data="LQV",
                style="success" if low == True else None,
            )
        ],
        [
            styled_button(
                text=_["ST_B_12"].format("✅") if medium == True else _["ST_B_12"].format(""),
                callback_data="MQV",
                style="success" if medium == True else None,
            )
        ],
        [
            styled_button(
                text=_["ST_B_13"].format("✅") if high == True else _["ST_B_13"].format(""),
                callback_data="HQV",
                style="success" if high == True else None,
            )
        ],
        [
            styled_button(text=_["BACK_BUTTON"], callback_data="settingsback_helper", style="primary"),
            styled_button(text=_["CLOSE_BUTTON"], callback_data="close", style="danger"),
        ],
    ]
    return buttons
