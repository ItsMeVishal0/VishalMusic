# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   GitHub : github.com/ItsMeVishal0/VishalMusic
#   Developer : @ItsMeVishalBots | Telegram
#   Module : /start Command & Welcome Handler
# ═══════════════════════════════════════════════════════════

import time
import asyncio
import random
from pyrogram import filters
from pyrogram.enums import ChatType
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from py_yt import VideosSearch

import config
from VISHALMUSIC import app
from VISHALMUSIC.misc import _boot_
from VISHALMUSIC.plugins.sudo.sudoers import sudoers_list
from VISHALMUSIC.utils.database import (
    add_served_chat,
    add_served_user,
    blacklisted_chats,
    get_lang,
    is_banned_user,
    is_on_off,
)
from VISHALMUSIC.utils.decorators.language import LanguageStart
from VISHALMUSIC.utils.formatters import get_readable_time
from VISHALMUSIC.utils.inline.help import first_page
from VISHALMUSIC.utils.inline.start import private_panel, start_panel
from config import BANNED_USERS
from strings import get_string

# 🔥 Love, Kiss, Cute stickers - alag alag type ke (all working)
STICKERS = [
    # ❤️ Love stickers
    "CAACAgUAAxkBAAEQI1RlTLnRAy4h9lOS6jgS5FYsQoruOAAC1gMAAg6ryVcldUr_lhPexzME",
    "CAACAgQAAxkBAAMraaaBHm27-Wy2uQoptU3WZAAB6j3PAALEFQACIPCZUR1h3KoW6nItHgQ",
    "CAACAgQAAxkBAAMtaaaBKyjqLW8aBukB-vtOy-pUCxwAAoIOAAIF9AFSd_QCdbkZVqAeBA",
    "CAACAgQAAxkBAAMvaaaBNyAKbOtk05em_J8gQTmqotsAAhELAAIbGgABUuUNZ1V7LfMMHgQ",
    "CAACAgQAAxkBAAMxaaaBTZjH9A31Qdrb_xgKnrd4700AArgaAAJLO-hR8MN1DY1xe2ceBA",
    
    # 💋 Kiss stickers
    "CAACAgQAAxkBAAM5aaaB7A7JfXbtkO7b8ubX6_IjDdIAAhoVAAKRIKFRpathP0j9IIYeBA",
    "CAACAgUAAxkBAAEQI2FlTLpR8P8P8P8P8P8P8P8P8P8P8QACDwADyvhHAAHLh_6L3bL3bA",
    "CAACAgUAAxkBAAEQI2hlTLqJ8P8P8P8P8P8P8P8P8P8P8QACFgADyvhHAAHLh_6L3bL3bA",
    
    # 🥰 Cute stickers
    "CAACAgQAAxkBAAMzaaaBUYNDr2RENDvdHTkz5tg-lVcAAmkaAAIIeUlRllAUMDa5YOoeBA",
    "CAACAgQAAxkBAAM7aaaB-elXM9UEYY4OIo4eTCIbgigAAuUVAALryRlQRN37BBGYPgYeBA",
    "CAACAgQAAxkBAAM_aaaCCjmuL6EkqSBKpYbYzK3xKCcAAqYTAAK9jHlQ6vzt6mbH8-ceBA",
    "CAACAgUAAxkBAAEQI2BlTLpJ8P8P8P8P8P8P8P8P8P8P8QACDgADyvhHAAHLh_6L3bL3bA",
    "CAACAgUAAxkBAAEQI2VlTLpx8P8P8P8P8P8P8P8P8P8P8QACEwADyvhHAAHLh_6L3bL3bA",
]

# 🔥 Sirf wo reactions jo Telegram 100% support karta hai
REACTIONS = ["❤️", "🔥", "🥰", "😍", "😘", "👍", "👏", "🎉", "✨", "⭐️", "🌈", "🎵", "🎶", "💝", "💖", "💗", "💓", "💞", "💕", "💋"]

async def delete_message_after_delay(message: Message, delay: int):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except:
        pass

@app.on_message(filters.command(["start"]) & filters.private & ~BANNED_USERS)
@LanguageStart
async def start_pm(client, message: Message, _):
    try:
        await add_served_user(message.from_user.id)
    except:
        pass
    
    # 🔥 PEHLE REACTION BHEJO - PRIVATE MEIN HAR BAAR
    try:
        reaction_emoji = random.choice(REACTIONS)
        await message.react(reaction_emoji)
    except Exception:
        try:
            await message.react("❤️")
        except:
            pass
    
    # Make sure _ is a dictionary
    if isinstance(_, int):
        language = await get_lang(message.chat.id)
        _ = get_string(language)
    
    if len(message.text.split()) > 1:
        name = message.text.split(None, 1)[1]
        if name[0:4] == "help":
            keyboard = first_page(_)
            # Random sticker for help command
            try:
                await message.reply_sticker(random.choice(STICKERS))
            except Exception:
                pass
            # Image for help command
            start_photo = random.choice(config.START_IMGS)
            return await message.reply_photo(
                photo=start_photo,
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                reply_markup=keyboard,
            )
        if name[0:3] == "sud":
            await sudoers_list(client=client, message=message, _=_)
            if await is_on_off(2):
                username = f"@{message.from_user.username}" if message.from_user.username else "None"
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>sᴜᴅᴏʟɪsᴛ</b>.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> {username}",
                )
            return
        if name[0:3] == "inf":
            m = await message.reply_text("🔎")
            query = (str(name)).replace("info_", "", 1)
            query = f"https://www.youtube.com/watch?v={query}"
            results = VideosSearch(query, limit=1)
            for result in (await results.next())["result"]:
                title = result["title"]
                duration = result["duration"]
                views = result["viewCount"]["short"]
                thumbnail = result["thumbnails"][0]["url"].split("?")[0]
                channellink = result["channel"]["link"]
                channel = result["channel"]["name"]
                link = result["link"]
                published = result["publishedTime"]
            searched_text = _["start_6"].format(
                title, duration, views, published, channellink, channel, app.mention
            )
            key = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(text=_["S_B_6"], url=link),
                        InlineKeyboardButton(text=_["S_B_4"], url=config.SUPPORT_CHAT),
                    ],
                ]
            )
            await m.delete()
            await app.send_photo(
                chat_id=message.chat.id,
                photo=thumbnail,
                caption=searched_text,
                reply_markup=key,
            )
            if await is_on_off(2):
                username = f"@{message.from_user.username}" if message.from_user.username else "None"
                return await app.send_message(
                    chat_id=config.LOGGER_ID,
                    text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ ᴛᴏ ᴄʜᴇᴄᴋ <b>ᴛʀᴀᴄᴋ ɪɴғᴏʀᴍᴀᴛɪᴏɴ</b>.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> {username}",
                )
    else:
        # Airbeats.py style animation - PRIVATE CHAT ONLY
        try:
            # Welcome animation
            welcome_msgs = [
                "𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁𝐚𝐛𝐲 ꨄ︎ {}.. ❣️",
                "𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁𝐚𝐛𝐲 ꨄ {}..... 🥳",
                "𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁𝐚𝐛𝐲 ꨄ {}........ 💥",
                "𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁𝐚𝐛𝐲 ꨄ {}.......... 🤩",
                "𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁𝐚𝐛𝐲 ꨄ {}........... 💌",
                "𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁𝐚𝐛𝐲 ꨄ {}............. 💞",
            ]
            
            lol = await message.reply_text(welcome_msgs[0].format(message.from_user.mention))
            for msg in welcome_msgs[1:]:
                await asyncio.sleep(0.3)
                await lol.edit_text(msg.format(message.from_user.mention))
            await lol.delete()
                
        except Exception:
            pass
        
        # 🖼️ Get user profile photo, fallback to config image
        start_photo = None
        try:
            if message.from_user.photo:
                start_photo = await app.download_media(message.from_user.photo.big_file_id)
        except Exception:
            pass
        
        if not start_photo:
            start_photo = random.choice(config.START_IMGS)
        
        # Original start.py buttons for private
        out = private_panel(_)
        
        # Send start message with IMAGE (user photo or fallback)
        await message.reply_photo(
            photo=start_photo,
            caption=_["start_2"].format(message.from_user.mention, app.mention),
            reply_markup=InlineKeyboardMarkup(out),
        )
        
        # Log
        if await is_on_off(2):
            username = f"@{message.from_user.username}" if message.from_user.username else "None"
            await app.send_message(
                chat_id=config.LOGGER_ID,
                text=f"{message.from_user.mention} ᴊᴜsᴛ sᴛᴀʀᴛᴇᴅ ᴛʜᴇ ʙᴏᴛ.\n\n<b>ᴜsᴇʀ ɪᴅ :</b> <code>{message.from_user.id}</code>\n<b>ᴜsᴇʀɴᴀᴍᴇ :</b> {username}",
            )

@app.on_message(filters.command(["start"]) & filters.group & ~BANNED_USERS)
@LanguageStart
async def start_gp(client, message: Message, _):
    # 🔥 PEHLE REACTION BHEJO - GROUP MEIN HAR BAAR
    try:
        reaction_emoji = random.choice(REACTIONS)
        await message.react(reaction_emoji)
    except Exception:
        try:
            await message.react("❤️")
        except:
            pass
    
    # Make sure _ is a dictionary
    if isinstance(_, int):
        language = await get_lang(message.chat.id)
        _ = get_string(language)
    
    # 🔥 STICKER PHIR BHEJO
    try:
        sticker_msg = await message.reply_sticker(random.choice(STICKERS))
        asyncio.create_task(delete_message_after_delay(sticker_msg, 3))
    except Exception:
        pass
    
    out = start_panel(_)
    uptime = int(time.time() - _boot_)
    
    # User profile photo or fallback image
    start_photo = None
    try:
        if message.from_user and message.from_user.photo:
            start_photo = await app.download_media(message.from_user.photo.big_file_id)
    except Exception:
        pass
    
    if not start_photo:
        start_photo = random.choice(config.START_IMGS)
    
    # Direct reply with IMAGE for groups
    await message.reply_photo(
        photo=start_photo,
        caption=_["start_1"].format(app.mention, get_readable_time(uptime)),
        reply_markup=InlineKeyboardMarkup(out),
    )
    
    return await add_served_chat(message.chat.id)


@app.on_message(filters.new_chat_members, group=-1)
async def welcome(client, message: Message):
    for member in message.new_chat_members:
        try:
            language = await get_lang(message.chat.id)
            _ = get_string(language)
            
            if await is_banned_user(member.id):
                try:
                    await message.chat.ban_member(member.id)
                except:
                    pass
                    
            if member.id == app.id:
                if message.chat.type != ChatType.SUPERGROUP:
                    await message.reply_text(_["start_4"])
                    return await app.leave_chat(message.chat.id)
                    
                if message.chat.id in await blacklisted_chats():
                    await message.reply_text(
                        _["start_5"].format(
                            app.mention,
                            f"https://t.me/{app.username}?start=sudolist",
                            config.SUPPORT_CHAT,
                        ),
                        disable_web_page_preview=True,
                    )
                    return await app.leave_chat(message.chat.id)

                # 🔥 Random love/kiss/cute sticker for welcome
                try:
                    await message.reply_sticker(random.choice(STICKERS))
                except Exception:
                    pass

                out = start_panel(_)
                
                # User profile photo or fallback image for welcome
                welcome_photo = None
                try:
                    if message.from_user and message.from_user.photo:
                        welcome_photo = await app.download_media(message.from_user.photo.big_file_id)
                except Exception:
                    pass
                
                if not welcome_photo:
                    welcome_photo = random.choice(config.START_IMGS)
                
                await message.reply_photo(
                    photo=welcome_photo,
                    caption=_["start_3"].format(
                        message.from_user.first_name,
                        app.mention,
                        message.chat.title,
                        app.mention,
                    ),
                    reply_markup=InlineKeyboardMarkup(out),
                )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()
                
        except Exception:
            pass

# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
