import asyncio

from pyrogram.enums import ChatMemberStatus
from pyrogram.errors import (
    ChatAdminRequired,
    InviteHashExpired,
    InviteRequestSent,
    UserAlreadyParticipant,
    UserNotParticipant,
)

from config import PLAYLIST_IMG_URL, SUPPORT_CHAT, adminlist
from strings import get_string
from VISHALMUSIC import YouTube, app
from VISHALMUSIC.misc import SUDOERS
from VISHALMUSIC.utils.database import (
    get_assistant,
    get_cmode,
    get_lang,
    get_playmode,
    get_playtype,
    is_active_chat,
    is_maintenance,
)
from VISHALMUSIC.utils.inline import botplaylist_markup
from VISHALMUSIC.utils.colored_buttons import styled_button, send_message_colored, send_photo_colored

links = {}


def PlayWrapper(command):
    async def wrapper(client, message):
        chat_id_raw = message.chat.id
        lang_task = asyncio.create_task(get_lang(chat_id_raw))
        maintenance_task = asyncio.create_task(is_maintenance())
        playmode_task = asyncio.create_task(get_playmode(chat_id_raw))
        playtype_task = asyncio.create_task(get_playtype(chat_id_raw))

        language = await lang_task
        _ = get_string(language)

        if message.sender_chat:
            upl = [[styled_button(text="ʜᴏᴡ ᴛᴏ ғɪx ?", callback_data="AnonymousAdmin", style="primary")]]
            return await send_message_colored(message.chat.id, _["general_3"], reply_markup=upl)

        if await maintenance_task is False:
            if message.from_user.id not in SUDOERS:
                return await message.reply_text(
                    text=f"{app.mention} ɪs ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ, ᴠɪsɪᴛ <a href={SUPPORT_CHAT}>sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ</a> ғᴏʀ ᴋɴᴏᴡɪɴɢ ᴛʜᴇ ʀᴇᴀsᴏɴ.",
                    disable_web_page_preview=True,
                )

        try:
            await message.delete()
        except Exception:
            pass

        audio_telegram = (
            (message.reply_to_message.audio or message.reply_to_message.voice)
            if message.reply_to_message
            else None
        )
        video_telegram = (
            (message.reply_to_message.video or message.reply_to_message.document)
            if message.reply_to_message
            else None
        )
        url = await YouTube.url(message)

        if audio_telegram is None and video_telegram is None and url is None:
            if len(message.command) < 2:
                if "stream" in message.command:
                    return await message.reply_text(_["str_1"])
                buttons = botplaylist_markup(_)
                return await send_photo_colored(
                    chat_id=message.chat.id,
                    photo=PLAYLIST_IMG_URL,
                    caption=_["play_18"],
                    reply_markup=buttons,
                )
        if message.command[0][0] == "c":
            chat_id = await get_cmode(message.chat.id)
            if chat_id is None:
                return await message.reply_text(_["setting_7"])
            try:
                chat = await app.get_chat(chat_id)
            except Exception:
                return await message.reply_text(_["cplay_4"])
            channel = chat.title
        else:
            chat_id = message.chat.id
            channel = None

        playmode = await playmode_task
        playty = await playtype_task
        if playty != "Everyone":
            if message.from_user.id not in SUDOERS:
                admins = adminlist.get(message.chat.id)
                if not admins:
                    return await message.reply_text(_["admin_13"])
                elif message.from_user.id not in admins:
                    return await message.reply_text(_["play_4"])

        if message.command[0][0] == "v":
            video = True
        else:
            if "-v" in message.text:
                video = True
            else:
                video = True if message.command[0][1] == "v" else None

        if message.command[0][-1] == "e":
            if not await is_active_chat(chat_id):
                return await message.reply_text(_["play_16"])
            fplay = True
        else:
            fplay = None

        if not await is_active_chat(chat_id):
            userbot = await get_assistant(chat_id)
            try:
                try:
                    member = await app.get_chat_member(chat_id, userbot.id)
                except ChatAdminRequired:
                    return await message.reply_text(_["call_1"])

                if member.status in (
                    ChatMemberStatus.BANNED,
                    ChatMemberStatus.RESTRICTED,
                ):
                    btn = [[styled_button(text="๏ 𝗨ɴʙᴀɴ 𝗔ssɪsᴛᴀɴᴛ ๏", callback_data="unban_assistant", style="danger")]]
                    return await send_message_colored(
                        message.chat.id,
                        _["call_2"].format(
                            app.mention, userbot.id, userbot.name, userbot.username
                        ),
                        reply_markup=btn,
                    )
            except UserNotParticipant:
                if chat_id in links:
                    invitelink = links[chat_id]
                else:
                    if message.chat.username:
                        invitelink = message.chat.username
                        try:
                            await userbot.resolve_peer(invitelink)
                        except Exception:
                            pass
                    else:
                        try:
                            invitelink = await app.export_chat_invite_link(chat_id)
                        except ChatAdminRequired:
                            return await message.reply_text(_["call_1"])
                        except Exception as e:
                            return await message.reply_text(
                                _["call_3"].format(app.mention, type(e).__name__)
                            )

                if invitelink.startswith("https://t.me/+"):
                    invitelink = invitelink.replace(
                        "https://t.me/+", "https://t.me/joinchat/"
                    )

                myu = await message.reply_text(_["call_4"].format(app.mention))
                try:
                    await userbot.join_chat(invitelink)
                except InviteHashExpired:
                    if chat_id in links:
                        del links[chat_id]
                    try:
                        invitelink = await app.export_chat_invite_link(chat_id)
                    except ChatAdminRequired:
                        return await message.reply_text(_["call_1"])
                    except Exception as e:
                        return await message.reply_text(
                            _["call_3"].format(app.mention, type(e).__name__)
                        )
                    if invitelink.startswith("https://t.me/+"):
                        invitelink = invitelink.replace(
                            "https://t.me/+", "https://t.me/joinchat/"
                        )
                    links[chat_id] = invitelink
                    await userbot.join_chat(invitelink)
                except InviteRequestSent:
                    try:
                        await app.approve_chat_join_request(chat_id, userbot.id)
                    except Exception as e:
                        return await message.reply_text(
                            _["call_3"].format(app.mention, type(e).__name__)
                        )
                    await asyncio.sleep(1)
                    await myu.edit(_["call_5"].format(app.mention))
                except UserAlreadyParticipant:
                    pass
                except Exception as e:
                    return await message.reply_text(
                        _["call_3"].format(app.mention, type(e).__name__)
                    )

                links[chat_id] = invitelink

                try:
                    await userbot.resolve_peer(chat_id)
                except Exception:
                    pass

        return await command(
            client, message, _, chat_id, video, channel, playmode, url, fplay
        )

    return wrapper
