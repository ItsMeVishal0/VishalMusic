# ═══════════════════════════════════════════════════════════
#        🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   GɪᴛHᴜʙ : github.com/ItsMeVishal0/VishalMusic
#   Dᴇᴠʟᴏᴘᴇʀ : @ItsMeVishalBots | Telegram
# ═══════════════════════════════════════════════════════════

import os
import asyncio

CPU = os.cpu_count() or 1

# Adaptive concurrency: lightweight on 1-core VPS, scales gently on multi-core
MAX_CONCURRENT = int(os.getenv("MAX_CONCURRENT", str(min(16, max(4, CPU * 2)))))

# 512 KB chunks — perfectly balanced for fast network without high memory allocation
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", str(512 * 1024)))

# Tighter yt-dlp timeout: fail fast, move to next method
YTDLP_TIMEOUT = int(os.getenv("YTDLP_TIMEOUT", "25"))

# Efficient metadata cache: 10 min TTL with 512 entries (saves RAM)
YOUTUBE_META_TTL = int(os.getenv("YOUTUBE_META_TTL", "600"))
YOUTUBE_META_MAX = int(os.getenv("YOUTUBE_META_MAX", "512"))

SEM = asyncio.Semaphore(MAX_CONCURRENT)

# ═══════════════════════════════════════════════════════════
#         🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
