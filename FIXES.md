# VishalMusic — Runtime Bug Fixes

Fixed date: 2026-08-28
Fixed by: Accio (code analysis + patch)

---

## Root cause summary

### 1. Missing imports → `NameError` at runtime (main reason "commands don't work")

17 files call the colored-button helper functions (`send_message_colored`, `send_photo_colored`, `edit_message_text_colored`, `edit_message_caption_colored`, `edit_reply_markup_colored`, `edit_message_media_colored`) **without importing them**. Pyrogram silently catches handler exceptions and only logs them, so every command hitting one of these paths looked like it "did nothing":

| File | Missing import(s) | Broken commands/features |
|---|---|---|
| `VISHALMUSIC/utils/decorators/play.py` | `send_message_colored` | `/play` family when anonymous admin or assistant banned |
| `VISHALMUSIC/utils/decorators/admins.py` | `send_message_colored` | pause/resume/skip/stop/seek/loop/shuffle/speed (anonymous admin / vote mode) |
| `VISHALMUSIC/plugins/Manager/del_msg.py` | `send_message_colored` | `/deleteall` confirm buttons |
| `VISHALMUSIC/plugins/Manager/welcome.py` | `send_photo_colored` | welcome image buttons |
| `VISHALMUSIC/plugins/Manager/zombie.py` | `send_message_colored` | `/zombies` |
| `VISHALMUSIC/plugins/sudo/sudoers.py` | `send_message_colored`, `edit_message_caption_colored` | `/addsudo` / `/delsudo` |
| `VISHALMUSIC/plugins/play/playmode.py` | `send_message_colored` | `/playmode` |
| `VISHALMUSIC/plugins/tools/gitinfo.py` | `send_message_colored`, `send_photo_colored` | `/gitinfo` |
| `VISHALMUSIC/plugins/tools/active.py` | `send_message_colored` | `/activevc` |
| `VISHALMUSIC/plugins/tools/song.py` | `send_message_colored`, `send_photo_colored`, `edit_reply_markup_colored` | `/song` download buttons |
| `VISHALMUSIC/plugins/tools/queue.py` | `edit_message_media_colored` | queue buttons |
| `VISHALMUSIC/plugins/tools/stats.py` | `edit_message_media_colored` | `/stats` buttons |
| `VISHALMUSIC/plugins/tools/dev.py` | `send_message_colored`, `edit_message_text_colored`, `edit_reply_markup_colored` | `/eval` / `/sh` buttons |
| `VISHALMUSIC/plugins/tools/telegraph.py` | `edit_message_text_colored` | `/telegraph` |
| `VISHALMUSIC/plugins/Kishu/ip.py` | `edit_message_text_colored` | `/ip` |
| `VISHALMUSIC/plugins/Kishu/password.py` | `edit_message_text_colored` | `/genpassword` |
| `VISHALMUSIC/plugins/Kishu/figlet.py` | `send_message_colored`, `edit_message_text_colored` | `/figlet` |

**Fix:** added the missing imports to all 17 files.

### 2. Button colors (primary/success/danger) not applying

- The `style` field IS supported by current Telegram Bot API (officially documented; values `primary` / `success` / `danger` are correct).
- The code **always called the official API** and ignored `LOCAL_BOT_API_URL`, even though config.py defines it ("Without this, button color (style) fields will be ignored"). → Now `LOCAL_BOT_API_URL` is used when set.
- When buttons were empty, the payload sent `"inline_keyboard": []` which the Bot API rejects → the whole send failed and fell back to plain (colorless) Pyrogram buttons. → Now `reply_markup` is only added when there are buttons.
- The Pyrogram fallbacks in `smart_send_message` / `smart_send_photo` were unguarded — if they also failed, the handler crashed. → Now wrapped in try/except.
- Many colored calls crashed before sending because of the missing imports above (fix #1), which also made buttons appear colorless or not at all.

**Note:** colored buttons also render on the Telegram **client** — make sure the Telegram app is updated (colored-button style rendering requires a client from after Feb 2026).

### 3. ZIP deploy: code silently replaced at startup (major!)

`VISHALMUSIC/core/git.py` — when the bot is deployed from a ZIP (no `.git` folder), startup ran `Repo.init()` → `git fetch` + `checkout` of the upstream repo, **deleting/overwriting the uploaded code on every restart**.

**Fix:** when no git repository exists, skip upstream sync entirely and keep the deployed code.

### 4. `/figlet` callback button dead for long text

`callback_data` = `figlet_<base64>` exceeded Telegram's 64-byte limit for long inputs, so the button was rejected by the Bot API.

**Fix:** encode only the first 25 characters for the callback payload.

---

## Round 2 — Long-running degradation fixes (2026-08-28)

Reported: after the bot runs continuously for a while → welcome image stops coming, assistant joins the VC but songs don't play, bot still shows "running".

### 5. YouTube cookies expire → downloads silently fail (main cause of "assistant in VC but no song")

Cookies were fetched **once at startup** (`fetch_and_store_cookies()`). YouTube invalidates them over time; after that every `yt-dlp` download fails, the queue never advances, and the assistant is left sitting in the VC with nothing playing — while the bot dashboard still shows "running".

**Fix:** added `_cookie_refresh_loop()` in `VISHALMUSIC/__main__.py` — re-fetches cookies every 12 hours (configurable via `COOKIE_REFRESH_HOURS`).

### 6. No self-healing for long uptime → optional auto-restart watchdog

Long-running bots degrade (stale pytgcalls calls, memory growth, dropped sessions). Added an **opt-in** watchdog: set env `AUTO_RESTART_HOURS` (e.g. `24`) and the bot restarts itself every N hours via the same mechanism as `/restart` (clean process, fresh sessions/cookies).

### 7. Welcome image fixes (`VISHALMUSIC/plugins/Manager/welcome.py`)

- **Caption HTML parse crash:** chat title / username with `&`, `<` etc. broke HTML parsing → the whole photo send failed and fell back to a plain text welcome (no image). Now all caption fields are HTML-escaped.
- **Missing `downloads/` folder:** image save failed silently if the folder didn't exist. Now it's created before saving.
- **Hardcoded coordinates:** avatar/text positions were tuned for exactly 2880x1620; now they scale to the actual `welcome.png` size, so the PNG renders correctly on any resolution.
- Verified locally: `build_pic()` generates a valid 2880×1620 RGBA PNG.

### Files changed (round 2)

```
VISHALMUSIC/__main__.py
VISHALMUSIC/plugins/Manager/welcome.py
```

### New environment variables

| Var | Default | Purpose |
|---|---|---|
| `COOKIE_REFRESH_HOURS` | `12` | How often to re-fetch YouTube cookies |
| `AUTO_RESTART_HOURS` | `0` (off) | Set e.g. `24` to auto-restart daily |

---

## Round 3 — AI features fixes (2026-08-28)

Reported: AI features (gpt/ai/bard/gemini/llama/mistral/assis) not working.

### 8. Bot could not even start without OPENROUTER_KEY (critical)

`tools/gpt.py` and `tools/ai.py` ran `raise Exception(...)` / `raise ValueError(...)` at **module import time** when `OPENROUTER_KEY` was missing. Since every plugin is imported at startup, a missing key crashed the **entire bot** (or made deploy fail).

**Fix:** removed the module-level raises. If the key is missing, AI commands now reply with a friendly "AI is not configured — set OPENROUTER_KEY" message instead of killing the bot. Also, the plugin loader in `VISHALMUSIC/__main__.py` now catches per-module import errors and continues, so one broken plugin can never take the bot down again.

### 9. Old model IDs deprecated on OpenRouter

The model map used dead IDs (`gpt-3.5-turbo`, `google/gemini-pro`, `google/gemini-flash-1.5`, `meta-llama/llama-3-8b-chat`, `mistralai/mistral-7b-instruct`) → OpenRouter returned "model not found", so commands failed even with a valid key. Updated to current IDs (verified against the OpenRouter API, Aug 2026):

| Command | Model |
|---|---|
| /ai | `openrouter/free` (auto free router) |
| /gpt | `openai/gpt-4o-mini` |
| /bard, /gemini | `google/gemini-3.7-flash` |
| /llama | `meta-llama/llama-4-maverick` |
| /mistral | `mistralai/mistral-medium-3-5` |

### 10. Duplicate handlers → double replies

`tools/gpt.py` and `tools/ai.py` BOTH registered `/gpt /bard /gemini /llama /mistral` → every command triggered two handlers (double responses). Removed the duplicates from `ai.py`; it now only provides the unique `/geminivision` command.

### Files changed (round 3)

```
VISHALMUSIC/__main__.py
VISHALMUSIC/plugins/tools/gpt.py
VISHALMUSIC/plugins/tools/ai.py
```

### To enable AI features

1. Get a free key at https://openrouter.ai/keys
2. Add it to your host env: `OPENROUTER_KEY=sk-or-...`
3. Restart the bot → `/ai`, `/gpt`, `/gemini`, `/assis` etc. will work.

---

## Round 4 — Clone system (2026-08-28)

Feature: koi bhi apne BOT_TOKEN se bot clone kar sakta hai. Clone me **uska apna OWNER_ID** show hota hai, branding master ki rahti hai, **master ka broadcast saare clones ke users/chats tak jata hai**, aur **clone owner ka broadcast sirf uske apne bot me**.

### Kaise kaam karta hai

1. **Namespaced collections:** har bot apne served users/chats ko `tgusersdb_<bot_username>` / `chats_<bot_username>` me rakhta hai (pehle sab shared `tgusersdb`/`chats` me the).
2. **Shared MongoDB:** saare clones ko SAME `MONGO_DB_URI` use karna hai — isi se master ko saare clones ka data dikhta hai.
3. **MASTER_ID (default 7044783841):** jis user ka ID MASTER_ID hai, uske `/broadcast` me `get_served_users_all()` / `get_served_chats_all()` use hota hai → har clone ke users/chats tak pahunchta hai. Baaki sudo users (clone owners) sirf apna namespace broadcast karte hain.
4. **OWNER_ID env-based hai** (pehle se) — clone owner apna OWNER_ID set kare toh CODER button, owner commands, SUDOERS sab uske hisaab se.

### Master ke liye (aap)

- Kuch nahi badalna — MASTER_ID default aapka ID hai.
- `/broadcast -user` ab saare clones ke users tak jayega.

### Cloner ke liye (jo bot clone karega)

- Set kare: `BOT_TOKEN` (apna), `API_ID`/`API_HASH` (apna), `OWNER_ID` (apna Telegram ID), `BOT_USERNAME` (apne bot ka username), `STRING_SESSION` (apna assistant session).
- **NOT change kare:** `MONGO_DB_URI` (master ka hi rakhe — shared userbase isi se chalti hai), `MASTER_ID` (master ka hi rahega).
- Branding (VISHALMUSIC, support links, "made by") master ki hi rahti hai.

### Files changed (round 4)

```
config.py
VISHALMUSIC/utils/database.py
VISHALMUSIC/plugins/misc/broadcast.py
```

---

## Round 5 — Clone setup simplification (2026-08-28)

Feature: cloner ko ab **sirf BOT_TOKEN** dena hai — baaki sab automatic.

### Kya-kya automatic ho gaya

| Cheez | Kaise |
|---|---|
| **Username** | Namespace + "ADD ME" buttons ab runtime `app.username` se lete hain (config.BOT_USERNAME ki zaroorat nahi) |
| **Owner ID** | **Auto-owner:** jo user sabse pehle bot ko PRIVATE me /start karega, wahi owner ban jata hai (`owner_<bot_username>` collection me store) — CODER button, SUDOERS sab uske hisaab se |
| **Assistant** | Master ka shared session: `config.MASTER_STRING_SESSION` me daalo, saare clones wahi use karenge |
| **API_ID / API_HASH** | pehle se config me hardcoded — cloner ko nahi dena |

### Files changed (round 5)

```
config.py
VISHALMUSIC/misc.py
VISHALMUSIC/utils/database.py
VISHALMUSIC/utils/inline/start.py
VISHALMUSIC/plugins/bot/start.py
VISHALMUSIC/plugins/bot/help.py
VISHALMUSIC/plugins/bot/settings.py
VISHALMUSIC/plugins/Kishu/password.py
```

### ⚠️ Shared assistant ki limitations

1. **Ek account ek waqt me sirf EK voice chat** me ho sakta hai — do clones ek saath music nahi chala sakte (doosra fail hoga "already in a call").
2. **Session kisi aur ko dena = account ka risk** — session string wala koi bhi assistant account use kar sakta hai.
3. `MASTER_STRING_SESSION` khali hai toh bot chalta hai, lekin VC/music features assistant ke bina kaam nahi karenge — master ko apna session daalna hoga.

---

## Files changed (19)

```
VISHALMUSIC/core/git.py
VISHALMUSIC/utils/colored_buttons.py
VISHALMUSIC/utils/decorators/admins.py
VISHALMUSIC/utils/decorators/play.py
VISHALMUSIC/plugins/Manager/del_msg.py
VISHALMUSIC/plugins/Manager/welcome.py
VISHALMUSIC/plugins/Manager/zombie.py
VISHALMUSIC/plugins/Kishu/figlet.py
VISHALMUSIC/plugins/Kishu/ip.py
VISHALMUSIC/plugins/Kishu/password.py
VISHALMUSIC/plugins/play/playmode.py
VISHALMUSIC/plugins/sudo/sudoers.py
VISHALMUSIC/plugins/tools/active.py
VISHALMUSIC/plugins/tools/dev.py
VISHALMUSIC/plugins/tools/gitinfo.py
VISHALMUSIC/plugins/tools/queue.py
VISHALMUSIC/plugins/tools/song.py
VISHALMUSIC/plugins/tools/stats.py
VISHALMUSIC/plugins/tools/telegraph.py
```

## Verification

- All changed files pass `python3 -m py_compile`.
- Re-scan confirms 0 remaining missing colored-button imports.
- Full-codebase static scan for undefined function calls: no remaining real issues.
