# ANNIEMUSIC/plugins/tools/ai.py
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
OPENROUTER_KEY = os.getenv("OPENROUTER_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

if not OPENROUTER_KEY:
    raise ValueError("❌ OpenRouter key not found! Please set OPENROUTER_KEY in your .env file.")

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

# ---------------------------
async def handle_text_model(message: Message, model_name: str):
    prompt = get_prompt(message)
    if not prompt:
        return await message.reply_text("❌ Please provide a prompt after the command.")

    await message._client.send_chat_action(message.chat.id, ChatAction.TYPING)
    status = await message.reply_text("💬 Thinking...")

    try:
        content = await asyncio.wait_for(get_gpt_response(prompt), timeout=60)
        if not content:
            await status.edit_text("⚠️ No response from GPT.")
        else:
            await status.edit_text(format_response(model_name, content))
    except Exception as e:
        await status.edit_text(f"❌ {e}")

# ---------------------------
# Command Handlers
# ---------------------------
@app.on_message(filters.command("gpt"))
async def gpt_handler(client: Client, message: Message):
    await handle_text_model(message, "GPT")

@app.on_message(filters.command("bard"))
async def bard_handler(client: Client, message: Message):
    await handle_text_model(message, "Bard")

@app.on_message(filters.command("gemini"))
async def gemini_handler(client: Client, message: Message):
    await handle_text_model(message, "Gemini")

@app.on_message(filters.command("llama"))
async def llama_handler(client: Client, message: Message):
    await handle_text_model(message, "LLaMA")

@app.on_message(filters.command("mistral"))
async def mistral_handler(client: Client, message: Message):
    await handle_text_model(message, "Mistral")

# ---------------------------
# GeminiVision (image) handler — uses text fallback
# ---------------------------
@app.on_message(filters.command("geminivision"))
async def geminivision_handler(client: Client, message: Message):
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