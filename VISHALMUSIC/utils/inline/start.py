import config
from VISHALMUSIC import app
from VISHALMUSIC.utils.colored_buttons import styled_button
from VISHALMUSIC.utils.database import get_owner_id


def start_panel(_):
    # Add me = success (green, positive CTA), Channel = primary (blue, info)
    buttons = [
        [
            styled_button(text=_["S_B_1"], url=f"https://t.me/{app.username}?startgroup=true", style="success"),
            styled_button(text=_["S_B_2"], url=config.SUPPORT_CHANNEL, style="primary"),
        ],
    ]
    return buttons


async def private_panel(_):
    # Add me = success (green CTA), Owner + Support = primary (blue), Help = success (green)
    # Owner = auto-owner (first /start user) if set, else config.OWNER_ID
    owner_id = await get_owner_id() or config.OWNER_ID
    buttons = [
        [
            styled_button(text=_["S_B_1"], url=f"https://t.me/{app.username}?startgroup=true", style="success"),
        ],
        [
            styled_button(text=_["S_B_7"], url=f"tg://user?id={owner_id}", style="primary"),
            styled_button(text=_["S_B_4"], url=config.SUPPORT_CHAT, style="primary"),
        ],
        [
            styled_button(text=_["S_B_3"], callback_data="open_help", style="success"),
        ],
    ]
    return buttons
