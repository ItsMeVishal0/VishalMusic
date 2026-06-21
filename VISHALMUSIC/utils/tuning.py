import os
import asyncio

CPU = os.cpu_count() or 4

MAX_CONCURRENT = int(os.getenv("MAX_CONCURRENT", str(min(64, CPU * 8))))

# 1 MB chunks — 16x faster than old 64 KB default
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", str(1024 * 1024)))

# Tighter yt-dlp timeout: fail fast, move to next method
YTDLP_TIMEOUT = int(os.getenv("YTDLP_TIMEOUT", "30"))

# Longer metadata cache (10 min), bigger LRU (4096 entries)
YOUTUBE_META_TTL = int(os.getenv("YOUTUBE_META_TTL", "600"))
YOUTUBE_META_MAX = int(os.getenv("YOUTUBE_META_MAX", "4096"))

SEM = asyncio.Semaphore(MAX_CONCURRENT)
