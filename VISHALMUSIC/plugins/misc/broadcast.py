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
    smart_send_message,
    smart_send_photo,
)
from VISHALMUSIC.utils.database import (
    get_active_chats,
    get_authuser_names,
    get_client,
    get_served_chats,
    get_served_users,
)
from VISHALMUSIC.utils.decorators.language import language
from VISHALMUSIC.utils.formatters import alpha_to_int
from config import SUPPORT_CHAT, adminlist

IS_BROADCASTING = False


def _extract_buttons(text: str):
    """Parse -btn segments into rows of colored URL buttons and strip them
    from the caption text.

    Supported syntax (sab kaam karta hai):
      -btn "Label1|https://url" "Label2|https://url"   -> one row, 2 buttons
      -btn/Label/URL                                   -> easy form (no quotes)
      -btn Label|https://url                           -> bare form
    Repeat `-btn` for more rows.
    Returns (caption_without_btn_parts, buttons).
    """
    if not text or "-btn" not in text:
        return (text or "").strip(), []

    # Known broadcast flags act as boundaries so a -btn spec never eats them.
    _FLAGS = r"(?:pinloud|pin|nobot|assistant|assistaint|user|photo|forward|wfchat|wfuser)"

    def _url_ok(u: str) -> bool:
        return bool(u) and u.startswith(("http://", "https://"))

    def _parse_spec(s: str):
        """Return (label, url) for one -btn spec, or None."""
        s = s.strip()
        if not s:
            return None
        # slash form: -btn/Label/URL   (URL may contain more slashes)
        if s.startswith("/"):
            parts = s[1:].split("/", 1)
            if len(parts) == 2 and _url_ok(parts[1].strip()):
                return parts[0].strip(), parts[1].strip()
            return None
        # quoted label first: -btn "Label|URL"  /  -btn "Label" URL  /  "Label"|URL
        m = re.match(r'^\s*"([^"]+)"\s*\|?\s*', s)
        if m:
            label, url = None, None
            quoted = m.group(1).strip()
            rest = s[m.end():].strip()
            # pipe may live INSIDE the quotes: "Label|URL"
            lbl, sep, inurl = quoted.partition("|")
            label = lbl.strip()
            if sep and inurl.strip() and _url_ok(inurl.strip()):
                url = inurl.strip()
            # or the URL sits outside the quotes
            elif rest:
                if rest.startswith("|"):
                    rest = rest[1:].strip()
                url = rest.split(None, 1)[0].strip() if rest else None
                if not _url_ok(url or ""):
                    url = None
            if label and _url_ok(url or ""):
                return label, url
            return None
        # bare/raw: "Label|URL" or "Label | URL" (tolerate spaces around |)
        if "|" in s:
            label, _, url = s.partition("|")
            label = label.strip().strip('"').strip()
            url = url.strip().strip('"').strip()
            if label and _url_ok(url):
                return label, url
            return None
        # last try: "Label URL" separated by whitespace
        sp = s.split(None, 1)
        if len(sp) == 2 and _url_ok(sp[1].strip()):
            return sp[0].strip().strip('"').strip(), sp[1].strip()
        return None

    rows = []
    cleaned = ""
    rest = text
    while True:
        m = re.search(r"(^|\s)-btn\b", rest)
        if not m:
            cleaned += rest
            break
        cleaned += rest[: m.start()]  # keep text before the marker
        rest = rest[m.end():]
        # spec ends at the next -btn marker or at a known flag token
        b = re.search(
            r"\s(?=-btn\b)|(?:\s-)(?:" + _FLAGS + r")(?![\w])", rest
        )
        end = b.start() if b else len(rest)
        spec = rest[:end]
        rest = rest[end:]
        parsed = _parse_spec(spec)
        if parsed:
            rows.append(
                [styled_button(parsed[0], url=parsed[1], style="primary")]
            )
    return cleaned.strip(), rows


@app.on_message(filters.command("broadcast") & SUDOERS)
@language
async def braodcast_message(client, message, _):
    global IS_BROADCASTING

    # ── "With File" quick modes (ported from ShrutiMusic broadcast) ──────────
    # /broadcast -wfchat   → reply-to photo/text, send FRESH to all served chats only
    # /broadcast -wfuser   → reply-to photo/text, send FRESH to all served users only
    # add -forward         → forward the original message instead of sending fresh
    if "-wfchat" in message.text or "-wfuser" in message.text:
        if not message.reply_to_message or not (
            message.reply_to_message.photo or message.reply_to_message.text
        ):
            return await message.reply_text(
                "Please reply to a text or image message for broadcasting."
            )
        reply = message.reply_to_message
        is_photo = bool(reply.photo)
        file_id = reply.photo.file_id if is_photo else None
        text_content = reply.text or ""
        caption = reply.caption or text_content
        reply_markup = getattr(reply, "reply_markup", None)

        IS_BROADCASTING = True
        await message.reply_text(_["broad_1"])

        targets = []
        if "-wfchat" in message.text:
            targets = [int(chat["chat_id"]) for chat in await get_served_chats()]
        else:
            targets = [int(user["user_id"]) for user in await get_served_users()]

        sent = 0
        for chat_id in targets:
            try:
                if "-forward" in message.text:
                    await app.forward_messages(
                        chat_id=chat_id,
                        from_chat_id=reply.chat.id,
                        message_ids=reply.id,
                    )
                elif is_photo:
                    m = await smart_send_photo(
                        chat_id=chat_id, photo=file_id, caption=caption or None,
                        reply_markup=reply_markup,
                    )
                    if not m:
                        m = await app.send_photo(
                            chat_id, file_id, caption=caption or None,
                            reply_markup=reply_markup,
                        )
                else:
                    m = await smart_send_message(
                        chat_id=chat_id, text=text_content,
                        reply_markup=reply_markup,
                    )
                    if not m:
                        m = await app.send_message(
                            chat_id, text_content, reply_markup=reply_markup,
                        )
                sent += 1
                await asyncio.sleep(0.2)
            except FloodWait as fw:
                flood_time = int(fw.value)
                if flood_time > 200:
                    continue
                await asyncio.sleep(flood_time)
            except Exception:
                continue
        kind = "chats" if "-wfchat" in message.text else "users"
        try:
            await message.reply_text(
                f"Broadcast to {kind} completed! Sent to {sent} {kind}."
            )
        except Exception:
            pass
        IS_BROADCASTING = False
        return

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

    # Parse -btn buttons FIRST (they get stripped from the caption too).
    query, buttons = _extract_buttons(query or "")

    # Photo source: -photo <url|file_id> takes priority, else reply-to-photo.
    photo = None
    reply = message.reply_to_message
    m_photo = re.search(r"-photo\s+(\S+)", query or "")
    if m_photo and m_photo.group(1).startswith(("http://", "https://")):
        photo = m_photo.group(1)
        query = query.replace(m_photo.group(0), "")
    elif reply and reply.photo and len(message.command) > 1:
        photo = reply.photo.file_id

    # NOTE: -pinloud must be stripped BEFORE -pin (substring conflict)
    for flag in ("-pinloud", "-pin", "-nobot", "-assistant", "-assistaint", "-user", "-photo"):
        query = query.replace(flag, "")
    query = query.strip()

    if not message.reply_to_message and not photo and query == "" and not buttons:
        return await message.reply_text(_["broad_8"])

    IS_BROADCASTING = True
    await message.reply_text(_["broad_1"])

    # Auto support button: photo broadcast without buttons, or -btn with no
    # valid buttons parsed.
    if not buttons and SUPPORT_CHAT and (photo or "-btn" in (message.text or "")):
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
        if buttons:
            # Text + inline keyboard buttons (colored via Bot API, fallback included).
            return await smart_send_message(
                chat_id=chat_id,
                text=query or "\u200b",
                reply_markup=buttons,
            )
        return (
            await app.forward_messages(chat_id, y, x)
            if message.reply_to_message
            else await app.send_message(chat_id, text=query)
        )

    if "-nobot" not in message.text:
        sent = 0
        pin = 0
        chats = []
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

    if "-assistant" in message.text or "-assistaint" in message.text:
        aw = await message.reply_text(_["broad_5"])
        text = _["broad_6"]
        from VISHALMUSIC.core.userbot import assistants

        for num in assistants:
            sent = 0
            client = await get_client(num)
            async for dialog in client.get_dialogs():
                try:
                    if photo:
                        await client.send_photo(
                            dialog.chat.id,
                            photo,
                            caption=query,
                            reply_markup=buttons_to_inline_markup(buttons) if buttons else None,
                        )
                    elif buttons:
                        await client.send_message(
                            dialog.chat.id,
                            text=query or "\u200b",
                            reply_markup=buttons_to_inline_markup(buttons) if buttons else None,
                        )
                    elif message.reply_to_message:
                        await client.forward_messages(dialog.chat.id, y, x)
                    else:
                        await client.send_message(dialog.chat.id, text=query)
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