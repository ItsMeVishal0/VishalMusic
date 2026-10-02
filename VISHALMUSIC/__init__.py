# ═══════════════════════════════════════════════════════════
#        🌺 Vɪsʜᴀʟ Mᴜsɪᴄ 🌺
#   GɪᴛHᴜʙ : github.com/ItsMeVishal0/VishalMusic
#   Dᴇᴠʟᴏᴘᴇʀ : @ItsMeVishalBots | Telegram
# ═══════════════════════════════════════════════════════════

# ── Pyrogram / PyTgCalls Compatibility Layer ────────────────
import pyrogram.errors

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
