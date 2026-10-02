# ═══════════════════════════════════════════════════════════
#        🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   GɪᴛHᴜʙ : github.com/ItsMeVishal0/VishalMusic
#   Dᴇᴠʟᴏᴘᴇʀ : @ItsMeVishalBots | Telegram
# ═══════════════════════════════════════════════════════════

# ── Pyrogram / PyTgCalls Compatibility Layer ────────────────
import pyrogram.errors

# 64-bit Int / OverflowError auto-protection for Pyrogram MTProto
try:
    import pyrogram.raw.core.primitives as _primitives

    def _safe_int_new(cls, value: int, signed: bool = True):
        try:
            val_int = int(value)
            if signed and (val_int > 2147483647 or val_int < -2147483648):
                val_int = (val_int & 0xFFFFFFFF)
                if val_int > 0x7FFFFFFF:
                    val_int -= 0x100000000
            return val_int.to_bytes(cls.SIZE, "little", signed=signed)
        except Exception:
            return (int(value) & 0xFFFFFFFF).to_bytes(4, "little", signed=False)

    _primitives.Int.__new__ = _safe_int_new
except Exception:
    pass

if not hasattr(pyrogram.errors, "GroupcallForbidden"):
    _found = False
    for _sub in ("bad_request_400", "forbidden_403"):
        try:
            import importlib
            _mod = importlib.import_module(f"pyrogram.errors.exceptions.{_sub}")
            if hasattr(_mod, "GroupcallForbidden"):
                setattr(pyrogram.errors, "GroupcallForbidden", getattr(_mod, "GroupcallForbidden"))
                _found = True
                break
        except Exception:
            pass
    if not _found:
        class GroupcallForbidden(pyrogram.errors.RPCError):
            """The group call is forbidden."""
            ID = "GROUPCALL_FORBIDDEN"
        setattr(pyrogram.errors, "GroupcallForbidden", GroupcallForbidden)

from VISHALMUSIC.core.bot import VISHAL
from VISHALMUSIC.core.dir import dirr
from VISHALMUSIC.core.git import git
from VISHALMUSIC.core.userbot import Userbot
from VISHALMUSIC.misc import dbb, heroku

from .logging import LOGGER

dirr()
git()
dbb()
heroku()

app = VISHAL()
userbot = Userbot()

# ── Kurigram mention fix ──────────────────────────────────────
# Kurigram ka User.mention bina quotes ka anchor banata hai:
#     <a href=tg://user?id=123>Name</a>
# Telegram Bot API usse parse nahi kar pata ("Unexpected end of name
# token") → Bot API path fail → buttons colorless fallback me jaate
# hain. Isliye mention ko QUOTED anchor ke saath override karte hain.
try:
    from pyrogram.types import User as _KurigramUser

    def _quoted_mention(self):
        name = self.first_name or "Deleted Account"
        return f'<a href="tg://user?id={self.id}">{name}</a>'

    _KurigramUser.mention = property(_quoted_mention)
    LOGGER("VISHALMUSIC").info("✔ mention HTML quote fix applied")
except Exception as _e:
    LOGGER("VISHALMUSIC").warning(f"mention fix failed: {_e}")


from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()

# ═══════════════════════════════════════════════════════════
#         🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
