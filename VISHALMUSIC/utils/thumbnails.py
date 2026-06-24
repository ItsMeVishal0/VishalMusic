# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   GitHub : github.com/ItsMeVishal0/VishalMusic
#   Developer : @ItsMeVishalBots | Telegram
#   Module : Thumbnail Generation for Now Playing
# ═══════════════════════════════════════════════════════════

import asyncio
import os
from typing import Optional

import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageFont

from config import YOUTUBE_IMG_URL
from VISHALMUSIC.core.dir import CACHE_DIR

# Branding font
_FONT_PATH = os.path.join(os.path.dirname(__file__), "..", "assets", "default.ttf")
_BRAND_TEXT = "VishalMusic"

# Shared persistent session — created once, reused forever
_thumb_session: Optional[aiohttp.ClientSession] = None
_thumb_session_lock = asyncio.Lock()

async def _get_session() -> aiohttp.ClientSession:
    global _thumb_session
    if _thumb_session and not _thumb_session.closed:
        return _thumb_session
    async with _thumb_session_lock:
        if _thumb_session and not _thumb_session.closed:
            return _thumb_session
        connector = aiohttp.TCPConnector(limit=32, ttl_dns_cache=300)
        timeout = aiohttp.ClientTimeout(total=15, sock_connect=5, sock_read=10)
        _thumb_session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return _thumb_session


async def get_thumb(videoid: str) -> str:
    cache_path = os.path.join(CACHE_DIR, f"{videoid}_original.png")
    if os.path.exists(cache_path):
        return cache_path

    thumbnail_urls = [
        f"https://img.youtube.com/vi/{videoid}/maxresdefault.jpg",
        f"https://img.youtube.com/vi/{videoid}/hqdefault.jpg",
        f"https://img.youtube.com/vi/{videoid}/sddefault.jpg",
        f"https://img.youtube.com/vi/{videoid}/mqdefault.jpg",
    ]

    session = await _get_session()
    thumb_path = os.path.join(CACHE_DIR, f"thumb{videoid}.jpg")
    downloaded = False

    for url in thumbnail_urls:
        try:
            async with session.get(url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(thumb_path, "wb") as f:
                        await f.write(await resp.read())
                    downloaded = True
                    break
        except Exception:
            continue

    if not downloaded:
        return YOUTUBE_IMG_URL

    try:
        img = Image.open(thumb_path).convert("RGBA")

        # Add branding text on top-right corner
        try:
            draw = ImageDraw.Draw(img)
            font_size = max(16, img.width // 30)
            try:
                font = ImageFont.truetype(_FONT_PATH, font_size)
            except Exception:
                font = ImageFont.load_default()

            bbox = draw.textbbox((0, 0), _BRAND_TEXT, font=font)
            text_w = bbox[2] - bbox[0]
            text_h = bbox[3] - bbox[1]

            padding = 8
            x = img.width - text_w - padding - 10
            y = padding + 5

            # Semi-transparent background behind text
            overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
            overlay_draw = ImageDraw.Draw(overlay)
            overlay_draw.rounded_rectangle(
                [x - padding, y - padding // 2, x + text_w + padding, y + text_h + padding // 2],
                radius=6,
                fill=(0, 0, 0, 120),
            )
            img = Image.alpha_composite(img, overlay)

            # Draw text
            draw = ImageDraw.Draw(img)
            draw.text((x, y), _BRAND_TEXT, fill=(255, 255, 255, 230), font=font)
        except Exception:
            pass

        img = img.convert("RGB")
        img.save(cache_path)
    except Exception:
        return YOUTUBE_IMG_URL
    finally:
        try:
            os.remove(thumb_path)
        except OSError:
            pass

    return cache_path

# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
