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
from PIL import Image

from config import YOUTUBE_IMG_URL
from VISHALMUSIC.core.dir import CACHE_DIR

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
        img = Image.open(thumb_path)
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
