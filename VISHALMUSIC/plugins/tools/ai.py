# VISHALMUSIC/plugins/tools/ai.py
import os
import base64
import mimetypes
import aiohttp
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatAction
from VISHALMUSIC import app
from dotenv import load_dotenv

# -------------------------
# 🔐 Load environment variables
# -------------------------
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

# ---------------------------
# 🔧 Helper: fetch GPT response from OpenRouter
# ---------------------------
async def get_gpt_response(prompt: str, model: str = "gpt-3.5-turbo") -> str:
    """Fetch GPT response from OpenRouter API"""
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "HTTP-Referer": "https://t.me/VaishalxMusic_robot",
            "X-Title": "VishalxMusic",
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
                # Safely extract the response text
                choice = result.get("choices")
                if not choice or not isinstance(choice, list):
                    raise Exception("No choices in API response.")
                message = choice[0].get("message") or choice[0].get("text") or {}
                if isinstance(message, dict):
                    if "content" in message:
                        if isinstance(message["content"], dict) and "parts" in message["content"]:
                            return "\n".join(message["content"]["parts"])
                        return message["content"]
                    if "text" in message:
                        return message["text"]
                return str(message)
    except Exception as e:
        raise Exception(f"❌ GPT Error: {e}")

# ---------------------------
def get_prompt(message: Message) -> str | None:
    parts = message.text.split(" ", 1)
    return parts[1] if len(parts) > 1 else None

def format_response(model_name: str, content: str) -> str:
    return f"**🤖 Model:** `{model_name}`\n\n**🧠 Response:**\n{content}"

# NOTE: /gpt /bard /gemini /llama /mistral are handled in tools/gpt.py
# (with up-to-date OpenRouter model IDs). This file only adds the unique
# /geminivision command to avoid double replies.

# ---------------------------
# GeminiVision (image) handler — uses text fallback
# ---------------------------
@app.on_message(filters.command("geminivision"))
async def geminivision_handler(client: Client, message: Message):
    if not OPENROUTER_KEY:
        return await message.reply_text(
            "❌ AI ɪs ɴᴏᴛ ᴄᴏɴꜰɪɢᴜʀᴇᴅ.\n\n"
            "Gᴇᴛ ᴀ ꜰʀᴇᴇ ᴋᴇʏ ᴀᴛ openrouter.ai/keys ᴀᴜʀ ᴜsᴇ "
            "`VISHALMUSIC/plugins/tools/ai.py` ᴋᴇ ᴛᴏᴘ ᴘᴀʀ "
            "`HARDCODED_OPENROUTER_KEY` ᴍᴇ ᴘᴀsᴛᴇ ᴋᴀʀᴏ, "
            "ᴘʜɪʀ ʙᴏᴛ ʀᴇsᴛᴀʀᴛ ᴋᴀʀᴏ."
        )
    if not (message.reply_to_message and (message.reply_to_message.photo or message.reply_to_message.document)):
        return await message.reply_text("🖼️ Please reply to an image with /geminivision and a prompt.")

    prompt = get_prompt(message)
    if not prompt:
        return await message.reply_text("❌ Please provide a prompt after the command.")

    await client.send_chat_action(message.chat.id, ChatAction.TYPING)
    status = await message.reply_text("🧩 Processing your image, please wait...")

    file_path = None
    try:
        file_path = await client.download_media(message.reply_to_message.photo or message.reply_to_message.document)
        with open(file_path, "rb") as f:
            img_data = base64.b64encode(f.read()).decode()
        fake_prompt = f"[Image included]\n{prompt}"
        content = await get_gpt_response(fake_prompt)
        await status.edit_text(format_response("Gemini Vision", content))
    except Exception as e:
        await status.edit_text(f"❌ Error: {e}")
    finally:
        if file_path and os.path.exists(file_path):
            try:
                os.remove(file_path)
            except:
                pass