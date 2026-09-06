# 🔥 VishalMusic — Upgrade Pack (New Features)

This folder is the **upgraded VishalMusic source**: your full original code plus a set of
new premium features, fully rebranded — **only Vishal branding/credits are used in the
code** (`VISHAL MUSIC BOT`, `github.com/ItsMeVishal0/VishalMusic`, `@ItsMeVishalBots`).

---

## ✅ What was analysed & decided

Your original source was compared feature-by-feature against a reference music-bot repo:

| Result | Detail |
| :--- | :--- |
| Already richer | VishalMusic already has ban/kick/purge, welcome, zombie cleaner, taggers, couple, invite link, dev tools, chatlog, AI/GPT tools, dice/bored games, TTS, speedtest, repo downloader, etc. — these were **not** duplicated. |
| Already coloured | `utils/colored_buttons.py` (green/red/blue style buttons) is used across **60+ files**. |
| Redundant | Duplicate modules (bot logs, ban, tag-all, zombie cleaner, welcome, wishes, truth/dare) were **skipped** — already covered by your `chatlog.py`, `Manager/actions.py`, `Manager/funtag.py`, `Manager/zombie.py` etc. |
| Clean-up | A leftover third-party API name in `platforms/Youtube.py` was renamed to **Vishal API** (`VISHAL_API_KEY`). |

## 🎁 New features added

| File | Commands | What it does |
| :--- | :--- | :--- |
| `VISHALMUSIC/plugins/tools/force_subscription.py` | `/fsub <channel>`, `/fsub off` | **Force subscription** — users who don't join your channel get muted / blocked from chatting until they join. |
| `VISHALMUSIC/plugins/tools/vclogger.py` | `/vclogger on/off` | **VC Logger** — announces (auto-deleting messages) when someone joins/leaves the group voice chat. State stored in MongoDB; monitoring resumes after restart. |
| `VISHALMUSIC/plugins/tools/lovebirds.py` | `/bal`, `/gifts`, `/sendgift @user <emoji>`, `/story Name1 Name2`, `/mygifts`, `/top` | **LoveBirds economy** — coins for chatting, gift catalogue, gift claiming, random love stories, richest-users leaderboard. |
| `VISHALMUSIC/plugins/bot/privacy.py` | `/privacy` | **Privacy policy** command (uses `PRIVACY_LINK` env var). |
| `VISHALMUSIC/plugins/tools/bots.py` | `/bots` | Lists all bots present in the group. |
| `VISHALMUSIC/plugins/tools/markdown.py` | `/markdownhelp` | Markdown/HTML formatting guide (useful to set up welcomes/logs). |

## 🔧 Integration changes made

1. **`config.py`** — added optional `PRIVACY_LINK` (defaults to `SUPPORT_CHAT`):
   ```env
   PRIVACY_LINK=https://t.me/YourChannel/123
   ```
2. **`requirements.txt`** — added `pymongo` (used by the force-subscription store).
3. **`VISHALMUSIC/__main__.py`** — after the assistant starts, VC Logger state is loaded
   from MongoDB so groups with `/vclogger on` keep notifications after a bot restart.
4. **`sample.env`** — documented the new `PRIVACY_LINK` variable.
5. **`Readme.md`** — added the new "Upgrade Pack" feature section.

### Important deployment notes
- **Force subscription** needs the bot to be **admin in the group** (to mute/unmute) and
  it must be able to see the target **channel** (bot added there as admin or the channel is public).
  The message gate handler runs at group `32` so it never collides with existing handlers.
- **VC Logger** needs the **assistant account** to work (raw group-call participant polling,
  1 request every 5 seconds per enabled chat — fine for normal use).
- `/privacy` button opens `PRIVACY_LINK`; set it to your own post/page.

## 🧪 Verification done

- `python3 -m compileall` — **all Python files compile** (syntax clean).
- Rebranding sweep — **zero** remaining foreign references inside the code; every module
  header/footer now carries the Vishal banner.

## 📤 How to publish this upgraded source

```bash
# 1) init git in this folder (or copy its contents over your existing clone)
git init
git add .
git commit -m "Upgrade: force-sub, VC logger, LoveBirds economy, privacy, bots list, markdown help"

# 2) push to your GitHub repo
git remote add origin https://github.com/ItsMeVishal0/VishalMusic.git
git branch -M main
git push -u origin main
```

Or simply replace the contents of your existing local clone with this folder and push.
After that, redeploy via Heroku/Render/VPS — all old environment variables still work,
only `PRIVACY_LINK` is new (optional).

## 💡 More upgrade ideas for later

- Vote-mode intensity setting (increment vote threshold by 2) — small settings-panel tweak.
- PyTgCalls `cache_duration` + extra ffmpeg params in `core/call.py` — performance tweak.
- Robust `time_converter` (m/h/d units) and edge-case user-extraction utilities.
- `awelcome` toggle and a `gali` fun command — small community features.
