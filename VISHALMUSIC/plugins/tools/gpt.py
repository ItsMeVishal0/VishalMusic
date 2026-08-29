# VISHALMUSIC/plugins/tools/gpt.py
import asyncio
import os
import aiohttp
from gtts import gTTS
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction
from VISHALMUSIC import app
from dotenv import load_dotenv  # ✅ Added for environment variables

# -----------------------------
# 🧠 Load environment variables
# -----------------------------
load_dotenv()

# ── OpenRouter API Key ─────────────────────────────────────────
# 👇 Option A (hardcoded): apni key yahan paste karo, env var ki zaroorat nahi
#    Example: HARDCODED_OPENROUTER_KEY = "sk-or-v1-xxxxxxxxxxxxxxxx"
HARDCODED_OPENROUTER_KEY = ""  # apni key .env ke OPENROUTER_KEY me daalo

# Option B: ya phir hosting ke env vars me OPENROUTER_KEY set karo
# env var ko priority di gayi hai (hardcoded sirf fallback hai)
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY") or HARDCODED_OPENROUTER_KEY
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# NOTE: no module-level raise here — a missing key must NOT crash the whole
# bot at startup. Commands reply with a setup hint instead.

# -----------------------------
# 🔧 GPT API — OpenRouter
# -----------------------------
async def get_gpt_response(prompt: str, model: str = "gpt-3.5-turbo") -> str:
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENROUTER_KEY}",
        }
        data = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(OPENROUTER_URL, headers=headers, json=data, timeout=60) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise Exception(f"API Error {resp.status}: {text}")
                result = await resp.json()
                return result["choices"][0]["message"]["content"]
    except Exception as e:
        raise Exception(f"❌ GPT Error: {e}")

# -----------------------------
async def safe_gpt_response(prompt: str, timeout: int = 30) -> str:
    try:
        return await asyncio.wait_for(get_gpt_response(prompt), timeout=timeout)
    except asyncio.TimeoutError:
        raise Exception("⚠️ GPT request timed out.")
    except Exception as e:
        raise Exception(str(e))

async def send_typing_action(client: Client, chat_id: int, interval: int = 3):
    try:
        while True:
            await client.send_chat_action(chat_id, ChatAction.TYPING)
            await asyncio.sleep(interval)
    except asyncio.CancelledError:
        pass

def _build_fullname(first_name, last_name, username):
    first = first_name or ""
    last = (last_name or "").strip()
    full = (f"{first} {last}".strip()) or (f"@{username}" if username else "")
    return full or "there"

def _user_mention_text(user):
    full = _build_fullname(
        getattr(user, "first_name", None),
        getattr(user, "last_name", None),
        getattr(user, "username", None),
    )
    mention_attr = getattr(user, "mention", None)
    if callable(mention_attr):
        try:
            return mention_attr(full)
        except Exception:
            pass
    return f"[{full}](tg://user?id={user.id})"

def get_requester_identity(message: Message):
    if message.from_user:
        u = message.from_user
        full = _build_fullname(u.first_name, getattr(u, "last_name", None), getattr(u, "username", None))
        return full, _user_mention_text(u)
    if message.sender_chat:
        title = message.sender_chat.title or "there"
        return title, title
    return "there", "there"

# -----------------------------
async def process_query(client: Client, message: Message, tts: bool = False, model: str = "gpt-3.5-turbo"):
    full, mention = get_requester_identity(message)
    if len(message.command) < 2:
        return await message.reply_text(f"✨ ʜᴇʏ {mention}, ɪ’ᴍ ˹𝐀ɴɴɪᴇ ✘ 𝙰ɪ˼ 💫\nAsk me anything!")

    query = message.text.split(" ", 1)[1].strip()
    if len(query) > 4000:
        return await message.reply_text("❌ Prompt too long (max 4000 chars).")

    audio_file = "response.mp3"
    typing_task = asyncio.create_task(send_typing_action(client, message.chat.id))

    try:
        content = await safe_gpt_response(query, timeout=40)
        if not content:
            return await message.reply_text("⚠️ No response from GPT.")

        styled = (
            f"✨ ʜᴇʏ {mention},\n"
            f"ɪ’ᴍ ˹𝐀ɴɴɪᴇ ✘ 𝙰ɪ˼ 💫\n"
            f"──────────────\n"
            f"🧠 ʀᴇsᴘᴏɴsᴇ:\n{content}"
        )

        if tts:
            try:
                tts_engine = gTTS(text=content[:1000], lang="en")
                tts_engine.save(audio_file)
                await client.send_voice(
                    chat_id=message.chat.id,
                    voice=audio_file,
                    caption=styled
                )
            except Exception as tts_error:
                await message.reply_text(f"❌ Voice generation error: {tts_error}")
        else:
            for i in range(0, len(styled), 4096):
                await message.reply_text(styled[i:i+4096])

    except Exception as e:
        await message.reply_text(str(e))
    finally:
        typing_task.cancel()
        if os.path.exists(audio_file):
            try:
                os.remove(audio_file)
            except:
                pass

# -----------------------------
# COMMANDS
# -----------------------------
@app.on_message(filters.command(["ai", "gpt", "bard", "gemini", "llama", "mistral"], prefixes=["/", ".", "-", "+", "?", "$"]))
async def gpt_handler(client: Client, message: Message):
    if not OPENROUTER_KEY:
        return await message.reply_text(
            "❌ AI ɪs ɴᴏᴛ ᴄᴏɴꜰɪɢᴜʀᴇᴅ.\n\n"
            "Gᴇᴛ ᴀ ꜰʀᴇᴇ ᴋᴇʏ ᴀᴛ openrouter.ai/keys ᴀᴜʀ ᴜsᴇ "
            "`VISHALMUSIC/plugins/tools/gpt.py` ᴋᴇ ᴛᴏᴘ ᴘᴀʀ "
            "`HARDCODED_OPENROUTER_KEY` ᴍᴇ ᴘᴀsᴛᴇ ᴋᴀʀᴏ, "
            "ᴘʜɪʀ ʙᴏᴛ ʀᴇsᴛᴀʀᴛ ᴋᴀʀᴏ."
        )
    # Current OpenRouter model IDs (old IDs like gpt-3.5-turbo are deprecated)
    model_map = {
        "ai": "openrouter/free",
        "gpt": "openai/gpt-4o-mini",
        "bard": "google/gemini-3.7-flash",
        "gemini": "google/gemini-3.7-flash",
        "llama": "meta-llama/llama-4-maverick",
        "mistral": "mistralai/mistral-medium-3-5",
    }
    cmd = message.command[0].lower()
    model = model_map.get(cmd, "openrouter/free")
    try:
        await asyncio.wait_for(process_query(client, message, model=model), timeout=60)
    except asyncio.TimeoutError:
        await message.reply_text("⏳ Timeout. Try again with a shorter prompt.")

# -----------------------------
# VISHAL AI VOICE MODE
# -----------------------------
@app.on_message(filters.command(["assis", "aivoice"], prefixes=["/", ".", "a", "A"]))
async def vishal_tts_handler(client: Client, message: Message):
    try:
        await asyncio.wait_for(process_query(client, message, tts=True), timeout=60)
    except asyncio.TimeoutError:
        await message.reply_text("⏳ Timeout. Try again with a shorter prompt.")