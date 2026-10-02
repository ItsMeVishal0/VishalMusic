# ═══════════════════════════════════════════════════════════
#        🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   GɪᴛHᴜʙ : github.com/ItsMeVishal0/VishalMusic
#   Dᴇᴠʟᴏᴘᴇʀ : @ItsMeVishalBots | Telegram
# ═══════════════════════════════════════════════════════════

import asyncio
import os
import sys
from pyrogram import Client, errors
from pyrogram.enums import ChatMemberStatus
from pyrogram.types import BotCommand

import config
from ..logging import LOGGER


class VISHAL(Client):
    def __init__(self):
        # Optimized workers & concurrency for low CPU & RAM overhead
        cpu_n = os.cpu_count() or 1
        opt_workers = min(16, max(4, cpu_n * 2))
        super().__init__(
            name="VishaLMusic",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            workers=opt_workers,
            max_concurrent_transmissions=3,
            sleep_threshold=60,
        )
        LOGGER(__name__).info(f"Bot client initialized (workers={opt_workers}).")

    async def start(self):
        while True:
            try:
                await super().start()
                break
            except errors.FloodWait as e:
                LOGGER(__name__).warning(f"⚠️ Telegram FloodWait detected. Waiting for {e.value}s...")
                await asyncio.sleep(e.value + 1)
            except Exception as e:
                LOGGER(__name__).error(f"❌ Failed to start Bot client: {e}")
                raise e

        me = await self.get_me()
        self.username, self.id = me.username, me.id
        self.name = f"{me.first_name} {me.last_name or ''}".strip()
        self.mention = me.mention

        try:
            await self.set_bot_commands(
                [
                    BotCommand("start", "⚡ ꜱᴛᴀʀᴛ ᴛʜᴇ ʙᴏᴛ"),
                    BotCommand("help", "📖 ɢᴇᴛ ʜᴇʟᴘ ᴍᴇɴᴜ"),
                    BotCommand("play", "🎵 ᴘʟᴀʏ ᴀ sᴏɴɢ ɪɴ ᴠᴄ"),
                    BotCommand("vplay", "🎬 ᴘʟᴀʏ ᴠɪᴅᴇᴏ ɪɴ ᴠᴄ"),
                    BotCommand("stop", "⏹ sᴛᴏᴘ sᴛʀᴇᴀᴍɪɴɢ"),
                    BotCommand("pause", "⏸ ᴘᴀᴜsᴇ ᴛʜᴇ sᴛʀᴇᴀᴍ"),
                    BotCommand("resume", "▶ ʀᴇsᴜᴍᴇ ᴛʜᴇ sᴛʀᴇᴀᴍ"),
                    BotCommand("skip", "⏭ sᴋɪᴘ ᴛᴏ ɴᴇxᴛ sᴏɴɢ"),
                    BotCommand("queue", "📜 sʜᴏᴡ ǫᴜᴇᴜᴇ ʟɪsᴛ"),
                    BotCommand("loop", "🔄 ʟᴏᴏᴘ ᴄᴜʀʀᴇɴᴛ sᴏɴɢ"),
                    BotCommand("shuffle", "🔀 sʜᴜғғʟᴇ ᴛʜᴇ ǫᴜᴇᴜᴇ"),
                    BotCommand("seek", "⏩ sᴇᴇᴋ ɪɴ ᴄᴜʀʀᴇɴᴛ sᴏɴɢ"),
                    BotCommand("speed", "🎚 ᴄʜᴀɴɢᴇ ᴘʟᴀʏʙᴀᴄᴋ sᴘᴇᴇᴅ"),
                    BotCommand("song", "📥 ᴅᴏᴡɴʟᴏᴀᴅ sᴏɴɢ"),
                    BotCommand("lock", "🔒 ʟᴏᴄᴋ ᴀ ᴄᴏɴᴛᴇɴᴛ ᴛʏᴘᴇ"),
                    BotCommand("unlock", "🔓 ᴜɴʟᴏᴄᴋ ᴀ ᴄᴏɴᴛᴇɴᴛ ᴛʏᴘᴇ"),
                    BotCommand("vclogger", "📢 ᴠᴄ ʟᴏɢɢᴇʀ ᴏɴ/ᴏғғ"),
                ]
            )
            LOGGER(__name__).info("Bot commands menu registered successfully.")
        except Exception as e:
            LOGGER(__name__).warning(f"Could not set bot commands: {e}")

        try:
            await self.send_message(
                config.LOGGER_ID,
                (
                    f"<u><b>» {self.mention} ʙᴏᴛ sᴛᴀʀᴛᴇᴅ :</b></u>\n\n"
                    f"ɪᴅ : <code>{self.id}</code>\n"
                    f"ɴᴀᴍᴇ : {self.name}\n"
                    f"ᴜsᴇʀɴᴀᴍᴇ : @{self.username}"
                ),
            )
        except (errors.ChannelInvalid, errors.PeerIdInvalid):
            # Log group accessible na ho to bot exit na ho — sirf log miss hoga.
            LOGGER(__name__).warning("⚠️ Bot cannot access the log group/channel – continuing without it.")
            return
        except Exception as exc:
            LOGGER(__name__).warning(f"⚠️ Bot failed to access the log group: {type(exc).__name__} – continuing.")
            return

        try:
            member = await self.get_chat_member(config.LOGGER_ID, self.id)
            if member.status != ChatMemberStatus.ADMINISTRATOR:
                LOGGER(__name__).warning("⚠️ Bot is not admin in the log group/channel – continuing without it.")
                return
        except Exception as e:
            LOGGER(__name__).warning(f"⚠️ Could not check log group admin status: {e} – continuing.")
            return

        LOGGER(__name__).info(f"✅ Music Bot started as {self.name} (@{self.username})")

# ═══════════════════════════════════════════════════════════
#         🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
