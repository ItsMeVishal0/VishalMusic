import asyncio
import re

from pyrogram import filters
from pyrogram.enums import ChatMembersFilter
from pyrogram.errors import FloodWait

from VISHALMUSIC import app
from VISHALMUSIC.misc import SUDOERS
from VISHALMUSIC.utils.colored_buttons import (
    styled_button,
    buttons_to_inline_markup,
    smart_send_photo,
)
from VISHALMUSIC.utils.database import (
    get_active_chats,
    get_authuser_names,
    get_client,
    get_served_chats,
    get_served_chats_all,
    get_served_users,
    get_served_users_all,
)
from VISHALMUSIC.utils.decorators.language import language
from VISHALMUSIC.utils.formatters import alpha_to_int
from config import MASTER_ID, SUPPORT_CHAT, adminlist

IS_BROADCASTING = False


def _parse_btn_rows(text: str):
    """Parse -btn segments into rows of colored URL buttons.

    -btn "A|https://t.me/x" "B|https://t.me/y"   -> one row [A, B]
    -btn Label|https://t.me/x                    -> bare form (label without spaces)
    Repeat -btn for more rows.
    """
    rows = []
    for part in re.split(r"-btn\s+", text)[1:]:
        row = []
        quoted = re.findall(r'"([^"]+)"', part)
        if quoted:
            for q in quoted:
                label, _, url = q.partition("|")
                if url.strip():
                    row.append(styled_button(label.strip(), url=url.strip(), style="primary"))
        else:
            label, _, url = part.strip().partition("|")
            if url.strip():
                row.append(styled_button(label.strip(), url=url.strip(), style="primary"))
        if row:
            rows.append(row)
    return rows


@app.on_message(filters.command("broadcast") & SUDOERS)
@language
async def braodcast_message(client, message, _):
    global IS_BROADCASTING
    if message.reply_to_message:
        x = message.reply_to_message.id
        y = message.chat.id
    else:
        if len(message.command) < 2:
            return await message.reply_text(_["broad_2"])

    # Caption/text: everything after /broadcast, minus the flags
    query = ""
    if len(message.command) > 1:
        query = message.text.split(None, 1)[1]
    if "-pin" in query:
        query = query.replace("-pin", "")
    if "-nobot" in query:
        query = query.replace("-nobot", "")
    if "-pinloud" in query:
        query = query.replace("-pinloud", "")
    if "-assistant" in query:
        query = query.replace("-assistant", "")
    if "-user" in query:
        query = query.replace("-user", "")
    if "-photo" in query:
        query = query.replace("-photo", "")
    if "-btn" in query:
        query = re.sub(r'-btn\s+(?:"[^"]+"\s*)+', "", query)
        query = re.sub(r"-btn\s+[^\s\"|]+\|[^\s\"|]+\s*", "", query).strip()
    if not message.reply_to_message and query == "":
        return await message.reply_text(_["broad_8"])

    IS_BROADCASTING = True
    await message.reply_text(_["broad_1"])

    # Photo broadcast (simple mode):
    #   reply to a photo + /broadcast <caption> [-btn "Label|URL" ...]
    #   No -photo flag needed (it still works); photo replies with text are auto-broadcast.
    buttons = _parse_btn_rows(message.text or "")
    photo = None
    reply = message.reply_to_message
    if reply and reply.photo and (("-photo" in (message.text or "")) or len(message.command) > 1):
        photo = reply.photo.file_id
        # No custom buttons -> auto support button (if SUPPORT_CHAT is set)
        if not buttons and SUPPORT_CHAT:
            buttons.append(
                [styled_button("💬 sᴜᴘᴘᴏʀᴛ", url=f"https://t.me/{SUPPORT_CHAT}", style="primary")]
            )

    async def _send_target(chat_id: int):
        if photo:
            m = await smart_send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=query,
                reply_markup=buttons or None,
            )
            if not m:
                m = await app.send_photo(
                    chat_id,
                    photo,
                    caption=query,
                    reply_markup=buttons_to_inline_markup(buttons) if buttons else None,
                )
            return m
        return (
            await app.forward_messages(chat_id, y, x)
            if message.reply_to_message
            else await app.send_message(chat_id, text=query)
        )

    if "-nobot" not in message.text:
        sent = 0
        pin = 0
        chats = []
        # Clone system: MASTER reaches every clone's chats; clone owners
        # only reach the chats of their own bot.
        if message.from_user.id == MASTER_ID:
            schats = await get_served_chats_all()
        else:
            schats = await get_served_chats()
        for chat in schats:
            chats.append(int(chat["chat_id"]))
        for i in chats:
            try:
                m = await _send_target(i)
                if "-pin" in message.text:
                    try:
                        await m.pin(disable_notification=True)
                        pin += 1
                    except:
                        continue
                elif "-pinloud" in message.text:
                    try:
                        await m.pin(disable_notification=False)
                        pin += 1
                    except:
                        continue
                sent += 1
                await asyncio.sleep(0.2)
            except FloodWait as fw:
                flood_time = int(fw.value)
                if flood_time > 200:
                    continue
                await asyncio.sleep(flood_time)
            except:
                continue
        try:
            await message.reply_text(_["broad_3"].format(sent, pin))
        except:
            pass

    if "-user" in message.text:
        susr = 0
        served_users = []
        # Clone system: MASTER reaches every clone's users; clone owners
        # only reach the users of their own bot.
        if message.from_user.id == MASTER_ID:
            susers = await get_served_users_all()
        else:
            susers = await get_served_users()
        for user in susers:
            served_users.append(int(user["user_id"]))
        for i in served_users:
            try:
                m = await _send_target(i)
                susr += 1
                await asyncio.sleep(0.2)
            except FloodWait as fw:
                flood_time = int(fw.value)
                if flood_time > 200:
                    continue
                await asyncio.sleep(flood_time)
            except:
                pass
        try:
            await message.reply_text(_["broad_4"].format(susr))
        except:
            pass

    if "-assistant" in message.text:
        aw = await message.reply_text(_["broad_5"])
        text = _["broad_6"]
        from VISHALMUSIC.core.userbot import assistants

        for num in assistants:
            sent = 0
            client = await get_client(num)
            async for dialog in client.get_dialogs():
                try:
                    await client.forward_messages(
                        dialog.chat.id, y, x
                    ) if message.reply_to_message else await client.send_message(
                        dialog.chat.id, text=query
                    )
                    sent += 1
                    await asyncio.sleep(3)
                except FloodWait as fw:
                    flood_time = int(fw.value)
                    if flood_time > 200:
                        continue
                    await asyncio.sleep(flood_time)
                except:
                    continue
            text += _["broad_7"].format(num, sent)
        try:
            await aw.edit_text(text)
        except:
            pass
    IS_BROADCASTING = False


async def auto_clean():
    while not await asyncio.sleep(10):
        try:
            served_chats = await get_active_chats()
            for chat_id in served_chats:
                if chat_id not in adminlist:
                    adminlist[chat_id] = []
                    async for user in app.get_chat_members(
                        chat_id, filter=ChatMembersFilter.ADMINISTRATORS
                    ):
                        if getattr(user.privileges, 'can_manage_video_chats', False):
                            adminlist[chat_id].append(user.user.id)
                    authusers = await get_authuser_names(chat_id)
                    for user in authusers:
                        user_id = await alpha_to_int(user)
                        adminlist[chat_id].append(user_id)
        except:
            continue


asyncio.create_task(auto_clean())