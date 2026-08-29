import html
import os
from PIL import Image, ImageDraw, ImageFont
from pyrogram import enums, filters
from pyrogram.types import ChatMemberUpdated
from pyrogram.errors import TopicClosed
from VISHALMUSIC import app
from VISHALMUSIC.mongo.welcomedb import is_on, bump, cool, auto_on
from VISHALMUSIC.utils.colored_buttons import styled_button, buttons_to_inline_markup, send_photo_colored

BG_PATH = "VISHALMUSIC/assets/VISHAL/welcome.png"
FALLBACK_PIC = "VISHALMUSIC/assets/upic.png"
FONT_PATH = "VISHALMUSIC/assets/VISHAL/Arimo.ttf"
BTN_VIEW = "ıll ᴠɪᴇᴡ ᴍᴇᴍʙᴇʀ llı"
BTN_ADD = "ıll ᴀᴅᴅ ᴍᴇ llı"

CAPTION_TXT = """
✨❄─────✧ ᴡᴇʟᴄᴏᴍᴇ ✧─────❄✨
💫 {chat_title} 💫

╔═══════════════════╗
║ 👤 Nᴀᴍᴇ : {mention}
║ 🆔 Iᴅ : `{uid}`
║ 🔗 Usᴇʀɴᴀᴍᴇ : @{uname}
║ 🌐 Tᴏᴛᴀʟ Mᴇᴍʙᴇʀs : {count}
╚═══════════════════╝

❄✦─────❅✧❅✦─────✦❄
"""

JOIN_THRESHOLD = 20
TIME_WINDOW = 10
COOL_MINUTES = 5
WELCOME_LIMIT = 5

last_messages: dict[int, list] = {}


def _cooldown_minutes(burst: int, threshold: int = JOIN_THRESHOLD, base: int = COOL_MINUTES) -> int:
    if burst < threshold:
        return 0
    extra = max(0, burst - threshold)
    return min(60, base + extra * 2)


def _circle(im, size=(835, 839)):
    im = im.resize(size, Image.LANCZOS).convert("RGBA")
    mask = Image.new("L", size, 0)
    ImageDraw.Draw(mask).ellipse((0, 0, *size), fill=255)
    im.putalpha(mask)
    return im


def build_pic(av, fn, uid, un):
    # Design coordinates are for the bundled 2880x1620 welcome.png.
    # Scale them to the actual image so a swapped PNG still renders correctly.
    bg = Image.open(BG_PATH).convert("RGBA")
    draw = ImageDraw.Draw(bg)

    s = min(bg.width / 2880, bg.height / 1620)

    AVATAR_SIZE = (round(835 * s), round(839 * s))
    AVATAR_POSITION = (round(1887 * s), round(390 * s))
    avatar = _circle(Image.open(av), size=AVATAR_SIZE)
    bg.paste(avatar, AVATAR_POSITION, avatar)

    font = ImageFont.truetype(FONT_PATH, max(16, round(65 * s)))

    NAME_X = round(550 * s)
    NAME_Y = round(720 * s)
    draw.text((NAME_X, NAME_Y), fn, fill=(242, 242, 242), font=font)

    ID_X = round(350 * s)
    ID_Y = round(1000 * s)
    draw.text((ID_X, ID_Y), str(uid), fill=(242, 242, 242), font=font)

    USERNAME_X = round(600 * s)
    USERNAME_Y = round(1300 * s)
    draw.text((USERNAME_X, USERNAME_Y), un, fill=(242, 242, 242), font=font)

    path = f"downloads/welcome_{uid}.png"
    os.makedirs("downloads", exist_ok=True)
    bg.save(path)
    return path


@app.on_chat_member_updated(filters.group, group=-3)
async def welcome(client, update: ChatMemberUpdated):
    old = update.old_chat_member
    new = update.new_chat_member
    cid = update.chat.id
    if not (new and new.status == enums.ChatMemberStatus.MEMBER):
        return
    valid_old_statuses = (enums.ChatMemberStatus.LEFT, enums.ChatMemberStatus.BANNED)
    if old and (old.status not in valid_old_statuses):
        return
    if not await is_on(cid):
        if await auto_on(cid):
            try:
                await client.send_message(cid, "**ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ʀᴇ-ᴇɴᴀʙʟᴇᴅ.**")
            except TopicClosed:
                return
        else:
            return
    burst = await bump(cid, TIME_WINDOW)
    if burst >= JOIN_THRESHOLD:
        minutes = _cooldown_minutes(burst, JOIN_THRESHOLD, COOL_MINUTES)
        await cool(cid, minutes)
        try:
            return await client.send_message(
                cid,
                f"**ᴍᴀssɪᴠᴇ ᴊᴏɪɴ ᴅᴇᴛᴇᴄᴛᴇᴅ (x{burst}). ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs ᴅɪsᴀʙʟᴇᴅ ғᴏʀ {minutes} ᴍɪɴᴜᴛᴇs.**"
            )
        except TopicClosed:
            return

    user = new.user
    avatar = img = None
    try:
        avatar = await client.download_media(user.photo.big_file_id, file_name=f"downloads/pp_{user.id}.png") if user.photo else FALLBACK_PIC
        img = build_pic(avatar, user.first_name, user.id, user.username or "No Username")
        members = await client.get_chat_members_count(cid)
        caption = CAPTION_TXT.format(
            chat_title=html.escape(str(update.chat.title)),
            mention=user.mention,
            uid=user.id,
            uname=html.escape(user.username or "No Username"),
            count=members
        )
        try:
            sent = await send_photo_colored(
                chat_id=cid,
                photo=img,
                caption=caption,
                reply_markup=[
                    [styled_button(BTN_VIEW, url=f"tg://openmessage?user_id={user.id}", style="primary")],
                    [styled_button(BTN_ADD, url=f"https://t.me/{client.username}?startgroup=true", style="success")],
                ]
            )
        except TopicClosed:
            return

        last_messages.setdefault(cid, []).append(sent)
        if len(last_messages[cid]) > WELCOME_LIMIT:
            old_msg = last_messages[cid].pop(0)
            if old_msg:
                try:
                    if isinstance(old_msg, dict):
                        chat_id = old_msg.get("chat", {}).get("id") or cid
                        msg_id = old_msg.get("message_id")
                        if msg_id:
                            await app.delete_messages(chat_id, msg_id)
                    else:
                        await old_msg.delete()
                except:
                    pass
    except TopicClosed:
        return
    except Exception:
        try:
            await client.send_message(cid, f"🎉 Welcome, {user.mention}!")
        except TopicClosed:
            return
    finally:
        for f in (avatar, img):
            if f and os.path.exists(f) and "VISHALMUSIC/assets" not in f:
                try:
                    os.remove(f)
                except:
                    pass

