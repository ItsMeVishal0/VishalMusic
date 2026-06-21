# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   GitHub : github.com/ItsMeVishal0/VishalMusic
#   Developer : @ItsMeVishalBots | Telegram
#   Module : YouTube Search, Download & Streaming
# ═══════════════════════════════════════════════════════════

import asyncio
import contextlib
import json
import os
import re
import time
import aiofiles
import aiohttp
import shutil
from typing import Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from py_yt import VideosSearch

from VISHALMUSIC.utils.cookie_handler import COOKIE_PATH
from VISHALMUSIC.utils.database import is_on_off
from VISHALMUSIC.utils.downloader import download_audio_concurrent, yt_dlp_download
from VISHALMUSIC.utils.errors import capture_internal_err
from VISHALMUSIC.utils.formatters import time_to_seconds
from VISHALMUSIC.utils.tuning import (
    YTDLP_TIMEOUT,
    YOUTUBE_META_MAX,
    YOUTUBE_META_TTL,
)
from VISHALMUSIC import LOGGER

_cache: Dict[str, Tuple[float, List[Dict]]] = {}
_cache_lock = asyncio.Lock()
_formats_cache: Dict[str, Tuple[float, List[Dict], str]] = {}
_formats_lock = asyncio.Lock()

# ============ API CONFIGURATION ============
SHRUTI_API_KEY = "ShrutiBotsL0zQEKsazSrYS2LWsIQW"

# API 1: Primary Shruti API (Direct Download)
PRIMARY_API_URL = "https://api.shrutibots.site"
# Endpoint: /download?url={video_id}&type=audio&api_key={KEY}
# Response: Direct file download

# API 2: Legacy/Fallback API (Token Based)
FALLBACK_API_URL = ""
# Endpoint 1: /download?url={video_id}&type=audio -> returns {"download_token": "xxx"}
# Endpoint 2: /stream/{video_id}?type=audio with header X-Download-Token

# API URLs loaded status
PRIMARY_API_LOADED = False
FALLBACK_API_LOADED = False

# ============ RATE LIMITING (async â€” does NOT block the event loop) ============
_request_timestamps = []
_RATE_LIMIT_WINDOW = 60
_MAX_REQUESTS_PER_WINDOW = 10
_rate_limit_lock = asyncio.Lock()

async def _check_rate_limit_async():
    """Non-blocking async rate-limit guard (replaces the old blocking time.sleep)."""
    global _request_timestamps
    async with _rate_limit_lock:
        now = time.time()
        _request_timestamps = [ts for ts in _request_timestamps if now - ts < _RATE_LIMIT_WINDOW]
        if len(_request_timestamps) >= _MAX_REQUESTS_PER_WINDOW:
            sleep_time = _RATE_LIMIT_WINDOW - (now - _request_timestamps[0])
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
            _request_timestamps = []
        _request_timestamps.append(time.time())


# â”€â”€ Shared persistent HTTP session for all API calls â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
_yt_session: aiohttp.ClientSession = None
_yt_session_lock = asyncio.Lock()

async def _get_yt_session() -> aiohttp.ClientSession:
    global _yt_session
    if _yt_session and not _yt_session.closed:
        return _yt_session
    async with _yt_session_lock:
        if _yt_session and not _yt_session.closed:
            return _yt_session
        connector = aiohttp.TCPConnector(limit=32, ttl_dns_cache=300, enable_cleanup_closed=True)
        timeout = aiohttp.ClientTimeout(total=300, sock_connect=10, sock_read=60)
        _yt_session = aiohttp.ClientSession(connector=connector, timeout=timeout)
        return _yt_session


async def load_apis():
    """Load and verify APIs â€” only checks non-empty URLs."""
    global PRIMARY_API_LOADED, FALLBACK_API_LOADED
    logger = LOGGER("VISHALMUSIC.platforms.Youtube.py")

    if PRIMARY_API_URL:
        try:
            session = await _get_yt_session()
            async with session.get(f"{PRIMARY_API_URL}/", timeout=aiohttp.ClientTimeout(total=8)) as response:
                if response.status == 200:
                    PRIMARY_API_LOADED = True
                    logger.info(f"âœ… PRIMARY API loaded: {PRIMARY_API_URL}")
                else:
                    logger.warning(f"âš ï¸ Primary API status {response.status}")
        except Exception as e:
            logger.warning(f"âš ï¸ Primary API unreachable: {e}")

    if FALLBACK_API_URL:  # only check when a URL is actually configured
        try:
            session = await _get_yt_session()
            async with session.get(f"{FALLBACK_API_URL}/", timeout=aiohttp.ClientTimeout(total=8)) as response:
                if response.status == 200:
                    FALLBACK_API_LOADED = True
                    logger.info(f"âœ… FALLBACK API loaded: {FALLBACK_API_URL}")
        except Exception as e:
            logger.warning(f"âš ï¸ Fallback API unreachable: {e}")

    return PRIMARY_API_LOADED, FALLBACK_API_LOADED

# Initialize APIs on startup
try:
    loop = asyncio.get_event_loop()
    if loop.is_running():
        asyncio.create_task(load_apis())
    else:
        loop.run_until_complete(load_apis())
except RuntimeError:
    pass

def _cookiefile_path() -> Optional[str]:
    path = str(COOKIE_PATH)
    try:
        if path and os.path.exists(path) and os.path.getsize(path) > 0:
            return path
    except Exception:
        pass
    return None

def _cookies_args() -> List[str]:
    p = _cookiefile_path()
    return ["--cookies", p] if p else []

async def _exec_proc(*args: str) -> Tuple[bytes, bytes]:
    proc = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    try:
        return await asyncio.wait_for(proc.communicate(), timeout=YTDLP_TIMEOUT)
    except asyncio.TimeoutError:
        with contextlib.suppress(Exception):
            proc.kill()
        return b"", b"timeout"

# Legacy sync alias removed â€” use _check_rate_limit_async() everywhere

# ============ API 1: PRIMARY SHRUTI API (DIRECT DOWNLOAD) ============
async def download_song_primary_api(link: str) -> str:
    """Primary Shruti API - Direct download with API key (shared session, 1 MB chunks)."""
    if not PRIMARY_API_URL:
        return None
    video_id = link.split('v=')[-1].split('&')[0] if 'v=' in link else link
    if not video_id or len(video_id) < 3:
        return None

    DOWNLOAD_DIR = "downloads"
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp3")

    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return file_path

    try:
        session = await _get_yt_session()
        params = {"url": video_id, "type": "audio", "api_key": SHRUTI_API_KEY}
        async with session.get(
            f"{PRIMARY_API_URL}/download",
            params=params,
            timeout=aiohttp.ClientTimeout(total=120),
        ) as response:
            if response.status != 200:
                return None
            async with aiofiles.open(file_path, "wb") as f:
                async for chunk in response.content.iter_chunked(1 << 20):  # 1 MB
                    await f.write(chunk)

        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return file_path
        return None
    except Exception:
        return None


async def download_video_primary_api(link: str) -> str:
    """Primary Shruti API - Video download with API key (shared session, 1 MB chunks)."""
    if not PRIMARY_API_URL:
        return None
    video_id = link.split('v=')[-1].split('&')[0] if 'v=' in link else link
    if not video_id or len(video_id) < 3:
        return None

    DOWNLOAD_DIR = "downloads"
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp4")

    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return file_path

    try:
        session = await _get_yt_session()
        params = {"url": video_id, "type": "video", "api_key": SHRUTI_API_KEY}
        async with session.get(
            f"{PRIMARY_API_URL}/download",
            params=params,
            timeout=aiohttp.ClientTimeout(total=180),
        ) as response:
            if response.status != 200:
                return None
            async with aiofiles.open(file_path, "wb") as f:
                async for chunk in response.content.iter_chunked(1 << 20):  # 1 MB
                    await f.write(chunk)

        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return file_path
        return None
    except Exception:
        return None


# ============ API 2: LEGACY/FALLBACK API (TOKEN BASED) ============
async def download_song_fallback_api(link: str) -> str:
    """Legacy/Fallback API - Token based download (shared session, 1 MB chunks)."""
    if not FALLBACK_API_URL:
        return None
    video_id = link.split('v=')[-1].split('&')[0] if 'v=' in link else link
    if not video_id or len(video_id) < 3:
        return None

    DOWNLOAD_DIR = "downloads"
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp3")
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return file_path

    try:
        session = await _get_yt_session()
        # Step 1: get token
        async with session.get(
            f"{FALLBACK_API_URL}/download",
            params={"url": video_id, "type": "audio"},
            timeout=aiohttp.ClientTimeout(total=30),
        ) as response:
            if response.status != 200:
                return None
            data = await response.json()
            download_token = data.get("download_token")
            if not download_token:
                return None

        # Step 2: stream file
        async with session.get(
            f"{FALLBACK_API_URL}/stream/{video_id}?type=audio",
            headers={"X-Download-Token": download_token},
            timeout=aiohttp.ClientTimeout(total=300),
        ) as file_response:
            if file_response.status != 200:
                return None
            async with aiofiles.open(file_path, "wb") as f:
                async for chunk in file_response.content.iter_chunked(1 << 20):
                    await f.write(chunk)

        return file_path if os.path.exists(file_path) and os.path.getsize(file_path) > 0 else None
    except Exception:
        return None


async def download_video_fallback_api(link: str) -> str:
    """Legacy/Fallback API - Video download with token (shared session, 1 MB chunks)."""
    if not FALLBACK_API_URL:
        return None
    video_id = link.split('v=')[-1].split('&')[0] if 'v=' in link else link
    if not video_id or len(video_id) < 3:
        return None

    DOWNLOAD_DIR = "downloads"
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp4")
    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        return file_path

    try:
        session = await _get_yt_session()
        # Step 1: get token
        async with session.get(
            f"{FALLBACK_API_URL}/download",
            params={"url": video_id, "type": "video"},
            timeout=aiohttp.ClientTimeout(total=30),
        ) as response:
            if response.status != 200:
                return None
            data = await response.json()
            download_token = data.get("download_token")
            if not download_token:
                return None

        # Step 2: stream file
        async with session.get(
            f"{FALLBACK_API_URL}/stream/{video_id}?type=video",
            headers={"X-Download-Token": download_token},
            timeout=aiohttp.ClientTimeout(total=600),
        ) as file_response:
            if file_response.status != 200:
                return None
            async with aiofiles.open(file_path, "wb") as f:
                async for chunk in file_response.content.iter_chunked(1 << 20):
                    await f.write(chunk)

        return file_path if os.path.exists(file_path) and os.path.getsize(file_path) > 0 else None
    except Exception:
        return None


# ============ YT-DLP FALLBACK ============
async def download_video_ytdlp(link: str) -> str:
    """Download video using yt-dlp directly"""
    video_id = link.split('v=')[-1].split('&')[0] if 'v=' in link else link

    if not video_id or len(video_id) < 3:
        return None

    DOWNLOAD_DIR = "downloads"
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.mp4")

    if os.path.exists(file_path) and os.path.getsize(file_path) > 10240:
        return file_path

    await _check_rate_limit_async()

    try:
        ytdlp_opts = [
            "yt-dlp",
            *(_cookies_args()),
            "--no-warnings",
            "--geo-bypass",
            "--force-ipv4",
            "-f",
            "best[height<=?720][width<=?1280]/best",
            "-o",
            file_path,
            link
        ]
        
        stdout, stderr = await _exec_proc(*ytdlp_opts)
        
        if os.path.exists(file_path) and os.path.getsize(file_path) > 10240:
            return file_path
        else:
            alternative_formats = ["best[ext=mp4]", "best", "worst[ext=mp4]", "worst"]
            
            for fmt in alternative_formats:
                try:
                    ytdlp_opts = [
                        "yt-dlp",
                        *(_cookies_args()),
                        "--no-warnings",
                        "--geo-bypass",
                        "--force-ipv4",
                        "-f",
                        fmt,
                        "-o",
                        file_path,
                        link
                    ]
                    
                    stdout, stderr = await _exec_proc(*ytdlp_opts)
                    
                    if os.path.exists(file_path) and os.path.getsize(file_path) > 10240:
                        return file_path
                    
                    await asyncio.sleep(1)
                except Exception:
                    continue
            
            return None

    except Exception as e:
        return None


async def download_audio_ytdlp(link: str) -> str:
    """Download audio using yt-dlp directly"""
    video_id = link.split('v=')[-1].split('&')[0] if 'v=' in link else link

    if not video_id or len(video_id) < 3:
        return None

    DOWNLOAD_DIR = "downloads"
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.webm")

    if os.path.exists(file_path):
        return file_path

    await _check_rate_limit_async()
    
    try:
        ytdlp_opts = [
            "yt-dlp",
            *(_cookies_args()),
            "--no-warnings",
            "--geo-bypass",
            "--force-ipv4",
            "-f",
            "bestaudio[ext=webm]/bestaudio",
            "--extract-audio",
            "--audio-format", "webm",
            "-o",
            file_path,
            link
        ]
        
        stdout, stderr = await _exec_proc(*ytdlp_opts)
        
        if os.path.exists(file_path) and os.path.getsize(file_path) > 10240:
            return file_path
        else:
            alternative_formats = ["bestaudio[ext=m4a]/bestaudio", "bestaudio/best", "worstaudio"]
            
            for fmt in alternative_formats:
                try:
                    alt_file_path = os.path.join(DOWNLOAD_DIR, f"{video_id}.webm")
                    ytdlp_opts = [
                        "yt-dlp",
                        *(_cookies_args()),
                        "--no-warnings",
                        "--geo-bypass",
                        "--force-ipv4",
                        "-f",
                        fmt,
                        "--extract-audio",
                        "--audio-format", "webm",
                        "-o",
                        alt_file_path,
                        link
                    ]
                    
                    stdout, stderr = await _exec_proc(*ytdlp_opts)
                    
                    if os.path.exists(alt_file_path) and os.path.getsize(alt_file_path) > 10240:
                        return alt_file_path
                    
                    await asyncio.sleep(1)
                except Exception:
                    continue
            
            return None

    except Exception as e:
        return None


# ============ MAIN DOWNLOAD FUNCTIONS (API1 -> API2 -> YTDLP) ============
async def download_audio(link: str) -> str:
    """
    Main audio download - Primary API -> Fallback API -> yt-dlp
    """
    # 1. TRY PRIMARY API FIRST
    print("🎵 Audio Download - Trying Primary API (Direct)...")
    result = await download_song_primary_api(link)
    if result:
        print("✅ Audio: Primary API Success")
        return result
    
    # 2. TRY FALLBACK API (TOKEN BASED)
    print("🔄 Audio - Primary failed, trying Fallback API (Token)...")
    result = await download_song_fallback_api(link)
    if result:
        print("✅ Audio: Fallback API Success")
        return result
    
    # 3. TRY YT-DLP AS LAST RESORT
    print("🔄 Audio - Both APIs failed, trying yt-dlp fallback...")
    result = await download_audio_ytdlp(link)
    if result:
        print("✅ Audio: yt-dlp Success")
        if result.endswith('.webm'):
            mp3_path = result.replace('.webm', '.mp3')
            try:
                shutil.move(result, mp3_path)
                return mp3_path
            except:
                return result
        return result
    
    print("❌ All audio download methods failed")
    return None


async def download_video(link: str) -> str:
    """
    Main video download - Primary API -> Fallback API -> yt-dlp
    """
    # 1. TRY PRIMARY API FIRST
    print("🎬 Video Download - Trying Primary API (Direct)...")
    result = await download_video_primary_api(link)
    if result:
        print("✅ Video: Primary API Success")
        return result
    
    # 2. TRY FALLBACK API (TOKEN BASED)
    print("🔄 Video - Primary failed, trying Fallback API (Token)...")
    result = await download_video_fallback_api(link)
    if result:
        print("✅ Video: Fallback API Success")
        return result
    
    # 3. TRY YT-DLP AS LAST RESORT
    print("🔄 Video - Both APIs failed, trying yt-dlp fallback...")
    result = await download_video_ytdlp(link)
    if result:
        print("✅ Video: yt-dlp Success")
        return result
    
    print("❌ All video download methods failed")
    return None


# ============ YOUTUBE API CLASS ============
@capture_internal_err
async def cached_youtube_search(query: str) -> List[Dict]:
    key = f"q:{query}"
    now = time.time()
    async with _cache_lock:
        if key in _cache:
            ts, val = _cache[key]
            if now - ts < YOUTUBE_META_TTL:
                return val
            _cache.pop(key, None)
        if len(_cache) > YOUTUBE_META_MAX:
            _cache.clear()
    try:
        data = await VideosSearch(query, limit=1).next()
        result = data.get("result", [])
    except Exception:
        result = []
    if result:
        async with _cache_lock:
            _cache[key] = (now, result)
    return result


@capture_internal_err
async def youtube_search_multi(query: str, limit: int = 8) -> List[Dict]:
    """
    Fetch multiple YouTube results for a query â€” used by autoplay so it can
    score and pick from a pool of candidates rather than always getting the
    same #1 result. Results are NOT cached (we want variety across calls).
    """
    try:
        data = await VideosSearch(query, limit=limit).next()
        return data.get("result", [])
    except Exception:
        return []

async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower():
            return out.decode("utf-8")
        else:
            return errorz.decode("utf-8")
    return out.decode("utf-8")

class YouTubeAPI:
    def __init__(self) -> None:
        self.base_url = "https://www.youtube.com/watch?v="
        self.playlist_url = "https://youtube.com/playlist?list="
        self.status = "https://www.youtube.com/oembed?url="
        self._url_pattern = re.compile(r"(?:youtube\.com|youtu\.be)")
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    def _prepare_link(self, link: str, videoid: Union[str, bool, None] = None) -> str:
        if isinstance(videoid, str) and videoid.strip():
            link = self.base_url + videoid.strip()
        if "youtu.be" in link:
            link = self.base_url + link.split("/")[-1].split("?")[0]
        elif "youtube.com/shorts/" in link or "youtube.com/live/" in link:
            link = self.base_url + link.split("/")[-1].split("?")[0]
        return link.split("&")[0]

    @capture_internal_err
    async def url(self, message: Message) -> Optional[str]:
        msgs = [message] + ([message.reply_to_message] if message.reply_to_message else [])
        for msg in msgs:
            text = msg.text or msg.caption or ""
            entities = msg.entities or msg.caption_entities or []
            for ent in entities:
                if ent.type == MessageEntityType.URL:
                    url = text[ent.offset : ent.offset + ent.length]
                    if self._url_pattern.search(url):
                        return url
                if ent.type == MessageEntityType.TEXT_LINK:
                    url = ent.url
                    if self._url_pattern.search(url):
                        return url
        return None

    @capture_internal_err
    async def exists(self, link: str, videoid: Union[str, bool, None] = None) -> bool:
        return bool(self._url_pattern.search(self._prepare_link(link, videoid)))

    @capture_internal_err
    async def _fetch_video_info(self, query: str, *, use_cache: bool = True) -> Optional[Dict]:
        q = self._prepare_link(query)
        if use_cache and not q.startswith("http"):
            res = await cached_youtube_search(q)
            return res[0] if res else None
        data = await VideosSearch(q, limit=1).next()
        result = data.get("result", [])
        return result[0] if result else None

    @capture_internal_err
    async def is_live(self, link: str) -> bool:
        await _check_rate_limit_async()
        prepared = self._prepare_link(link)
        stdout, _ = await _exec_proc("yt-dlp", *(_cookies_args()), "--dump-json", prepared)
        if not stdout:
            return False
        try:
            info = json.loads(stdout.decode())
            return bool(info.get("is_live"))
        except json.JSONDecodeError:
            return False

    @capture_internal_err
    async def details(self, link: str, videoid: Union[str, bool, None] = None) -> Tuple[str, Optional[str], int, str, str]:
        info = await self._fetch_video_info(self._prepare_link(link, videoid))
        if not info:
            raise ValueError("Video not found")
        dt = info.get("duration")
        ds = int(time_to_seconds(dt)) if dt else 0
        thumb = (info.get("thumbnail") or info.get("thumbnails", [{}])[0].get("url", "")).split("?")[0]
        return info.get("title", ""), dt, ds, thumb, info.get("id", "")

    @capture_internal_err
    async def title(self, link: str, videoid: Union[str, bool, None] = None) -> str:
        info = await self._fetch_video_info(self._prepare_link(link, videoid))
        return info.get("title", "") if info else ""

    @capture_internal_err
    async def duration(self, link: str, videoid: Union[str, bool, None] = None) -> Optional[str]:
        info = await self._fetch_video_info(self._prepare_link(link, videoid))
        return info.get("duration") if info else None

    @capture_internal_err
    async def thumbnail(self, link: str, videoid: Union[str, bool, None] = None) -> str:
        info = await self._fetch_video_info(self._prepare_link(link, videoid))
        if info:
            thumb = info.get("thumbnail") or info.get("thumbnails", [{}])[0].get("url", "")
            return thumb.split("?")[0] if thumb else ""
        return ""

    @capture_internal_err
    async def video(self, link: str, videoid: Union[str, bool, None] = None) -> Tuple[int, str]:
        link = self._prepare_link(link, videoid)
        
        try:
            downloaded_file = await download_video(link)
            if downloaded_file:
                return (1, downloaded_file)
        except Exception:
            pass
        
        await _check_rate_limit_async()
        
        ytdlp_args = [
            "yt-dlp", *(_cookies_args()), "--no-warnings", "--geo-bypass", "--force-ipv4",
            "-g", "-f", "best[height<=?720][width<=?1280]/best", link
        ]
        
        stdout, stderr = await _exec_proc(*ytdlp_args)
        
        if stdout:
            stream_url = stdout.decode().split("\n")[0]
            if stream_url and stream_url.startswith('http'):
                return (1, stream_url)
            else:
                return (0, "Invalid stream URL")
        else:
            error_msg = stderr.decode() if stderr else "Unknown error"
            if "429" in error_msg or "Too Many Requests" in error_msg:
                await asyncio.sleep(30)
                return (0, "Rate limited")
            elif "403" in error_msg:
                return await self._try_alternative_format(link)
            else:
                return (0, error_msg)

    async def _try_alternative_format(self, link: str) -> Tuple[int, str]:
        format_options = ["best[height<=480]", "best[ext=mp4]", "best", "worst"]
        for fmt in format_options:
            stdout, stderr = await _exec_proc("yt-dlp", *(_cookies_args()), "--no-warnings", "-g", "-f", fmt, link)
            if stdout:
                stream_url = stdout.decode().split("\n")[0]
                if stream_url and stream_url.startswith('http'):
                    return (1, stream_url)
            await asyncio.sleep(1)
        return (0, "All format attempts failed")

    @capture_internal_err
    async def playlist(self, link: str, limit: int, user_id, videoid: Union[str, bool, None] = None) -> List[str]:
        if videoid:
            link = self.playlist_url + str(videoid)
        link = link.split("&")[0]
        await _check_rate_limit_async()
        playlist = await shell_cmd(f"yt-dlp -i --get-id --flat-playlist --playlist-end {limit} --skip-download {link}")
        try:
            items = [key for key in playlist.split("\n") if key]
        except:
            items = []
        return items

    @capture_internal_err
    async def track(self, link: str, videoid: Union[str, bool, None] = None) -> Tuple[Dict, str]:
        try:
            info = await self._fetch_video_info(self._prepare_link(link, videoid))
            if not info:
                raise ValueError("Track not found via API")
        except Exception:
            await _check_rate_limit_async()
            prepared = self._prepare_link(link, videoid)
            stdout, _ = await _exec_proc("yt-dlp", *(_cookies_args()), "--dump-json", prepared)
            if not stdout:
                raise ValueError("Track not found (yt-dlp fallback)")
            info = json.loads(stdout.decode())
        thumb = (info.get("thumbnail") or info.get("thumbnails", [{}])[0].get("url", "")).split("?")[0]
        _dur = info.get("duration")
        if isinstance(_dur, str) and _dur:
            duration_min = _dur
        elif isinstance(_dur, (int, float)) and _dur > 0:
            _secs = int(_dur)
            duration_min = f"{_secs // 60}:{_secs % 60:02d}"
        else:
            duration_min = None
        details = {
            "title": info.get("title", ""),
            "link": info.get("webpage_url", self._prepare_link(link, videoid)),
            "vidid": info.get("id", ""),
            "duration_min": duration_min,
            "thumb": thumb,
        }
        return details, info.get("id", "")

    @capture_internal_err
    async def formats(self, link: str, videoid: Union[str, bool, None] = None) -> Tuple[List[Dict], str]:
        link = self._prepare_link(link, videoid)
        key = f"f:{link}"
        now = time.time()
        async with _formats_lock:
            cached = _formats_cache.get(key)
            if cached and now - cached[0] < YOUTUBE_META_TTL:
                return cached[1], cached[2]

        await _check_rate_limit_async()
        
        opts = {"quiet": True}
        cf = _cookiefile_path()
        if cf:
            opts["cookiefile"] = cf
        out: List[Dict] = []
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(link, download=False)
                for fmt in info.get("formats", []):
                    if "dash" in str(fmt.get("format", "")).lower():
                        continue
                    if not any(k in fmt for k in ("filesize", "filesize_approx")):
                        continue
                    if not all(k in fmt for k in ("format", "format_id", "ext", "format_note")):
                        continue
                    size = fmt.get("filesize") or fmt.get("filesize_approx")
                    if not size:
                        continue
                    out.append({
                        "format": fmt["format"],
                        "filesize": size,
                        "format_id": fmt["format_id"],
                        "ext": fmt["ext"],
                        "format_note": fmt["format_note"],
                        "yturl": link,
                    })
        except Exception:
            pass

        async with _formats_lock:
            if len(_formats_cache) > YOUTUBE_META_MAX:
                _formats_cache.clear()
            _formats_cache[key] = (now, out, link)

        return out, link

    @capture_internal_err
    async def slider(self, link: str, query_type: int, videoid: Union[str, bool, None] = None) -> Tuple[str, Optional[str], str, str]:
        data = await VideosSearch(self._prepare_link(link, videoid), limit=10).next()
        results = data.get("result", [])
        if not results or query_type >= len(results):
            raise IndexError(f"Query type index {query_type} out of range (found {len(results)} results)")
        r = results[query_type]
        return (
            r.get("title", ""),
            r.get("duration"),
            r.get("thumbnails", [{}])[0].get("url", "").split("?")[0],
            r.get("id", ""),
        )

    @capture_internal_err
    async def download(
        self,
        link: str,
        mystic,
        *,
        video: Union[bool, str, None] = None,
        videoid: Union[str, bool, None] = None,
        songaudio: Union[bool, str, None] = None,
        songvideo: Union[bool, str, None] = None,
        format_id: Union[bool, str, None] = None,
        title: Union[bool, str, None] = None,
    ) -> Union[Tuple[str, Optional[bool]], Tuple[None, None]]:
        link = self._prepare_link(link, videoid)
        video_id = link.split('v=')[-1].split('&')[0] if 'v=' in link else link
        
        extension = ".webm" if not video else ".mp4"
        common_file_path = os.path.join("downloads", f"{video_id}{extension}")
        
        if os.path.exists(common_file_path) and os.path.getsize(common_file_path) > 10240:
            print("✅ Local cache")
            return common_file_path, True

        if songvideo or video:
            try:
                downloaded_file = await download_video(link)
                if downloaded_file:
                    print("✅ Video downloaded successfully")
                    if downloaded_file != common_file_path and downloaded_file.endswith('.mp4'):
                        try:
                            shutil.move(downloaded_file, common_file_path)
                            return common_file_path, True
                        except Exception:
                            return downloaded_file, True
                    return downloaded_file, True
            except Exception as e:
                print(f"❌ Video download error: {str(e)}")
            
            status, stream_url = await self.video(link)
            if status == 1:
                print("✅ Video stream")
                return stream_url, None
            else:
                return None, None

        else:
            try:
                audio_result = await download_audio(link)
                if audio_result:
                    print("✅ Audio downloaded successfully")
                    if audio_result.endswith('.mp3') and common_file_path.endswith('.webm'):
                        mp3_path = audio_result
                        webm_path = common_file_path
                        try:
                            shutil.move(mp3_path, webm_path)
                            return webm_path, True
                        except Exception:
                            return audio_result, True
                    return audio_result, True
            except Exception as e:
                print(f"❌ Audio download error: {str(e)}")
            
            try:
                p = await yt_dlp_download(link, type="audio")
                if p and os.path.exists(p) and os.path.getsize(p) > 10240:
                    print("✅ yt-dlp (original)")
                    if p != common_file_path:
                        try:
                            shutil.move(p, common_file_path)
                            return common_file_path, True
                        except Exception:
                            return p, True
                    return p, True
            except Exception as e:
                print(f"❌ Original yt-dlp error: {str(e)}")
            
            try:
                p = await download_audio_concurrent(link)
                if p and os.path.exists(p) and os.path.getsize(p) > 10240:
                    print("✅ concurrent")
                    if p != common_file_path:
                        try:
                            shutil.move(p, common_file_path)
                            return common_file_path, True
                        except Exception:
                            return p, True
                    return p, True
            except Exception as e:
                print(f"❌ Concurrent download error: {str(e)}")
            
            print("❌ All audio download methods failed")
            return None, None

YouTube = YouTubeAPI()

# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
