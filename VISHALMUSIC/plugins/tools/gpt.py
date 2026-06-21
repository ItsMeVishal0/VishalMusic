# ANNIEMUSIC/plugins/tools/gpt.py
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
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")  # 👈 .env se load hoga
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

if not OPENROUTER_KEY:
    raise Exception("❌ Missing OPENROUTER_KEY in .env file")

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
    model_map = {
        "ai": "gpt-3.5-turbo",
        "gpt": "gpt-3.5-turbo",
        "bard": "google/gemini-flash-1.5",
        "gemini": "google/gemini-pro",
        "llama": "meta-llama/llama-3-8b-chat",
        "mistral": "mistralai/mistral-7b-instruct",
    }
    cmd = message.command[0].lower()
    model = model_map.get(cmd, "gpt-3.5-turbo")
    try:
        await asyncio.wait_for(process_query(client, message, model=model), timeout=60)
    except asyncio.TimeoutError:
        await message.reply_text("⏳ Timeout. Try again with a shorter prompt.")

# -----------------------------
# ANNIE AI VOICE MODE
# -----------------------------
@app.on_message(filters.command(["assis", "aivoice"], prefixes=["/", ".", "a", "A"]))
async def annie_tts_handler(client: Client, message: Message):
    try:
        await asyncio.wait_for(process_query(client, message, tts=True), timeout=60)
    except asyncio.TimeoutError:
        await message.reply_text("⏳ Timeout. Try again with a shorter prompt.")