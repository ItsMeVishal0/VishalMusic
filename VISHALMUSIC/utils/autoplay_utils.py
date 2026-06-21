# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   GitHub : github.com/ItsMeVishal0/VishalMusic
#   Developer : @ItsMeVishalBots | Telegram
#   Module : Autoplay Feature Handler
# ═══════════════════════════════════════════════════════════

from VISHALMUSIC.core.mongo import mongodb

_autoplay_db = mongodb.autoplay


async def is_autoplay_on(chat_id: int) -> bool:
    data = await _autoplay_db.find_one({"chat_id": chat_id})
    return bool(data.get("status", False)) if data else False


async def toggle_autoplay(chat_id: int) -> bool:
    data = await _autoplay_db.find_one({"chat_id": chat_id})
    if not data:
        await _autoplay_db.insert_one({"chat_id": chat_id, "status": True})
        return True
    new_status = not bool(data.get("status", False))
    await _autoplay_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"status": new_status}},
    )
    return new_status

# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
