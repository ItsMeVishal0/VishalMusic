# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   GitHub : github.com/ItsMeVishal0/VishalMusic
#   Developer : @ItsMeVishalBots | Telegram
#   Module : Package Initialization & App Setup
# ═══════════════════════════════════════════════════════════

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
#        😎  VISHAL MUSIC BOT  😎
#   github.com/ItsMeVishal0/VishalMusic
# ═══════════════════════════════════════════════════════════
