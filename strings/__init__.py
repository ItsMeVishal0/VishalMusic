# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#        ðŸ˜Ž  VISHAL MUSIC BOT  ðŸ˜Ž
#   GitHub : github.com/ItsMeVishal0/VishalMusic
#   Developer : @ItsMeVishalBots | Telegram
#   Module : Multi-Language String Loader (15+ Languages)
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•

import os
import yaml
try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader

languages = {}
languages_present = {}

def get_string(lang: str):
    return languages.get(lang, languages.get("en", {}))

lang_path = "./strings/langs/"

for filename in os.listdir(lang_path):
    if "en" not in languages:
        with open(os.path.join(lang_path, "en.yml"), encoding="utf8") as f:
            languages["en"] = yaml.load(f, Loader=SafeLoader)
        languages_present["en"] = languages["en"].get("name", "English")

    if filename.endswith(".yml"):
        language_name = filename[:-4]
        if language_name == "en":
            continue
        with open(os.path.join(lang_path, filename), encoding="utf8") as f:
            languages[language_name] = yaml.load(f, Loader=SafeLoader)

        # Fill missing keys from English
        for item in languages["en"]:
            if item not in languages[language_name]:
                languages[language_name][item] = languages["en"][item]

        # Safely set display name
        lang_display = languages[language_name].get("name", language_name)
        languages_present[language_name] = lang_display

print(f"[INFO] Loaded {len(languages_present)} languages: {', '.join(languages_present.keys())}")

# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
#        ðŸ˜Ž  VISHAL MUSIC BOT  ðŸ˜Ž
#   github.com/ItsMeVishal0/VishalMusic
# â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•
