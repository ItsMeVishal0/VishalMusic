import asyncio
import random
import re
import time

import aiohttp
try:
    from unidecode import unidecode as _unidecode
except ImportError:
    _unidecode = None

from VISHALMUSIC import app
from VISHALMUSIC.core.mongo import mongodb
from VISHALMUSIC.misc import db
from VISHALMUSIC.platforms.Youtube import YouTubeAPI, youtube_search_multi

yt = YouTubeAPI()
autoplay_db = mongodb.autoplay

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  PROTECTION SYSTEM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━

RECENT = {}            # {chat_id: [(vidid, timestamp), ...]}
RECENT_TITLES = {}     # {chat_id: [(norm_title, timestamp), ...]}
RECENT_ARTISTS = {}    # {chat_id: [artist, artist, ...]}  — last 10 artists
AUTO_PLAYING = {}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚫 DEVOTIONAL WORDS — hard-skip when mood != devotional
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━

DEVOTIONAL_WORDS = [
    "bhajan", "aarti", "mantra", "chalisa", "bhakti", "devotional",
    "kirtan", "stotra", "stuti", "vandana", "pooja", "puja",
    "jai shri", "jai ram", "jai hanuman", "jai ganesh", "jai durga",
    "namo namo", "om shanti", "shiv tandav", "shri ram", "jai mata",
    "navratri", "ganpati", "sai baba", "balaji", "tirupati",
    "ramayana", "mahabharata", "bajrang baan", "sunderkand",
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🌐 LANGUAGE TITLE INDICATORS — detect language from title keywords
# Used to prevent hindi→bhojpuri/haryanvi cross-over etc.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━

LANG_TITLE_INDICATORS = {
    "bhojpuri":  ["bhojpuri", "pawan singh", "khesari", "pramod premi", "bhojpuri song"],
    "haryanvi":  ["haryanvi", "mewati", "khasa aala chahar", "masoom sharma", "haryanvi song"],
    "gujarati":  ["gujarati", "garba", "gujju", "gujarati song"],
    "tamil":     ["tamil", "kollywood", "tamil song"],
    "telugu":    ["telugu", "tollywood", "telugu song"],
    "bengali":   ["bengali", "bangla", "bengali song"],
    "marathi":   ["marathi", "marathi song"],
    "punjabi":   ["punjabi", "jatt", "pind", "sidhu", "diljit", "karan aujla", "ammy virk", "punjabi song"],
    "english":   ["english song", "english version"],
}

# Languages that should be hard-blocked from bleeding into each other
# e.g. if lang=hindi, skip bhojpuri/haryanvi/tamil etc.
INCOMPATIBLE_LANGS = {
    "hindi":    ["bhojpuri", "haryanvi", "gujarati", "tamil", "telugu", "bengali", "marathi"],
    "punjabi":  ["bhojpuri", "haryanvi", "tamil", "telugu", "bengali"],
    "bhojpuri": ["punjabi", "haryanvi", "tamil", "telugu", "bengali", "gujarati"],
    "haryanvi": ["bhojpuri", "punjabi", "tamil", "telugu", "bengali", "gujarati"],
    "tamil":    ["hindi", "punjabi", "bhojpuri", "haryanvi", "telugu", "bengali"],
    "telugu":   ["hindi", "punjabi", "bhojpuri", "haryanvi", "tamil", "bengali"],
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎤 SIMILAR ARTISTS — for variety when same artist repeats
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━

SIMILAR_ARTISTS = {
    "arijit singh":     ["jubin nautiyal", "atif aslam", "armaan malik", "shreya ghoshal", "darshan raval"],
    "jubin nautiyal":   ["arijit singh", "armaan malik", "darshan raval", "pawandeep rajan"],
    "atif aslam":       ["arijit singh", "jubin nautiyal", "falak shabir", "rahat fateh ali"],
    "shreya ghoshal":   ["arijit singh", "neha kakkar", "lata mangeshkar", "alka yagnik"],
    "sidhu moosewala":  ["karan aujla", "shubh", "ap dhillon", "diljit dosanjh", "ammy virk"],
    "diljit dosanjh":   ["sidhu moosewala", "karan aujla", "ammy virk", "gurnazar"],
    "karan aujla":      ["sidhu moosewala", "ap dhillon", "shubh", "diljit dosanjh"],
    "ap dhillon":       ["karan aujla", "shubh", "gurinder gill", "diljit dosanjh"],
    "badshah":          ["yo yo honey singh", "neha kakkar", "guru randhawa"],
    "yo yo honey singh":["badshah", "guru randhawa", "neha kakkar"],
    "neha kakkar":      ["shreya ghoshal", "badshah", "tony kakkar", "tulsi kumar"],
    "armaan malik":     ["arijit singh", "jubin nautiyal", "darshan raval"],
    "guru randhawa":    ["badshah", "yo yo honey singh", "neha kakkar"],
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🇮🇳 INDIAN LANGUAGE DATABASE
# Keywords that appear IN the title itself (song name / channel name)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━

LANG_DB = {
    "hindi":    ["hindi", "bollywood", "hindi song", "bollywood song", "filmi gaana"],
    "punjabi":  ["punjabi", "jatt", "pind", "punjabi song", "punjabi music"],
    "english":  ["english", "english song", "english version"],
    "bhojpuri": ["bhojpuri", "bhojpuri song", "bhojpuri music"],
    "haryanvi": ["haryanvi", "haryanvi song", "mewati"],
    "gujarati": ["gujarati", "garba", "gujarati song", "gujju"],
    "tamil":    ["tamil", "kollywood", "tamil song", "tamil cinema"],
    "telugu":   ["telugu", "tollywood", "telugu song", "telugu cinema"],
    "bengali":  ["bengali", "bangla", "bengali song"],
    "marathi":  ["marathi", "marathi song"],
    "urdu":     ["urdu", "urdu song", "ghazal"],
}

# Artist → language mapping — much more reliable than title keywords.
# Most song titles ("Kesariya", "Brown Munde") contain NO language words,
# so we identify language via the artist instead.
ARTIST_LANG = {
    "hindi": [
        "arijit singh", "jubin nautiyal", "atif aslam", "shreya ghoshal",
        "sonu nigam", "alka yagnik", "udit narayan", "kumar sanu",
        "lata mangeshkar", "kishore kumar", "mohammad rafi",
        "neha kakkar", "armaan malik", "darshan raval", "pawandeep rajan",
        "rahat fateh ali", "sunidhi chauhan", "shaan", "kk", "mohit chauhan",
        "vishal shekhar", "amit trivedi", "pritam", "shankar ehsaan loy",
    ],
    "punjabi": [
        "sidhu moosewala", "diljit dosanjh", "karan aujla", "ap dhillon",
        "ammy virk", "gurinder gill", "shubh", "guru randhawa",
        "badshah", "yo yo honey singh", "jasmine sandlas", "gurnazar",
        "b praak", "jaani", "hardy sandhu", "mankirt aulakh", "sukh e",
    ],
    "bhojpuri": [
        "pawan singh", "khesari lal yadav", "pramod premi", "dinesh lal yadav",
        "manoj tiwari", "ritesh pandey",
    ],
    "haryanvi": [
        "khasa aala chahar", "masoom sharma", "renuka panwar", "raj mawar",
        "sumit goswami", "raju punjabi",
    ],
    "tamil": ["anirudh ravichander", "sid sriram", "dhanush", "g v prakash"],
    "telugu": ["devi sri prasad", "ss thaman", "chinmayi", "sid sriram"],
    "english": [
        "ed sheeran", "taylor swift", "justin bieber", "the weeknd",
        "drake", "eminem", "billie eilish", "ariana grande",
    ],
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎭 MOOD DATABASE (Indian Context)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━

MOOD_DB = {
    "sad": ["sad", "broken", "heart", "bewafa", "alone", "cry", "dard", "tanha", "rula", "sad song"],
    "love": ["love", "romantic", "ishq", "pyaar", "mohabbat", "love song", "romantic song", "pyar", "ishq wala"],
    "party": ["party", "dj", "dance", "club", "bhangra", "party song", "dj song", "dance song", "masala"],
    "wedding": ["wedding", "shaadi", "marriage", "dulhan", "mehendi", "sangeet"],
    "devotional": ["devotional", "bhajan", "aarti", "mantra", "shiva", "krishna", "ram", "ganesha", "hanuman"],
    "oldschool": ["old", "classic", "90s", "80s", "kishore", "lata", "rafi", "old song", "retro", "purana"],
    "punjabi": ["punjabi", "sidhu", "diljit", "bhangra", "jatt", "punjabi song"],
    "sufi": ["sufi", "qawwali", "nusrat", "kalam", "sufiana"],
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎤 INDIAN ARTIST DATABASE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━

ARTIST_DB = {
    "arijit singh": ["arijit", "arijit singh", "arijit song", "arijit new"],
    "atif aslam": ["atif", "atif aslam", "atif song"],
    "sidhu moosewala": ["sidhu", "sidhu moosewala", "sidhu song"],
    "diljit dosanjh": ["diljit", "diljit dosanjh", "diljit song"],
    "karan aujla": ["karan", "karan aujla", "karan song"],
    "jubin nautiyal": ["jubin", "jubin nautiyal", "jubin song"],
    "badshah": ["badshah", "badshah song", "badshah new"],
    "yo yo honey singh": ["honey singh", "yo yo", "brown rang", "yo yo honey singh"],
    "neha kakkar": ["neha kakkar", "neha song", "neha new"],
    "shreya ghoshal": ["shreya", "shreya ghoshal", "shreya song"],
    "sonu nigam": ["sonu", "sonu nigam", "sonu song"],
    "alka yagnik": ["alka", "alka yagnik", "alka song"],
    "udit narayan": ["udit", "udit narayan", "udit song"],
    "kumar sanu": ["kumar sanu", "kumar song"],
    "lata mangeshkar": ["lata", "lata mangeshkar", "lata song"],
    "kishore kumar": ["kishore", "kishore kumar", "kishore song"],
    "mohammad rafi": ["rafi", "mohammad rafi", "rafi song"],
    "ap dhillon": ["ap dhillon", "ap", "dhillon", "ap song"],
    "gurinder gill": ["gurinder gill", "gill", "gurinder song"],
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎬 INDIAN MOVIE DATABASE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━

MOVIE_DB = {
    "animal": ["animal", "animal song", "animal movie"],
    "kabir singh": ["kabir singh", "kabir movie"],
    "aashiqui 2": ["aashiqui", "aashiqui 2", "aashiqui song"],
    "shershaah": ["shershaah", "shershaah song", "shershaah movie"],
    "pushpa": ["pushpa", "pushpa song", "pushpa movie", "srivali"],
    "kgf": ["kgf", "kgf song", "rocky bhai"],
    "pathaan": ["pathaan", "pathaan song", "shah rukh"],
    "jawan": ["jawan", "jawan song", "jawan movie"],
    "dunki": ["dunki", "dunki song", "dunki movie"],
    "gadar 2": ["gadar", "gadar 2", "gadar song"],
    "rocky aur rani": ["rocky", "rani", "rocky aur rani", "kjo"],
    "tu jhoothi main makkaar": ["tu jhoothi", "tjmm", "ranbir", "shraddha"],
    "bhool bhulaiyaa 2": ["bhool bhulaiyaa", "bb2", "kartik aaryan"],
    "brahmastra": ["brahmastra", "astra", "ranbir", "alia"],
    "tanhaji": ["tanhaji", "ajay devgn", "tanhaji song"],
    "chhichhore": ["chhichhore", "sushant", "chhichhore song"],
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  TRENDING KEYWORDS (Indian)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━

TRENDING_STYLES = [
    "hindi songs",
    "punjabi songs",
    "bollywood songs",
    "Instagram trending",
    "Love songs",
    "sad songs",
]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🌍 DETECT LANGUAGE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━

def detect_lang(title: str) -> str:
    """
    Detect language from song title using TWO methods:

    Method 1 — Title keywords ("punjabi song", "bhojpuri", "haryanvi" etc.)
    Method 2 — Artist name in title (AP Dhillon → punjabi, Arijit → hindi)

    Method 2 is the primary one because most Indian song titles
    ("Kesariya", "Brown Munde", "Dil Diyan Gallan") contain NO language word.
    """
    if not title:
        return "hindi"
    t = title.lower()

    # Method 1: explicit language keyword in title
    for lang, keys in LANG_DB.items():
        if any(x in t for x in keys):
            return lang

    # Method 2: artist name in title → infer language
    for lang, artists in ARTIST_LANG.items():
        if any(a in t for a in artists):
            return lang

    return "hindi"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎭 DETECT MOOD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━

def detect_mood(title):
    if not title:
        return "normal"
    title = title.lower()
    for mood, keys in MOOD_DB.items():
        if any(x in title for x in keys):
            return mood
    return "normal"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎤 DETECT ARTIST
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━

_NOISE_IN_ARTIST = re.compile(
    r"\b(official|video|music|audio|lyrics|lyrical|full|hd|hq|4k|song|new|latest|ft|feat|vs)\b",
    re.IGNORECASE,
)

def extract_artist(title: str) -> str:
    """
    Extract artist name from a YouTube title.

    Priority:
    1. ARTIST_DB lookup (known artists, most reliable)
    2. Parse the title — artist is usually AFTER the separator
       "Song Name - Artist" / "Song Name | Artist"
    3. ARTIST_LANG lookup (all known artists across languages)

    The old fallback (LEFT of "-") was WRONG — it returned the song name.
    YouTube format is almost always "Song - Artist", not "Artist - Song".
    """
    if not title:
        return ""
    title_lower = title.lower()

    # 1. ARTIST_DB (exact known artists)
    for artist, keys in ARTIST_DB.items():
        if any(x in title_lower for x in keys):
            return artist

    # 2. Parse separator — artist is on the RIGHT
    for sep in [" - ", " | ", " — "]:
        if sep in title:
            parts = title.split(sep)
            # parts[1:] are artist/movie/etc. Check each part
            for part in parts[1:]:
                part = _NOISE_IN_ARTIST.sub("", part).strip(" .,|")
                if 2 < len(part) < 45:
                    part_lower = part.lower()
                    # Skip if it looks like a label/channel (has "records", "music", "films")
                    if any(w in part_lower for w in ["records", "films", "movies", "productions", "entertainment"]):
                        continue
                    # Check if any ARTIST_LANG artist is mentioned in this part
                    for lang_artists in ARTIST_LANG.values():
                        for known_artist in lang_artists:
                            if known_artist in part_lower:
                                return known_artist
                    # Return cleaned part as best guess
                    return part.lower()
            break

    # 3. ARTIST_LANG scan (catches artists not in ARTIST_DB)
    for lang_artists in ARTIST_LANG.values():
        for known_artist in lang_artists:
            if known_artist in title_lower:
                return known_artist

    return ""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎬 DETECT MOVIE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━

def detect_movie(title):
    if not title:
        return ""
    title = title.lower()
    for movie, keys in MOVIE_DB.items():
        if any(x in title for x in keys):
            return movie
    return ""


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔤 TITLE NORMALIZER
# Problem: "Diwaniyat" vs "Diwaniyat - AP Dhillon" vs "Diwaniyat Lyrics"
# — different formats, same song. Two-step approach:
# Step 1: Split on " - " / " | " separators to drop artist suffix
# Step 2: Strip bracket content and noise words
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━

def normalize_title(title: str) -> str:
    if not title:
        return ""
    t = title.strip()

    # BUG FIX: Transliterate Devanagari (and any other script) to ASCII FIRST
    # so that "तुम ही हो" and "Tum Hi Ho" both become "tum hi ho" and can be
    # fuzzy-matched as the same song. Without this, Hindi-script and Roman-script
    # titles of the same song were never recognised as repeats.
    if _unidecode:
        t = _unidecode(t)

    t = t.lower().strip()

    # Step 1: Drop artist/channel suffix after separator
    for sep in [" - ", " | ", " — ", " ft ", " feat "]:
        if sep in t:
            t = t.split(sep)[0].strip()
            break

    # Step 2: Remove bracket content — "(Official Video)", "[Lyrics]", etc.
    t = re.sub(r"[\(\[\{][^\)\]\}]*[\)\]\}]", "", t)

    # Step 3: Remove noise words
    noise = [
        "official", "video", "music", "audio", "lyrics", "lyrical",
        "lyric", "full", "hd", "hq", "4k", "song", "new", "latest",
        "visualizer", "teaser", "promo",
    ]
    for w in noise:
        t = re.sub(rf"\b{w}\b", "", t)

    t = re.sub(r"\s+", " ", t).strip()
    return t


def _same_song(stored: str, candidate: str) -> bool:
    """
    Fuzzy title match — handles cases where one has extra words.
    e.g. stored="diwaniyat", candidate="diwaniyat ap dhillon shreya ghoshal"
    Both start with "diwaniyat" so they match.

    BUG FIX: Old code used `short in long` which caused false positives for
    common short phrases like "dil", "pyar", "rang" appearing as substrings
    in completely different songs, blocking valid candidates from autoplay.
    Now we only match when:
      - The longer title STARTS WITH the shorter (very high confidence same song)
      - AND the shorter title is at least 8 chars (prevents 4-7 char noise matches)
    """
    if not stored or not candidate:
        return False
    if len(stored) < 4 or len(candidate) < 4:
        return False
    short = stored if len(stored) <= len(candidate) else candidate
    long  = candidate if len(stored) <= len(candidate) else stored
    # Only match if long starts with short AND short is long enough to be meaningful
    return len(short) >= 8 and long.startswith(short)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔁 REPEAT CHECK (vidid + fuzzy title)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def is_repeat(chat_id, vidid, title: str = "") -> bool:
    current = time.time()
    # Keep last 60 songs played OR songs within last 6 hours — whichever is larger.
    # This prevents the same song from appearing within a ~60-song session window.
    if chat_id not in RECENT:
        RECENT[chat_id] = []
    recent = RECENT[chat_id]
    # Never expire the last 30 entries (time-independent repeat window)
    if len(recent) > 30:
        cutoff = current - 21600  # 6 hours
        recent = recent[-30:] + [(v, t) for v, t in recent[:-30] if current - t < cutoff]
    RECENT[chat_id] = recent
    if vidid in [v for v, _ in recent]:
        return True

    # title-based fuzzy check — same song from different channels/uploads
    if title:
        norm = normalize_title(title)
        if norm and len(norm) >= 4:
            if chat_id not in RECENT_TITLES:
                RECENT_TITLES[chat_id] = []
            recent_t = RECENT_TITLES[chat_id]
            if len(recent_t) > 30:
                cutoff = current - 21600
                recent_t = recent_t[-30:] + [(n, t) for n, t in recent_t[:-30] if current - t < cutoff]
            RECENT_TITLES[chat_id] = recent_t
            for stored_norm, _ in recent_t:
                if _same_song(stored_norm, norm):
                    return True

    return False


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ➕ ADD RECENT SONG + ARTIST
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def add_recent(chat_id, vidid, title: str = "", artist: str = "") -> None:
    if not vidid:
        return
    current = time.time()

    if chat_id not in RECENT:
        RECENT[chat_id] = []
    RECENT[chat_id].append((vidid, current))
    if len(RECENT[chat_id]) > 60:
        RECENT[chat_id] = RECENT[chat_id][-60:]

    if title:
        norm = normalize_title(title)
        if norm and len(norm) >= 4:
            if chat_id not in RECENT_TITLES:
                RECENT_TITLES[chat_id] = []
            RECENT_TITLES[chat_id].append((norm, current))
            if len(RECENT_TITLES[chat_id]) > 60:
                RECENT_TITLES[chat_id] = RECENT_TITLES[chat_id][-60:]

    # Track artist for diversity — keep last 10
    if artist:
        if chat_id not in RECENT_ARTISTS:
            RECENT_ARTISTS[chat_id] = []
        RECENT_ARTISTS[chat_id].append(artist.lower())
        if len(RECENT_ARTISTS[chat_id]) > 10:
            RECENT_ARTISTS[chat_id] = RECENT_ARTISTS[chat_id][-10:]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⏱ DURATION PARSER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _parse_duration_mins(duration_str: str) -> int:
    """
    Convert YouTube duration string to total minutes.

    BUG FIX: Old code did int(parts[0]) which treated "2:30:00" (2 hr 30 min)
    as 2 minutes and let it through the 7-minute cap. This caused 2-3 hour
    songs to play in autoplay.

    Handles:
      MM:SS      → minutes only        e.g. "4:32"  → 4 min
      HH:MM:SS   → hours + minutes     e.g. "2:30:00" → 150 min
    """
    try:
        parts = duration_str.strip().split(":")
        if len(parts) == 3:
            return int(parts[0]) * 60 + int(parts[1])   # HH:MM:SS
        elif len(parts) == 2:
            return int(parts[0])                          # MM:SS
    except Exception:
        pass
    return 0


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  SMART QUERY BUILDER (Indian Focus)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━

def build_smart_queries(title, artist, movie, lang, mood, recent_artists=None):
    """
    Build diverse search queries for autoplay.

    Changes vs. old version:
    - Mood queries are now LANG-prefixed (e.g. "sad hindi songs" not just "sad songs")
      so the wrong-language risk is much lower.
    - If the same artist has played 3+ times recently, SIMILAR_ARTISTS queries are
      injected to break the repetition loop.
    - Generic TRENDING_STYLES fallback removed — it could pull any genre.
    - Each language has a lang-specific generic fallback that stays in genre.
    """
    queries = []
    recent_artists = recent_artists or []

    clean_title = re.sub(
        r"official|video|lyrics|lyrical|hd|4k|music|song|audio|full|hq",
        "",
        title,
        flags=re.IGNORECASE,
    ).strip()

    # Title-based queries (most related)
    if clean_title:
        queries.append(f"{clean_title} song")
        queries.append(f"{clean_title} {lang}" if lang else clean_title)

    # Artist queries — but if same artist dominates recent history, rotate to similar
    if artist:
        same_artist_count = recent_artists.count(artist.lower())
        if same_artist_count >= 3:
            # Enough of this artist — add similar artists for variety
            for sim in SIMILAR_ARTISTS.get(artist.lower(), []):
                queries.append(f"{sim} {lang} songs" if lang else f"{sim} songs")
                queries.append(f"{sim} hits")
        else:
            queries.append(f"{artist} songs")
            queries.append(f"{artist} best songs")
            if lang:
                queries.append(f"{artist} {lang} hits")

    # Movie queries — very relevant (same movie = same vibe)
    if movie:
        queries.append(f"{movie} all songs")
        queries.append(f"{movie} jukebox")

    # Mood queries — always prefixed with lang to prevent genre cross-over
    lang_prefix = lang if lang in ("hindi", "punjabi", "bhojpuri", "haryanvi") else "hindi"
    if mood == "sad":
        queries += [f"sad {lang_prefix} songs", f"heartbreak {lang_prefix} songs", "bewafa songs"]
    elif mood == "love":
        queries += [f"romantic {lang_prefix} songs", f"love {lang_prefix} songs", "ishq wala love song"]
    elif mood == "party":
        queries += [f"party {lang_prefix} songs", f"dance {lang_prefix} songs"]
    elif mood == "wedding":
        queries += [f"wedding {lang_prefix} songs", "shaadi sangeet songs"]
    elif mood == "devotional":
        queries += ["bhajan hindi", "aarti songs", "bhakti songs"]
    elif mood == "oldschool":
        queries += [f"90s {lang_prefix} songs", f"old {lang_prefix} songs", "retro bollywood"]
    elif mood == "sufi":
        queries += ["sufi hindi songs", "qawwali hindi"]

    # Language-specific generic fallback — stays in the correct genre
    if lang == "hindi":
        queries += ["top bollywood songs 2024", "best hindi romantic songs"]
    elif lang == "punjabi":
        queries += ["top punjabi songs 2024", "best punjabi hits"]
    elif lang == "bhojpuri":
        queries += ["bhojpuri superhit songs", "bhojpuri new songs"]
    elif lang == "haryanvi":
        queries += ["haryanvi superhit songs", "haryanvi new songs 2024"]
    elif lang == "gujarati":
        queries += ["gujarati love songs", "garba songs new"]
    elif lang == "tamil":
        queries += ["tamil melody songs", "kollywood hits 2024"]
    elif lang == "telugu":
        queries += ["telugu melody songs", "tollywood hits 2024"]
    elif lang == "bengali":
        queries += ["bangla romantic songs", "bengali new songs"]
    elif lang == "marathi":
        queries += ["marathi romantic songs", "marathi new songs 2024"]
    elif lang == "urdu":
        queries += ["urdu ghazal songs", "urdu romantic songs"]

    # Deduplicate and sanitize
    bad_words = [
        "slowed", "reverb", "lofi", "8d", "live",
        "bass boosted", "cover", "karaoke", "instrumental", "sped up",
    ]
    final = []
    for q in queries:
        q_lower = q.lower()
        if not any(bad in q_lower for bad in bad_words):
            if q not in final and len(q) > 3:
                final.append(q)

    return final[:20]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎵 BEST SONG FINDER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━

def _detect_title_lang(title_lower: str) -> str:
    """Detect the language a song title belongs to based on keywords in title."""
    for lang_name, keywords in LANG_TITLE_INDICATORS.items():
        if any(kw in title_lower for kw in keywords):
            return lang_name
    return ""


async def get_best_song(chat_id, queries, last_title, last_vidid, artist, movie, mood, lang):
    """
    Search multiple queries, fetch up to 8 results each, score all candidates
    and return the best non-repeated song.

    Filtering rules (hard-skip — song is excluded entirely):
    1. Duration < 2 min or > 7 min.
    2. Bad content types (slowed, reverb, karaoke, etc.).
    3. Already in RECENT (last 60 songs / 6 hours).
    4. Devotional content (bhajan/aarti/chalisa) when current mood is NOT devotional.
    5. Wrong language — e.g. hindi session picks up bhojpuri/haryanvi/tamil.

    Scoring (higher = better match):
    - Title word overlap with current song.
    - Artist match.
    - Movie match.
    - Language match.
    - Mood match.
    - Penalty if same artist has appeared many times recently (for variety).
    """
    candidates = []
    original_words = last_title.lower().split()

    BAD_WORDS = [
        "slowed", "reverb", "8d", "lofi", "live", "mix", "dj remix",
        "bass boosted", "cover", "karaoke", "instrumental", "sped up",
    ]

    # Incompatible languages for this session's language
    blocked_langs = set(INCOMPATIBLE_LANGS.get(lang, []))

    # Recent artist counts — penalise over-repeated artists
    recent_artists_list = RECENT_ARTISTS.get(chat_id, [])

    # Shuffle queries so we don't probe the same order every time
    shuffled = list(queries)
    random.shuffle(shuffled)

    for q in shuffled:
        try:
            raw_results = await youtube_search_multi(q, limit=8)
            if not raw_results:
                continue

            for info in raw_results:
                try:
                    vidid = info.get("id", "")
                    if not vidid or vidid == last_vidid:
                        continue

                    raw_title = info.get("title", "")
                    title_lower = raw_title.lower()
                    duration_str = info.get("duration", "0:00") or "0:00"

                    # ── HARD FILTERS ──────────────────────────────────────

                    # 1. Bad content type
                    if any(x in title_lower for x in BAD_WORDS):
                        continue

                    # 2. Exact same song title — compare AFTER normalizing both
                    # (includes unidecode so "तुम ही हो" == "Tum Hi Ho" after norm)
                    if normalize_title(raw_title) == normalize_title(last_title):
                        continue

                    # 3. Duration 2–10 min (HH:MM:SS parsed correctly)
                    # BUG FIX: total_mins == 0 means duration was "0:00" or unknown
                    # (YouTube API sometimes omits it). Old code filtered these out
                    # which caused autoplay to find zero songs after 2–3 tracks.
                    # Allow unknown-duration songs through; only hard-block when
                    # the duration is known AND out of range.
                    total_mins = _parse_duration_mins(duration_str)
                    if total_mins != 0 and (total_mins < 2 or total_mins > 10):
                        continue

                    # 4. Already played recently
                    if await is_repeat(chat_id, vidid, raw_title):
                        continue

                    # 5. Devotional content when mood is NOT devotional
                    if mood != "devotional":
                        if any(dw in title_lower for dw in DEVOTIONAL_WORDS):
                            continue

                    # 6. Language cross-over — block incompatible languages
                    if blocked_langs:
                        title_detected_lang = _detect_title_lang(title_lower)
                        if title_detected_lang and title_detected_lang in blocked_langs:
                            continue

                    # ── SCORING ──────────────────────────────────────────

                    score = 0

                    # Title word overlap with current song
                    match_count = sum(
                        1 for w in original_words[:5] if w in title_lower and len(w) > 3
                    )
                    score += match_count * 15

                    # Artist match
                    if artist and artist.lower() in title_lower:
                        score += 50
                        if title_lower.startswith(artist.lower()):
                            score += 20

                    # Movie match
                    if movie and movie.lower() in title_lower:
                        score += 45

                    # Language match
                    if any(x in title_lower for x in LANG_DB.get(lang, [])):
                        score += 20

                    # Mood match
                    if mood != "normal":
                        if any(x in title_lower for x in MOOD_DB.get(mood, [])):
                            score += 15

                    # Artist repetition penalty — if this artist dominated recently, reduce score
                    if artist:
                        same_count = recent_artists_list.count(artist.lower())
                        if same_count >= 3:
                            score -= same_count * 10  # penalise, but don't hard-block

                    # Build details dict matching what stream() expects
                    thumb = ""
                    thumb_info = info.get("thumbnails") or []
                    if thumb_info and isinstance(thumb_info, list):
                        thumb = thumb_info[-1].get("url", "").split("?")[0]
                    if not thumb:
                        thumb = info.get("thumbnail", "").split("?")[0]

                    details = {
                        "title": raw_title,
                        "duration_min": duration_str,
                        "thumb": thumb,
                        "vidid": vidid,
                        "link": f"https://youtube.com/watch?v={vidid}",
                    }

                    candidates.append((score, vidid, details))

                except Exception:
                    continue

        except Exception:
            continue

        await asyncio.sleep(0.15)

    if not candidates:
        return None, None

    candidates.sort(key=lambda x: x[0], reverse=True)

    # Pick randomly among top-3 — prevents always picking the same winner
    # when multiple songs have close scores
    top_pool = candidates[:3]
    best = random.choice(top_pool)
    return best[1], best[2]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🖼 THUMBNAIL
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def get_thumbnail_direct(video_id):
    urls = [
        f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg",
        f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg",
        f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg",
    ]
    async with aiohttp.ClientSession() as session:
        for url in urls:
            try:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        return url
            except Exception:
                continue
    return urls[-1]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🇮🇳 INDIAN EMOJI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━

def get_indian_emoji():
    emojis = ["🇮🇳","🎧","❤️","🎶","✨","🎤","💖","🎵","🔥","💫","🎸","💕","🪩","🌙","💘","🥰","🎼","⚡","💞","🦋","🎶","💜","🎤","🌸","🕺","💃","💝","🎧","🌈","❣️","🪘","💗","✨","🔥"]
    return random.choice(emojis)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀 MAIN AUTOPLAY FUNCTION
#
# FIX 1: last_vidid param added — current song added to RECENT before
#         searching so it can never be picked as the next song.
#         get_best_song also hard-skips repeats (not just penalises).
# FIX 2: stop_stream() removed — assistant stays in VC between songs.
#         Stream ended naturally so bot is already in VC; calling
#         stop_stream() was the only reason it was leaving and rejoining.
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def auto_play_next(
    chat_id: int,
    original_chat_id: int,
    last_title: str = "",
    last_vidid: str = "",
    video: bool = False,
) -> bool:
    """
    Search for next Indian song smartly based on last song's context.
    Returns True if successfully started, False otherwise.
    """
    from VISHALMUSIC.utils.database import get_lang
    from VISHALMUSIC.utils.stream.stream import stream
    from strings import get_string

    # Double-play protection
    if AUTO_PLAYING.get(chat_id):
        return False

    AUTO_PLAYING[chat_id] = True

    try:
        data = await autoplay_db.find_one({"chat_id": chat_id})
        if not data or not data.get("status"):
            return False

        # Mark current song as recent BEFORE searching (so it's never picked again)
        lang = detect_lang(last_title) if last_title else "hindi"
        mood = detect_mood(last_title) if last_title else "normal"
        artist = extract_artist(last_title) if last_title else ""
        movie = detect_movie(last_title) if last_title else ""

        if last_vidid:
            await add_recent(chat_id, last_vidid, last_title, artist)

        indian_emoji = get_indian_emoji()

        try:
            msg = await app.send_message(
                original_chat_id,
                f"{indian_emoji} ᴀᴜᴛᴏᴘʟᴀʏ → ꜰᴇᴛᴄʜɪɴɢ ɴᴇxᴛ ꜱᴏɴɢ...........",
            )
        except Exception:
            return False

        if not last_title:
            queue = db.get(chat_id)
            if queue and len(queue) > 0:
                last_title = queue[0].get("title", "latest hindi song")
            else:
                last_title = "latest hindi song"
            lang = detect_lang(last_title)
            mood = detect_mood(last_title)
            artist = extract_artist(last_title)
            movie = detect_movie(last_title)

        # Pass recent_artists so query builder rotates away from overplayed artists
        recent_artists_list = RECENT_ARTISTS.get(chat_id, [])
        queries = build_smart_queries(last_title, artist, movie, lang, mood, recent_artists_list)

        vidid, details = await get_best_song(
            chat_id, queries, last_title, last_vidid, artist, movie, mood, lang
        )

        # Fallback chain — applies ALL the same hard filters (devotional, lang,
        # duration, repeat) so wrong-genre songs can't sneak in via fallback.
        if not vidid:
            blocked_langs = set(INCOMPATIBLE_LANGS.get(lang, []))
            fallback_queries = []
            if movie:
                fallback_queries += [f"{movie} jukebox", f"{movie} all songs"]
            if artist:
                # If same artist dominated recently, use similar artists
                same_count = recent_artists_list.count(artist.lower())
                if same_count >= 3:
                    for sim in SIMILAR_ARTISTS.get(artist.lower(), [artist]):
                        fallback_queries.append(f"{sim} {lang} songs")
                else:
                    fallback_queries += [f"{artist} {lang} songs", f"{artist} hits"]
            # Lang-specific fallbacks — stays in genre
            if lang == "hindi":
                fallback_queries += ["best hindi romantic songs", "bollywood melody songs 2024"]
            elif lang == "punjabi":
                fallback_queries += ["punjabi melody songs 2024", "best punjabi songs"]
            elif lang == "bhojpuri":
                fallback_queries += ["bhojpuri superhit songs 2024"]
            elif lang == "haryanvi":
                fallback_queries += ["haryanvi superhit songs 2024"]
            else:
                fallback_queries += [f"best {lang} songs 2024"]

            random.shuffle(fallback_queries)
            details = None
            for fq in fallback_queries:
                try:
                    fb_results = await youtube_search_multi(fq, limit=5)
                    for fb_info in fb_results:
                        fb_vidid = fb_info.get("id", "")
                        if not fb_vidid or fb_vidid == last_vidid:
                            continue
                        fb_title = fb_info.get("title", "")
                        fb_title_lower = fb_title.lower()
                        # Apply same hard filters as get_best_song
                        if await is_repeat(chat_id, fb_vidid, fb_title):
                            continue
                        fb_dur = fb_info.get("duration", "0:00") or "0:00"
                        try:
                            fb_mins = _parse_duration_mins(fb_dur)
                            # Same fix as get_best_song: allow unknown duration (0)
                            if fb_mins != 0 and (fb_mins < 2 or fb_mins > 10):
                                continue
                        except Exception:
                            pass
                        # Devotional filter
                        if mood != "devotional":
                            if any(dw in fb_title_lower for dw in DEVOTIONAL_WORDS):
                                continue
                        # Language filter
                        if blocked_langs:
                            fb_detected_lang = _detect_title_lang(fb_title_lower)
                            if fb_detected_lang and fb_detected_lang in blocked_langs:
                                continue
                        thumb_list = fb_info.get("thumbnails") or []
                        fb_thumb = (
                            thumb_list[-1].get("url", "").split("?")[0]
                            if thumb_list else fb_info.get("thumbnail", "").split("?")[0]
                        )
                        details = {
                            "title": fb_title,
                            "duration_min": fb_dur,
                            "thumb": fb_thumb,
                            "vidid": fb_vidid,
                            "link": f"https://youtube.com/watch?v={fb_vidid}",
                        }
                        vidid = fb_vidid
                        break
                    if vidid:
                        break
                except Exception:
                    continue

        if not vidid:
            try:
                await msg.edit_text("❌ ɴᴏ ꜱᴏɴɢ ꜰᴏᴜɴᴅ")
            except Exception:
                pass
            return False

        new_title = details.get("title", "") if details else ""
        new_artist = extract_artist(new_title) if new_title else ""
        await add_recent(chat_id, vidid, new_title, new_artist)

        link = f"https://youtube.com/watch?v={vidid}"

        try:
            thumb = details.get("thumb", "")
            if not thumb or not thumb.startswith("http"):
                thumb = await get_thumbnail_direct(vidid)
        except Exception:
            thumb = await get_thumbnail_direct(vidid)

        language = await get_lang(chat_id)
        _ = get_string(language)

        # BUG FIX: stream() has @capture_internal_err which silently swallows
        # exceptions. If join_call() inside stream() fails (e.g. NoActiveGroupCall,
        # network error), the decorator catches it and returns None. stream()
        # then continues: adds song to queue and sends a "now playing" photo —
        # but NOTHING is actually streaming. This function was returning True
        # (success) even in that case, so call.py never called leave_call(),
        # and the bot was stuck in VC playing nothing.
        #
        # Fix: after stream(), verify is_active_chat(). A successful join_call()
        # always calls add_active_chat(). If it's still False, the join failed.

        await stream(
            _,
            msg,
            app.id,
            {
                "link": link,
                "vidid": vidid,
                "title": details.get("title", "🇮🇳 ꜱɪᴍɪʟᴀʀ ɪɴᴅɪᴀɴ ꜱᴏɴɢ"),
                "duration_min": details.get("duration_min", "00:00"),
                "thumb": thumb,
            },
            chat_id,
            "🔁 ᴀᴜᴛᴏᴘʟᴀʏ",
            original_chat_id,
            video=video,          # pass through — video mode stays video
            streamtype="youtube",
        )

        from VISHALMUSIC.utils.database import is_active_chat as _verify_stream_active
        if not await _verify_stream_active(chat_id):
            try:
                await msg.edit_text("❌ ᴀᴜᴛᴏᴘʟᴀʏ ꜱᴛʀᴇᴀᴍ ꜰᴀɪʟᴇᴅ")
            except Exception:
                pass
            return False

        try:
            await msg.delete()
        except Exception:
            pass

        return True

    except Exception:
        return False

    finally:
        AUTO_PLAYING.pop(chat_id, None)
