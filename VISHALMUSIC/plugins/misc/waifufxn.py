import aiohttp

from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
from nekosbest import Client as NekoClient
from VISHALMUSIC import app

neko_client = NekoClient()

# Actions not available on the main API map to a visually similar reaction.
ALIASES = {
    "highfive": "wave",
    "shoot": "punch",
    "baka": "smug",
    "nod": "smile",
    "nope": "shrug",
    "bored": "yawn",
    "yeet": "shrug",
    "think": "stare",
    "peck": "kiss",
    "lurk": "stare",
}

commands = {
    "punch": {"emoji": "💥", "text": "punched"},
    "slap": {"emoji": "😒", "text": "slapped"},
    "hug": {"emoji": "🤗", "text": "hugged"},
    "bite": {"emoji": "😈", "text": "bit"},
    "kiss": {"emoji": "😘", "text": "kissed"},
    "highfive": {"emoji": "🙌", "text": "high-fived"},
    "shoot": {"emoji": "🔫", "text": "shot"},
    "dance": {"emoji": "💃", "text": "danced"},
    "happy": {"emoji": "😊", "text": "was happy"},
    "baka": {"emoji": "😡", "text": "called you a baka"},
    "pat": {"emoji": "👋", "text": "patted"},
    "nod": {"emoji": "👍", "text": "nodded"},
    "nope": {"emoji": "👎", "text": "said nope"},
    "cuddle": {"emoji": "🤗", "text": "cuddled"},
    "feed": {"emoji": "🍴", "text": "fed"},
    "bored": {"emoji": "😴", "text": "was bored"},
    "nom": {"emoji": "😋", "text": "nommed"},
    "yawn": {"emoji": "😪", "text": "yawned"},
    "facepalm": {"emoji": "🤦", "text": "facepalmed"},
    "tickle": {"emoji": "😆", "text": "tickled"},
    "yeet": {"emoji": "💨", "text": "yeeted"},
    "think": {"emoji": "🤔", "text": "thought"},
    "blush": {"emoji": "😊", "text": "blushed"},
    "smug": {"emoji": "😏", "text": "was smug"},
    "wink": {"emoji": "😉", "text": "winked"},
    "peck": {"emoji": "😘", "text": "pecked"},
    "smile": {"emoji": "😄", "text": "smiled"},
    "wave": {"emoji": "👋", "text": "waved"},
    "poke": {"emoji": "👉", "text": "poked"},
    "stare": {"emoji": "👀", "text": "stared"},
    "shrug": {"emoji": "🤷", "text": "shrugged"},
    "sleep": {"emoji": "😴", "text": "slept"},
    "lurk": {"emoji": "👤", "text": "is lurking"}
}


def md_escape(text: str) -> str:
    return text.replace('[', '\\[').replace(']', '\\]')


async def get_animation(action: str):
    # 1. nekos.best
    try:
        result = await neko_client.get_image(action)
        if result and getattr(result, "url", None):
            return result.url
    except Exception as e:
        print(f"❌ NekoClient error: {e}")

    # 2. otakugifs.xyz — returns Tenor CDN URLs (reachable by Telegram)
    try:
        reaction = ALIASES.get(action, action)
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            async with session.get(
                f"https://api.otakugifs.xyz/gif?reaction={reaction}"
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("url"):
                        return data["url"]
    except Exception as e:
        print(f"❌ otakugifs error: {e}")

    # 3. purrbot.site (covers feed + others)
    try:
        async with aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=10)
        ) as session:
            async with session.get(
                f"https://purrbot.site/api/img/sfw/{action}/gif"
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if data.get("link"):
                        return data["link"]
    except Exception as e:
        print(f"❌ purrbot error: {e}")

    return None


@app.on_message(filters.command(list(commands.keys())) & ~filters.forwarded & ~filters.via_bot)
async def animation_command(client: Client, message: Message):
    command = message.command[0].lower()

    if command not in commands:
        return await message.reply_text("⚠️ That command is not supported.")

    gif_url = await get_animation(command)
    if not gif_url:
        return await message.reply_text("❌ Couldn't fetch the animation. Please try again later.")

    sender_name = md_escape(message.from_user.first_name)
    sender = f"[{sender_name}](tg://user?id={message.from_user.id})"

    if message.reply_to_message:
        target_name = md_escape(message.reply_to_message.from_user.first_name)
        target = f"[{target_name}](tg://user?id={message.reply_to_message.from_user.id})"
    else:
        target = sender

    action_text = commands[command]['text']
    emoji = commands[command]['emoji']

    caption = f"**{sender} {action_text} {target}!** {emoji}"

    await message.reply_animation(
        animation=gif_url,
        caption=caption,
        parse_mode=ParseMode.MARKDOWN
    )
