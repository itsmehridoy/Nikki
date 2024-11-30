from random import choice

from pyrogram import enums, filters
from pyrogram.types import CallbackQuery, Message

from Powers.bot_class import Nikki
from Powers.utils.kbhelpers import ikb

async def gen_formatting_kb(m):
    return ikb(
        [
            [
                ("ᴍᴀʀᴋᴅᴏᴡɴ", "formatting.md_formatting"),
                ("ғɪʟʟɪɴɢs", "formatting.fillings"),
            ],
            [("ʀᴀɴᴅᴏᴍ", "formatting.random_content")],
        ],
        True,
        "commands"
    )

@Nikki.on_message(
    filters.command(["markdownhelp", "formatting"]) & filters.private,
)
async def markdownhelp(c: Nikki, m: Message):
    await c.send_message(
        m.chat.id,
        text=f"{__HELP__}",
        reply_markup=(await gen_formatting_kb(m)),
        protect_content=True,
    )
    return


@Nikki.on_callback_query(filters.regex("^formatting."))
async def get_formatting_info(c: Nikki, q: CallbackQuery):
    cmd = q.data.split(".")[1]
    kb = ikb([[("ʙᴀᴄᴋ", "back.formatting")]])

    if cmd == "md_formatting":
        
        txt = """<b>ᴍᴀʀᴋᴅᴏᴡɴ ғᴏʀᴍᴀᴛᴛɪɴɢ</b>
ʏᴏᴜ ᴄᴀɴ ғᴏʀᴍᴀᴛ ʏᴏᴜʀ ᴍᴇssᴀɢᴇ ᴜsɪɴɢ ʙᴏʟᴅ, ɪᴛᴀʟɪᴄ, ᴜɴᴅᴇʀʟɪɴᴇ, sᴛʀɪᴋᴇ ᴀɴᴅ ᴍᴜᴄʜ ᴍᴏʀᴇ. ɢᴏ ᴀʜᴇᴀᴅ ᴀɴᴅ ᴇxᴘᴇʀɪᴍᴇɴᴛ!

**ɴᴏᴛᴇ**: ɪᴛ sᴜᴘᴘᴏʀᴛs ᴛᴇʟᴇɢʀᴀᴍ ᴜsᴇʀ ʙᴀsᴇᴅ ғᴏʀᴍᴀᴛᴛɪɴɢ ᴀs ᴡᴇʟʟ ᴀs ʜᴛᴍʟ ᴀɴᴅ ᴍᴀʀᴋᴅᴏᴡɴ ғᴏʀᴍᴀᴛᴛɪɴɢs.
<b>sᴜᴘᴘᴏʀᴛᴇᴅ ᴍᴀʀᴋᴅᴏᴡɴ:</b>
• `ᴄᴏᴅᴇ ᴡᴏʀᴅs`: ʙᴀᴄᴋᴛɪᴄᴋs ᴀʀᴇ ᴜsᴇᴅ ғᴏʀ ᴍᴏɴᴏsᴘᴀᴄᴇ ғᴏɴᴛs. sʜᴏᴡs ᴀs: <code>ᴄᴏᴅᴇ ᴡᴏʀᴅs.</code>
• __ɪᴛᴀʟɪᴄ__: ᴜɴᴅᴇʀsᴄᴏʀᴇs ᴀʀᴇ ᴀʀᴇ ғᴏʀ ɪᴛᴀʟɪᴄ ғᴏɴᴛs. sʜᴏᴡs ᴀs: <i>ɪᴛᴀʟɪᴄ ᴡᴏʀᴅs.</i>
• **ʙᴏʟᴅ**: ᴀsᴛᴇʀɪsᴋs ᴀʀᴇ ᴜsᴇᴅ ғᴏʀ ʙᴏʟᴅ ғᴏɴᴛs. sʜᴏᴡs ᴀs: <b>ʙᴏʟᴅ ᴡᴏʀᴅs.</b>
• ```pre```: ᴛᴏ ᴍᴀᴋᴇ ᴛʜᴇ ғᴏʀᴍᴀᴛᴛᴇʀ ɪɢɴᴏʀᴇ ᴏᴛʜᴇʀ ғᴏʀᴍᴀᴛᴛɪɴɢ ᴄʜᴀʀᴀᴄᴛᴇʀs ɪɴsɪᴅᴇ ᴛʜᴇ ᴛᴇxᴛ ғᴏʀᴍᴀᴛᴛᴇᴅ ᴡɪᴛʜ '```', ʟɪᴋᴇ: **ʙᴏʟᴅ** | *ʙᴏʟᴅ*.
• --ᴜɴᴅᴇʀʟɪɴᴇ: ᴛᴏ ᴍᴀᴋᴇ ᴛᴇxᴛ <u>ᴜɴᴅᴇʀʟɪɴᴇ.</u>
• ~~sᴛʀɪᴋᴇ~~: ᴛɪʟᴅᴇs ᴀʀᴇ ᴜsᴇᴅ ғᴏʀ sᴛʀɪᴋᴇᴛʜʀᴏᴜɢʜ. sʜᴏᴡs ᴀs: <strike>sᴛʀɪᴋᴇ</strike>
• ||sᴘᴏɪʟᴇʀ||: ᴅᴏᴜʙʟᴇ ᴠᴇʀᴛɪᴄᴀʟ ʙᴀʀs ᴀʀᴇ ᴜsᴇᴅ ғᴏʀ sᴘᴏɪʟᴇʀs. sʜᴏᴡs ᴀs: <spoiler>sᴘᴏɪʟᴇʀ</spoiler>
• <code>[ʜʏᴘᴇʀʟɪɴᴋ](t.me/MissNikkibot)</code>: ᴛʜɪs ɪs ᴛʜᴇ ғᴏʀᴍᴀᴛᴛɪɴɢ ᴜsᴇᴅ ғᴏʀ ʜʏᴘᴇʀʟɪɴᴋs. sʜᴏᴡs ᴀs: <a href="https://example.com/">ʜʏᴘᴇʀʟɪɴᴋ</a>
• <code>[ᴍʏ ʙᴜᴛᴛᴏɴ](buttonurl://t.me/MissNikkibot)</code>: ᴛʜɪs ɪs ᴛʜᴇ ғᴏʀᴍᴀᴛᴛɪɴɢ ᴜsᴇᴅ ғᴏʀ ᴄʀᴇᴀᴛɪɴɢ ʙᴜᴛᴛᴏɴs. ᴛʜɪs ᴇxᴀᴍᴘʟᴇ ᴡɪʟʟ ᴄʀᴇᴀᴛᴇ ᴀ ʙᴜᴛᴛᴏɴ ɴᴀᴍᴇᴅ "ᴍʏ ʙᴜᴛᴛᴏɴ" ᴡʜɪᴄʜ ᴏᴘᴇɴs <code>example.com</code> ᴡʜᴇɴ ᴄʟɪᴄᴋᴇᴅ.
ɪғ ʏᴏᴜ ᴡᴏᴜʟᴅ ʟɪᴋᴇ ᴛᴏ sᴇɴᴅ ʙᴜᴛᴛᴏɴs ᴏɴ ᴛʜᴇ sᴀᴍᴇ ʀᴏᴡ, ᴜsᴇ ᴛʜᴇ :same ғᴏʀᴍᴀᴛᴛɪɴɢ.
ᴇxᴀᴍᴘʟᴇ:
<code>[ʙᴜᴛᴛᴏɴ 1](buttonurl:example.com)</code>
<code>[ʙᴜᴛᴛᴏɴ 2](buttonurl://example.com:same)</code>
<code>[ʙᴜᴛᴛᴏɴ 3](buttonurl://example.com)</code>
ᴛʜɪs ᴡɪʟʟ sʜᴏᴡ ʙᴜᴛᴛᴏɴ 1 ᴀɴᴅ 2 ᴏɴ ᴛʜᴇ sᴀᴍᴇ ʟɪɴᴇ, ᴡʜɪʟᴇ 3 ᴡɪʟʟ ʙᴇ ᴜɴᴅᴇʀɴᴇᴀᴛʜ."""
        await q.message.edit_text(
            text=txt,
            reply_markup=kb,
            parse_mode=enums.ParseMode.HTML,
        )            
    elif cmd == "fillings":
        await q.message.edit_text(
            text="""<b>ғɪʟʟɪɴɢs</b>

ʏᴏᴜ ᴄᴀɴ ᴀʟsᴏ ᴄᴜsᴛᴏᴍɪsᴇ ᴛʜᴇ ᴄᴏɴᴛᴇɴᴛs ᴏғ ʏᴏᴜʀ ᴍᴇssᴀɢᴇ ᴡɪᴛʜ ᴄᴏɴᴛᴇxᴛᴜᴀʟ ᴅᴀᴛᴀ. ғᴏʀ ᴇxᴀᴍᴘʟᴇ, ʏᴏᴜ ᴄᴏᴜʟᴅ ᴍᴇɴᴛɪᴏɴ ᴀ ᴜsᴇʀ ʙʏ ɴᴀᴍᴇ ɪɴ ᴛʜᴇ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ, ᴏʀ ᴍᴇɴᴛɪᴏɴ ᴛʜᴇᴍ ɪɴ ᴀ ғɪʟᴛᴇʀ!
ʏᴏᴜ ᴄᴀɴ ᴜsᴇ ᴛʜᴇsᴇ ᴛᴏ ᴍᴇɴᴛɪᴏɴ ᴀ ᴜsᴇʀ ɪɴ ɴᴏᴛᴇs ᴛᴏᴏ!

<b>sᴜᴘᴘᴏʀᴛᴇᴅ ғɪʟʟɪɴɢs:</b>
• <code>{first}</code>: ᴛʜᴇ ᴜsᴇʀ's ғɪʀsᴛ ɴᴀᴍᴇ.     
• <code>{last}</code>: ᴛʜᴇ ᴜsᴇʀ's ʟᴀsᴛ ɴᴀᴍᴇ.      
• <code>{fullname}</code>: ᴛʜᴇ ᴜsᴇʀ's ғᴜʟʟ ɴᴀᴍᴇ.      
• <code>{username}</code>: ᴛʜᴇ ᴜsᴇʀ's ᴜsᴇʀɴᴀᴍᴇ. ɪғ ᴛʜᴇʏ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴏɴᴇ, ᴍᴇɴᴛɪᴏɴs ᴛʜᴇ ᴜsᴇʀ ɪɴsᴛᴇᴀᴅ      
• <code>{mention}</code>: ᴍᴇɴᴛɪᴏɴs ᴛʜᴇ ᴜsᴇʀ ᴡɪᴛʜ ᴛʜᴇɪʀ ғɪʀsᴛɴᴀᴍᴇ      
• <code>{id}</code>: ᴛʜᴇ ᴜsᴇʀ's ɪᴅ      
• <code>{chatname}</code>: ᴛʜᴇ ᴄʜᴀᴛ's ɴᴀᴍᴇ.""",
            reply_markup=kb,
            parse_mode=enums.ParseMode.HTML,
        )
    elif cmd == "random_content":
        await q.message.edit_text(
            text="""<b>ʀᴀɴᴅᴏᴍ ᴄᴏɴᴛᴇɴᴛ</b>

ᴀɴᴏᴛʜᴇʀ ᴛʜɪɴɢ ᴛʜᴀᴛ ᴄᴀɴ ʙᴇ ғᴜɴ, ɪs ᴛᴏ ʀᴀɴᴅᴏᴍɪsᴇ ᴛʜᴇ ᴄᴏɴᴛᴇɴᴛs ᴏғ ᴀ ᴍᴇssᴀɢᴇ. ᴍᴀᴋᴇ ᴛʜɪɴɢs ᴀ ʟɪᴛᴛʟᴇ ᴍᴏʀᴇ ᴘᴇʀsᴏɴᴀʟ ʙʏ ᴄʜᴀɴɢɪɴɢ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇs, ᴏʀ ᴄʜᴀɴɢɪɴɢ ɴᴏᴛᴇs!

<b>ʜᴏᴡ ᴛᴏ ᴜsᴇ ʀᴀɴᴅᴏᴍ ᴄᴏɴᴛᴇɴᴛs:</b>
- %%%: ᴛʜɪs sᴇᴘᴀʀᴀᴛᴏʀ ᴄᴀɴ ʙᴇ ᴜsᴇᴅ ᴛᴏ ᴀᴅᴅ "ʀᴀɴᴅᴏᴍ" ʀᴇᴘʟɪᴇs ᴛᴏ ᴛʜᴇ ʙᴏᴛ.
ғᴏʀ ᴇxᴀᴍᴘʟᴇ:
 <code>ʜᴇʟʟᴏ
    %%%
 ʜᴏᴡ ᴀʀᴇ ʏᴏᴜ</code>
 
ᴛʜɪs ᴡɪʟʟ ʀᴀɴᴅᴏᴍʟʏ ᴄʜᴏᴏsᴇ ʙᴇᴛᴡᴇᴇɴ sᴇɴᴅɪɴɢ ᴛʜᴇ ғɪʀsᴛ ᴍᴇssᴀɢᴇ, "ʜᴇʟʟᴏ", ᴏʀ ᴛʜᴇ sᴇᴄᴏɴᴅ ᴍᴇssᴀɢᴇ, "ʜᴏᴡ ᴀʀᴇ ʏᴏᴜ".
ᴜsᴇ ᴛʜɪs ᴛᴏ ᴍᴀᴋᴇ ɴɪᴋᴋɪ ғᴇᴇʟ ᴀ ʙɪᴛ ᴍᴏʀᴇ ᴄᴜsᴛᴏᴍɪsᴇᴅ! (ᴏɴʟʏ ᴡᴏʀᴋs ɪɴ ғɪʟᴛᴇʀs/ɴᴏᴛᴇs)

<b>ᴇxᴀᴍᴘʟᴇ ᴡᴇʟᴄᴏᴍᴇ ᴍᴇssᴀɢᴇ:</b>
- ᴇᴠᴇʀʏ ᴛɪᴍᴇ ᴀ ɴᴇᴡ ᴜsᴇʀ ᴊᴏɪɴs, ᴛʜᴇʏ'ʟʟ ʙᴇ ᴘʀᴇsᴇɴᴛᴇᴅ ᴡɪᴛʜ ᴏɴᴇ ᴏғ ᴛʜᴇ ᴛʜʀᴇᴇ ᴍᴇssᴀɢᴇs sʜᴏᴡɴ ʜᴇʀᴇ.
 -> /filter "ʜᴇʏ"
 ʜᴇʟʟᴏ ᴛʜᴇʀᴇ <code>{first}</code>!
     %%%
 ᴏᴏᴏᴏʜ, <code>{first}</code> ʜᴏᴡ ᴀʀᴇ ʏᴏᴜ?
  %%%
sᴜᴘ? <code>{first}</code>""",
            reply_markup=kb,
            parse_mode=enums.ParseMode.HTML,
        )

    await q.answer()
    return

@Nikki.on_callback_query(filters.regex("^format."))
async def get_ex_info(c: Nikki, q: CallbackQuery):
    cmd = q.data.split(".")[1]
    xb = ikb([[("ғɪʟʟɪɴɢs", "formatting.fillings")],[("ʙᴀᴄᴋ", "commands")]])

    if cmd == "ex_filters":
        
        txt = """<b>ᴇxᴀᴍᴘʟᴇ ᴜsᴀɢᴇ ᴏғ ғɪʟᴛᴇʀ's</b>

ғɪʟᴛᴇʀs ᴄᴀɴ sᴇᴇᴍ ǫᴜɪᴛᴇ ᴄᴏᴍᴘʟɪᴄᴀᴛᴇᴅ; sᴏ ʜᴇʀᴇ ᴀʀᴇ sᴏᴍᴇ ᴇxᴀᴍᴘʟᴇs, sᴏ ʏᴏᴜ ᴄᴀɴ ɢᴇᴛ sᴏᴍᴇ ɪɴsᴘɪʀᴀᴛɪᴏɴ.

<b>ᴇxᴀᴍᴘʟᴇs:</b>
- sᴇᴛ ᴀ ғɪʟᴛᴇʀ:
•> <code>/filter hello Hello there! How are you?</code>

- sᴇᴛ ᴀ ғɪʟᴛᴇʀ ᴡʜɪᴄʜ ᴜsᴇs ᴛʜᴇ ᴜsᴇʀs ɴᴀᴍᴇ ᴛʜʀᴏᴜɢʜ ғɪʟʟɪɴɢs:
•> <code>/filter hello Hello there {first}! How are you?</code>

- sᴇᴛ ᴀ ғɪʟᴛᴇʀ ᴏɴ ᴀ sᴇɴᴛᴇɴᴄᴇ:
•> <code>/filter "hello friend" Hello back! Long time no see!</code>


- ᴛᴏ ɢᴇᴛ ᴛʜᴇ ᴜɴғᴏʀᴍᴀᴛᴛᴇᴅ ᴠᴇʀsɪᴏɴ ᴏғ ᴀ ғɪʟᴛᴇʀ, ᴛᴏ ᴄᴏᴘʏ ᴀɴᴅ ᴇᴅɪᴛ ɪᴛ, sɪᴍᴘʟʏ sᴀʏ ᴛʜᴇ ᴛʀɪɢɢᴇʀ ғᴏʟʟᴏᴡᴇᴅ ʙʏ ᴛʜᴇ ᴋᴇʏᴡᴏʀᴅ "noformat":
•> trigger noformat

- ᴛᴏ sᴀᴠᴇ ᴀ "ᴘʀᴏᴛᴇᴄᴛᴇᴅ" ғɪʟᴛᴇʀ, ᴡʜɪᴄʜ ᴄᴀɴ'ᴛ ʙᴇ ғᴏʀᴡᴀʀᴅᴇᴅ:
•> <code>/filter "example" This filter cant be forwarded {protect}</code>

- ᴛᴏ sᴀᴠᴇ ᴀ ғɪʟᴇ, ɪᴍᴀɢᴇ, ɢɪғ, ᴏʀ ᴀɴʏ ᴏᴛʜᴇʀ ᴀᴛᴛᴀᴄʜᴍᴇɴᴛ, sɪᴍᴘʟʏ ʀᴇᴘʟʏ ᴛᴏ ғɪʟᴇ ᴡɪᴛʜ:
•> <code>/filter trigger</code>

- ᴛᴏ sᴇᴛ ᴀ ғɪʟᴛᴇʀ ᴡʜɪᴄʜ ʀᴇᴘʟɪᴇs ᴡɪᴛʜ ᴀ ʀᴀɴᴅᴏᴍ ᴀɴsᴡᴇʀ ғʀᴏᴍ ᴀ ᴘʀᴇsᴇᴛ ʟɪsᴛ:
•> <code>/filter test
Answer one
%%%
Answer two</code>"""
        await q.message.edit_text(
            text=txt,
            reply_markup=xb,
            parse_mode=enums.ParseMode.HTML,
        )
    elif cmd == "notes_content":
        await q.message.edit_text(
            text="""<b>ᴇxᴀᴍᴘʟᴇ ᴜsᴀɢᴇ ᴏғ ɴᴏᴛᴇs</b>
ɴᴏᴛᴇs ᴄᴀɴ sᴇᴇᴍ ǫᴜɪᴛᴇ ᴄᴏᴍᴘʟɪᴄᴀᴛᴇᴅ; sᴏ ʜᴇʀᴇ ᴀʀᴇ sᴏᴍᴇ ᴇxᴀᴍᴘʟᴇs, sᴏ ʏᴏᴜ ᴄᴀɴ ɢᴇᴛ sᴏᴍᴇ ɪɴsᴘɪʀᴀᴛɪᴏɴ.

<b>ᴇxᴀᴍᴘʟᴇs:</b>
- sᴀᴠɪɴɢ ᴀ ɴᴏᴛᴇ. ɴᴏᴡ, ᴀɴʏᴏɴᴇ ᴜsɪɴɢ <code>#test</code> ᴏʀ <code>/get test</code> ᴡɪʟʟ sᴇᴇ ᴛʜɪs ᴍᴇssᴀɢᴇ. ᴛᴏ sᴀᴠᴇ ᴀɴ ɪᴍᴀɢᴇ, ɢɪғ, sᴛɪᴄᴋᴇʀ, ᴏʀ ᴀɴʏ ᴏᴛʜᴇʀ ᴋɪɴᴅ ᴏғ ᴅᴀᴛᴀ, sɪᴍᴘʟʏ ʀᴇᴘʟʏ ᴛᴏ ᴛʜᴀᴛ ᴍᴇssᴀɢᴇ
•> <code>/save test This is a fancy note!</code>

- ᴛᴏ ʀᴇᴛʀɪᴇᴠᴇ ᴀ ɴᴏᴛᴇ ᴡɪᴛʜᴏᴜᴛ ғᴏʀᴍᴀᴛᴛɪɴɢ, ᴀᴅᴅ noformat|raw ᴀғᴛᴇʀ ᴛʜᴇ ɢᴇᴛ ᴄᴏᴍᴍᴀɴᴅ. ᴛʜɪs ᴡɪʟʟ ʀᴇᴛʀɪᴇᴠᴇ ᴛʜᴇ ɴᴏᴛᴇ ᴡɪᴛʜ ɴᴏ ғᴏʀᴍᴀᴛᴛɪɴɢ, ᴀʟʟᴏᴡɪɴɢ ʏᴏᴜ ᴛᴏ ᴄᴏᴘʏ ᴀɴᴅ ᴇᴅɪᴛ ɪᴛ.
-> <code>/get notename noformat</code>

- ᴛᴏ sᴀᴠᴇ ᴀɴ ᴀᴅᴍɪɴᴏɴʟʏ ɴᴏᴛᴇ:
-> <code>/save example This note will only be opened by admins {admin}</code>

- ᴛᴏ sᴀᴠᴇ ᴀ "protected" ɴᴏᴛᴇ, ᴡʜɪᴄʜ ᴄᴀɴ'ᴛ ʙᴇ ғᴏʀᴡᴀʀᴅᴇᴅ:
-> <code>/save example This note cant be forwarded {protect}</code>

- ᴛᴏ sᴇɴᴅ ᴀʟʟ ɴᴏᴛᴇs ᴛᴏ ᴛʜᴇ ᴜsᴇʀ's ᴘᴍ [ʀᴇᴄᴏᴍᴍᴇɴᴅᴇᴅ]:
-> <code>/privatenotes on</code>""",
            reply_markup=xb,
            parse_mode=enums.ParseMode.HTML,
        )

    await q.answer()
    return


@Nikki.on_callback_query(filters.regex("^back."))
async def send_mod_help(_, q: CallbackQuery):
    await q.message.edit_text(
        text="""ᴍᴇ sᴜᴘᴘᴏʀᴛs ᴀ ʟᴀʀɢᴇ ɴᴜᴍʙᴇʀ ᴏғ ғᴏʀᴍᴀᴛᴛɪɴɢ ᴏᴘᴛɪᴏɴs ᴛᴏ ᴍᴀᴋᴇ ʏᴏᴜʀ ᴍᴇssᴀɢᴇs ᴍᴏʀᴇ ᴇxᴘʀᴇssɪᴠᴇ. ᴛᴀᴋᴇ ᴀ ʟᴏᴏᴋ ʙʏ ᴄʟɪᴄᴋɪɴɢ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ!""",
        reply_markup=(await gen_formatting_kb(q.message)),
    )
    await q.answer()
    return


__PLUGIN__ = "Fᴏʀᴍᴀᴛᴛɪɴɢ"

__alt_name__ = ["formatting", "markdownhelp", "markdown"]
__buttons__ = [
    [
        ("ᴍᴀʀᴋᴅᴏᴡɴ", "formatting.md_formatting"),
        ("ғɪʟʟɪɴɢs", "formatting.fillings"),
    ],
    [("ʀᴀɴᴅᴏᴍ", "formatting.random_content")],
]

__HELP__ = """
ᴍᴇ sᴜᴘᴘᴏʀᴛs ᴀ ʟᴀʀɢᴇ ɴᴜᴍʙᴇʀ ᴏғ ғᴏʀᴍᴀᴛᴛɪɴɢ ᴏᴘᴛɪᴏɴs ᴛᴏ ᴍᴀᴋᴇ ʏᴏᴜʀ ᴍᴇssᴀɢᴇs ᴍᴏʀᴇ ᴇxᴘʀᴇssɪᴠᴇ. ᴛᴀᴋᴇ ᴀ ʟᴏᴏᴋ ʙʏ ᴄʟɪᴄᴋɪɴɢ ᴛʜᴇ ʙᴜᴛᴛᴏɴs ʙᴇʟᴏᴡ!"""
