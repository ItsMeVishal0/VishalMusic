from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ParseMode
import requests
from VISHALMUSIC import app


@app.on_message(filters.command("population"))
async def country_command_handler(client: Client, message: Message):
    if len(message.text.split()) < 2:
        return await message.reply_text(
            "Please provide a valid country code. Example: /population US"
        )

    country_code = message.text.split(maxsplit=1)[1].strip()
    api_url = f"https://restcountries.com/v3.1/alpha/{country_code}"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
        country_info = response.json()

        if country_info:
            country_name = country_info[0].get("name", {}).get("common", "N/A")
            capital = country_info[0].get("capital", ["N/A"])[0]
            population = country_info[0].get("population", "N/A")

            response_text = (
                f"🌍 **Country Information**\n\n"
                f"**Name:** {country_name}\n"
                f"**Capital:** {capital}\n"
                f"**Population:** {population:,}"
            )
        else:
            response_text = "❌ Country information could not be fetched."

    except requests.exceptions.HTTPError:
        response_text = "❌ Invalid country code. Please use a valid ISO code like `IN`, `US`, etc."
    except Exception as err:
        print(f"Error: {err}")
        response_text = "⚠️ An unexpected error occurred. Please try again later."

    await message.reply_text(response_text, parse_mode=ParseMode.MARKDOWN)
