#!/usr/bin/env python3
"""
Quick test script to verify colored buttons are working
"""
import asyncio
import aiohttp
import json

# Your bot token
BOT_TOKEN = "7807965637:AAGnQoaaL1Pe61d-7s-NZFl2Su4hEFCO66c"

# Test chat ID (your user ID)
CHAT_ID = "8262565708"

async def test_colored_buttons():
    """Test if colored buttons work via direct Bot API call"""
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    
    # Create colored buttons (NO DEFAULT!)
    buttons = {
        "inline_keyboard": [
            [
                {"text": "🔵 Primary (Blue)", "callback_data": "test1", "style": "primary"},
                {"text": "🟢 Success (Green)", "callback_data": "test2", "style": "success"}
            ],
            [
                {"text": "🔴 Danger (Red)", "callback_data": "test3", "style": "danger"}
            ]
        ]
    }
    
    payload = {
        "chat_id": CHAT_ID,
        "text": "🧪 **COLORED BUTTONS TEST**\n\n"
                "If you see colors:\n"
                "✅ Blue, Green, Red buttons = WORKING!\n\n"
                "If ALL buttons look same:\n"
                "❌ Telegram client too old (need Feb 2026+ version)\n\n"
                "Check your Telegram version in Settings!",
        "parse_mode": "Markdown",
        "reply_markup": buttons
    }
    
    print("🚀 Sending test message with colored buttons...")
    print(f"📍 Chat ID: {CHAT_ID}")
    print(f"🔑 Bot Token: {BOT_TOKEN[:20]}...")
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload) as resp:
            result = await resp.json()
            
            print(f"\n📊 Response Status: {resp.status}")
            print(f"📄 Response: {json.dumps(result, indent=2)}")
            
            if result.get("ok"):
                print("\n✅ SUCCESS! Message sent with colored buttons!")
                print(f"📱 Check Telegram (User ID: {CHAT_ID})")
                print("\n🎨 If you DON'T see colors:")
                print("   → Update Telegram app to latest version")
                print("   → Settings → About → Check version (need 11.x+)")
            else:
                error = result.get("description", "Unknown error")
                print(f"\n❌ FAILED: {error}")
                
                if "Unauthorized" in error:
                    print("   → BOT_TOKEN is invalid!")
                elif "chat not found" in error:
                    print("   → CHAT_ID is wrong or bot not started!")

if __name__ == "__main__":
    asyncio.run(test_colored_buttons())
