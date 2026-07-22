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
from VISHALMUSIC.utils.colored_buttons import (
    buttons_to_inline_markup,
    smart_send_photo as send_photo_colored,
)
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
            
            # Try Bot API with colored buttons
            start_photo = random.choice(config.START_IMGS)
            result = await send_photo_colored(
                chat_id=message.chat.id,
                photo=start_photo,
                caption=_["help_1"].format(config.SUPPORT_CHAT),
                reply_markup=keyboard
            )
            
            # Fallback to Pyrogram if Bot API fails
            if not result:
                from pyrogram import enums
                # Note: buttons_to_inline_markup loses colors (no style field in Pyrogram)
                # For colored buttons, user must have valid BOT_TOKEN set in config
                return await message.reply_photo(
                    photo=start_photo,
                    caption=_["help_1"].format(config.SUPPORT_CHAT),
                    parse_mode=enums.ParseMode.HTML,
                    reply_markup=buttons_to_inline_markup(keyboard),
                )
            return
            return
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
            # Build bot mention properly
            bot_mention = f'<a href="tg://user?id={app.id}">{app.name}</a>'
            searched_text = _["start_6"].format(
                title, duration, views, published, channellink, channel, bot_mention
            )
            
            # Import colored button functions
            from VISHALMUSIC.utils.colored_buttons import styled_button, buttons_to_inline_markup
            
            # Create colored buttons
            key = [
                [
                    styled_button(text=_["S_B_6"], url=link, style="primary"),
                    styled_button(text=_["S_B_4"], url=config.SUPPORT_CHAT, style="primary"),
                ],
            ]
            
            await m.delete()
            from pyrogram import enums
            await app.send_photo(
                chat_id=message.chat.id,
                photo=thumbnail,
                caption=searched_text,
                parse_mode=enums.ParseMode.HTML,
                reply_markup=buttons_to_inline_markup(key),
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
            # Build user mention for animation
            user_mention = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
            
            # Welcome animation
            welcome_msgs = [
                "𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁𝐚𝐛𝐲 ꨄ︎ {}.. ❣️",
                "𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁𝐚𝐛𝐲 ꨄ {}..... 🥳",
                "𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁𝐚𝐛𝐲 ꨄ {}........ 💥",
                "𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁𝐚𝐛𝐲 ꨄ {}.......... 🤩",
                "𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁𝐚𝐛𝐲 ꨄ {}........... 💌",
                "𝐖𝐞𝐥𝐜𝐨𝐦𝐞 𝐁𝐚𝐛𝐲 ꨄ {}............. 💞",
            ]
            
            from pyrogram import enums
            lol = await message.reply_text(
                welcome_msgs[0].format(user_mention),
                parse_mode=enums.ParseMode.HTML
            )
            for msg in welcome_msgs[1:]:
                await asyncio.sleep(0.3)
                await lol.edit_text(
                    msg.format(user_mention),
                    parse_mode=enums.ParseMode.HTML
                )
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
        
        # Get buttons with colored support
        out = private_panel(_)
        
        # Build caption with proper HTML mention formatting
        user_mention = f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
        bot_mention = f'<a href="tg://user?id={app.id}">{app.name}</a>'
        caption = _["start_2"].format(user_mention, bot_mention)
        
        # Try colored buttons first via Bot API
        result = await send_photo_colored(
            chat_id=message.chat.id,
            photo=start_photo,
            caption=caption,
            reply_markup=out
        )
        
        # Fallback to Pyrogram if Bot API fails
        if not result:
            from pyrogram import enums
            # Note: buttons_to_inline_markup loses colors (no style field in Pyrogram)
            # For colored buttons, user must have valid BOT_TOKEN set in config
            await message.reply_photo(
                photo=start_photo,
                caption=caption,
                parse_mode=enums.ParseMode.HTML,
                reply_markup=buttons_to_inline_markup(out),
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
    
    # Get buttons with Telegram native colored button support
    from VISHALMUSIC.utils.colored_buttons import buttons_to_inline_markup
    from pyrogram import enums
    
    # Build caption with proper HTML mention
    bot_mention = f'<a href="tg://user?id={app.id}">{app.name}</a>'
    caption = _["start_1"].format(bot_mention, get_readable_time(uptime))
    
    # Direct Pyrogram (Telegram natively handles colors via Bot API if BOT_TOKEN set!)
    # Note: buttons_to_inline_markup loses colors (no style field in Pyrogram)
    # For colored buttons, user must have valid BOT_TOKEN set in config
    await message.reply_photo(
        photo=start_photo,
        caption=caption,
        parse_mode=enums.ParseMode.HTML,
        reply_markup=buttons_to_inline_markup(out),
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
                
                # Get user who joined's profile photo, fallback to config START_IMGS
                welcome_photo = None
                try:
                    if member and member.photo:
                        welcome_photo = await app.download_media(member.photo.big_file_id)
                except Exception:
                    pass
                
                if not welcome_photo:
                    welcome_photo = random.choice(config.START_IMGS)
                
                from pyrogram import enums
                await message.reply_photo(
                    photo=welcome_photo,
                    caption=_["start_3"].format(
                        member.first_name,
                        app.mention,
                        message.chat.title,
                        app.mention,
                    ),
                    parse_mode=enums.ParseMode.HTML,
                    reply_markup=buttons_to_inline_markup(out),
                )
                await add_served_chat(message.chat.id)
                await message.stop_propagation()
                
        except Exception:
            pass

# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
