# ═══════════════════════════════════════════════════════════
#        😎  VISHAL MUSIC BOT  😎
#   GitHub : github.com/ItsMeVishal0/VishalMusic
#   Developer : @ItsMeVishalBots | Telegram
#   Module : Markdown Help Guide
# ═══════════════════════════════════════════════════════════
from pyrogram.enums import ChatType, ParseMode
from pyrogram.filters import command
from pyrogram.types import Message

from VISHALMUSIC import app
MARKDOWN = """
ʀᴇᴀᴅ ᴛʜᴇ ʙᴇʟᴏᴡ ᴛᴇxᴛ ᴄᴀʀᴇғᴜʟʟʏ ᴛᴏ ғɪɴᴅ ᴏᴜᴛ ʜᴏᴡ ғᴏʀᴍᴀᴛᴛɪɴɢ ᴡᴏʀᴋs!

<u>sᴜᴘᴘᴏʀᴛᴇᴅ ғɪʟʟɪɴɢs:</u>

{GROUPNAME} - ɢʀᴏᴜᴘ's ɴᴀᴍᴇ
{NAME} - ᴜsᴇʀ ɴᴀᴍᴇ
{ID} - ᴜsᴇʀ ɪᴅ
{FIRSTNAME} - ᴜsᴇʀ ғɪʀsᴛ ɴᴀᴍᴇ 
{SURNAME} - ɪғ ᴜsᴇʀ ʜᴀs sᴜʀɴᴀᴍᴇ sᴏ ᴛʜɪs ᴡɪʟʟ sʜᴏᴡ sᴜʀɴᴀᴍᴇ ᴇʟsᴇ ɴᴏᴛʜɪɴɢ
{USERNAME} - ᴜsᴇʀ ᴜsᴇʀɴᴀᴍᴇ

{TIME} - ᴛᴏᴅᴀʏ  ᴛɪᴍᴇ
{DATE} - ᴛᴏᴅᴀʏ ᴅᴀᴛᴇ 
{WEEKDAY} - ᴛᴏᴅᴀʏ ᴡᴇᴇᴋᴅᴀʏ 

<b><u>NOTE:</u></b> ғɪʟʟɪɴɢs ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ᴡᴇʟᴄᴏᴍᴇ ᴍᴏᴅᴜʟᴇ.

<u>sᴜᴘᴘᴏʀᴛᴇᴅ ғᴏʀᴍᴀᴛᴛɪɴɢ:</u>

<code>**Bold**</code> : ᴛʜɪs ᴡɪʟʟ sʜᴏᴡ ᴀs <b>Bold</b> ᴛᴇxᴛ.
<code>~~strike~~</code>: ᴛʜɪs ᴡɪʟʟ sʜᴏᴡ ᴀs <strike>strike</strike> ᴛᴇxᴛ.
<code>__italic__</code>: ᴛʜɪs ᴡɪʟʟ sʜᴏᴡ ᴀs <i>italic</i> ᴛᴇxᴛ
<code>--underline--</code>: ᴛʜɪs ᴡɪʟʟ sʜᴏᴡ ᴀs <u>underline</u> ᴛᴇxᴛ.
<code>`code words`</code>: ᴛʜɪs ᴡɪʟʟ sʜᴏᴡ ᴀs <code>code</code> ᴛᴇxᴛ.
<code>||spoiler||</code>: ᴛʜɪs ᴡɪʟʟ sʜᴏᴡ ᴀs <spoiler>Spoiler</spoiler> ᴛᴇxᴛ.
<code>[hyperlink](google.com)</code>: ᴛʜɪs ᴡɪʟʟ ᴄʀᴇᴀᴛᴇ ᴀ <a href='https://www.google.com'>hyperlink</a> text
<code>> hello</code>  ᴛʜɪs ᴡɪʟʟ sʜᴏᴡ ᴀs <blockquote>hello</blockquote>
<b>Note:</b> ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ʙᴏᴛʜ ᴍᴀʀᴋᴅᴏᴡɴ & ʜᴛᴍʟ ᴛᴀɢs.


<u>ʙᴜᴛᴛᴏɴ ғᴏʀᴍᴀᴛᴛɪɴɢ:</u>

- > <blockquote>text ~ [button text, button link]</blockquote>


<u>ᴇxᴀᴍᴘʟᴇ:</u>

<b>example</b>  
<blockquote><i>button with markdown</i> <code>formatting</code> ~ [button text, https://google.com]</blockquote>
"""



@app.on_message(command("markdownhelp"))
async def mkdwnhelp(_, m: Message):
    await m.reply(
        MARKDOWN, parse_mode=ParseMode.HTML, disable_web_page_preview=True
    )
    return
