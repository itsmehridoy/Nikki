import html
import re
import time
import json
import asyncio
import aiofiles
import requests
import pyfiglet
from traceback import format_exc
from os import remove
from random import choice
from html import escape
from urllib.parse import quote, unquote
from requests import request
from pyshorteners import Shortener
from pyrogram import filters
from pyrogram.errors import BadRequest, UserNotParticipant, FloodWait
from pyrogram.types import (InlineKeyboardButton, InlineKeyboardMarkup,
                            Message, CallbackQuery)
from extras.fonts import Fonts
from pyrogram.enums import ChatMembersFilter, ChatMemberStatus as CMS, ParseMode
from googletrans import Translator
from Powers.utils.http_helper import *

from Powers.bot_class import Nikki
from Powers import OWNER_ID, MESSAGE_DUMP, LOGGER, TIME_ZONE
from Powers.database.antispam_db import GBan
from Powers.database.approve_db import Approve
from Powers.database.blacklist_db import Blacklist
from Powers.database.chats_db import Chats
from Powers.database.disable_db import Disabling
from Powers.database.filters_db import Filters
from Powers.database.greetings_db import Greetings
from Powers.database.notes_db import Notes, NotesSettings
from Powers.database.pins_db import Pins
from Powers.database.rules_db import Rules
from Powers.database.users_db import Users
from Powers.database.warns_db import Warns, WarnSettings
from apscheduler.schedulers.asyncio import AsyncIOScheduler

async def clean_my_db(c: Nikki, is_cmd=False, user_id=None):
    to_clean = []
    chats_list = Chats.list_chats_by_id()
    to_clean.clear()
    start = time.time()
    
    for chat_id in chats_list:
        try:
            chat_member = await c.get_chat_member(chat_id=chat_id, user_id=Nikki.id)
            if chat_member.status not in [CMS.MEMBER, CMS.ADMINISTRATOR, CMS.OWNER]:
                to_clean.append(chat_id)
        except UserNotParticipant:
            to_clean.append(chat_id)
        except Exception as e:
            LOGGER.error(e)
            LOGGER.error(format_exc())
            if not is_cmd:
                return str(e)
            else:
                to_clean.append(chat_id)
    
    for chat_id in to_clean:
        Approve(chat_id).clean_approve()
        Blacklist(chat_id).clean_blacklist()
        Chats.remove_chat(chat_id)
        Disabling(chat_id).clean_disable()
        Filters().rm_all_filters(chat_id)
        Floods().rm_flood(chat_id)
        Greetings(chat_id).clean_greetings()
        Notes().rm_all_notes(chat_id)
        NotesSettings().clean_notes(chat_id)
        Pins(chat_id).clean_pins()
        Reporting(chat_id).clean_reporting()
        Warns(chat_id).clean_warn()
        WarnSettings(chat_id).clean_warns()
    
    x = len(to_clean)
    txt = f"#INFO\n\nCleaned db:\nTotal chats removed: {x}"
    to_clean.clear()
    nums = time.time() - start
    
    if is_cmd:
        user = await c.get_users(user_ids=user_id)
        txt += f"\nClean type: Forced\nInitiated by: {user.mention}"
        txt += f"\nClean type: Manual\n\tTook {round(nums, 2)} seconds to complete the process"
        await c.send_message(chat_id=MESSAGE_DUMP, text=txt)
        return txt
    else:
        txt += f"\nClean type: Auto\n\tTook {round(nums, 2)} seconds to complete the process"
        await c.send_message(chat_id=MESSAGE_DUMP, text=txt)
        return txt

def figle(text):
    x = pyfiglet.FigletFont.getFonts()
    font = choice(x)
    figled = str(pyfiglet.figlet_format(text,font=font))
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(text="ᴄʜᴀɴɢᴇ", callback_data="figlet"),InlineKeyboardButton(text="ᴄʟᴏsᴇ", callback_data="close_reply")]])
    return figled, keyboard

@Nikki.on_cmd("figlet")
async def echo(_, message: Message):
    global text
    try:
        text = message.text.split(' ',1)[1]
    except IndexError:
        return await message.reply_text("ᴇxᴀᴍᴘʟᴇ:\n\n`/figlet Nyc`")
    kul_text, keyboard = figle(text)
    await message.reply_text(f"ʜᴇʀᴇ ɪs ʏᴏᴜʀ ғɪɢʟᴇᴛ :\n<pre>{kul_text}</pre>", quote=True, reply_markup=keyboard)

@Nikki.on_cb("figlet")
async def figlet_handler(Nikki, query: CallbackQuery):
  try:
      kul_text, keyboard = figle(text)
      await query.message.edit_text(f"ʜᴇʀᴇ ɪs ʏᴏᴜʀ ғɪɢʟᴇᴛ :\n<pre>{kul_text}</pre>", reply_markup=keyboard)
  except Exception as e : 
      await message.reply(e)

@Nikki.on_cmd("write")
async def handwrite(_, message: Message):
    if message.reply_to_message:
        text = message.reply_to_message.text
    else:
        text_parts = message.text.split(None, 1)
        if len(text_parts) < 2:
            return await message.reply("» Pʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ sᴏᴍᴇ ᴛᴇxᴛ ᴛᴏ ᴡʀɪᴛᴇ.")
        text = text_parts[1]
    
    m = await message.reply_text("» ʟᴇᴍᴍᴇ ᴡʀɪᴛᴇ ᴛʜᴇ ᴘʀᴏᴠɪᴅᴇᴅ ᴛᴇxᴛ...")
    write = requests.get(f"https://apis.xditya.me/write?text={text}").url

    caption = f"""
sᴜᴄᴇssғᴜʟʟʏ ᴡʀɪᴛᴛᴇɴ ᴛᴇxᴛ 💘
✨ **ᴡʀɪᴛᴛᴇɴ ʙʏ :** {(await Nikki.get_me()).mention}
🥀 **ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :** {message.from_user.mention}
"""
    await m.delete()
    await message.reply_photo(photo=write, caption=caption)

@Nikki.on_cmd("gstats")
async def get_stats(_, m: Message):
    # initialise
    bldb = Blacklist
    gbandb = GBan()
    notesdb = Notes()
    rulesdb = Rules
    grtdb = Greetings
    userdb = Users
    dsbl = Disabling
    appdb = Approve
    chatdb = Chats
    fldb = Filters()
    pinsdb = Pins
    notesettings_db = NotesSettings()
    warns_db = Warns
    warns_settings_db = WarnSettings

    replymsg = await m.reply_text("<b><i>Fetching Stats...</i></b>", quote=True)
    rply = (
        f"<b>Users:</b> <code>{(userdb.count_users())}</code> in <code>{(chatdb.count_chats())}</code> chats\n"
        f"<b>Anti Channel Pin:</b> <code>{(pinsdb.count_chats('antichannelpin'))}</code> enabled chats\n"
        f"<b>Clean Linked:</b> <code>{(pinsdb.count_chats('cleanlinked'))}</code> enabled chats\n"
        f"<b>Filters:</b> <code>{(fldb.count_filters_all())}</code> in <code>{(fldb.count_filters_chats())}</code> chats\n"
        f"    <b>Aliases:</b> <code>{(fldb.count_filter_aliases())}</code>\n"
        f"<b>Blacklists:</b> <code>{(bldb.count_blacklists_all())}</code> in <code>{(bldb.count_blackists_chats())}</code> chats\n"
        f"    <b>Action Specific:</b>\n"
        f"        <b>None:</b> <code>{(bldb.count_action_bl_all('none'))}</code> chats\n"
        f"        <b>Kick</b> <code>{(bldb.count_action_bl_all('kick'))}</code> chats\n"
        f"        <b>Warn:</b> <code>{(bldb.count_action_bl_all('warn'))}</code> chats\n"
        f"        <b>Ban</b> <code>{(bldb.count_action_bl_all('ban'))}</code> chats\n"
        f"<b>Rules:</b> Set in <code>{(rulesdb.count_chats_with_rules())}</code> chats\n"
        f"    <b>Private Rules:</b> <code>{(rulesdb.count_privrules_chats())}</code> chats\n"
        f"<b>Warns:</b> <code>{(warns_db.count_warns_total())}</code> in <code>{(warns_db.count_all_chats_using_warns())}</code> chats\n"
        f"    <b>Users Warned:</b> <code>{(warns_db.count_warned_users())}</code> users\n"
        f"    <b>Action Specific:</b>\n"
        f"        <b>Kick</b>: <code>{(warns_settings_db.count_action_chats('kick'))}</code>\n"
        f"        <b>Mute</b>: <code>{(warns_settings_db.count_action_chats('mute'))}</code>\n"
        f"        <b>Ban</b>: <code>{warns_settings_db.count_action_chats('ban')}</code>\n"
        f"<b>Notes:</b> <code>{(notesdb.count_all_notes())}</code> in <code>{(notesdb.count_notes_chats())}</code> chats\n"
        f"    <b>Private Notes:</b> <code>{(notesettings_db.count_chats())}</code> chats\n"
        f"<b>GBanned Users:</b> <code>{(gbandb.count_gbans())}</code>\n"
        f"<b>Welcoming Users in:</b> <code>{(grtdb.count_chats('welcome'))}</code> chats\n"
        f"<b>Approved People</b>: <code>{(appdb.count_all_approved())}</code> in <code>{(appdb.count_approved_chats())}</code> chats\n"
        f"<b>Disabling:</b> <code>{(dsbl.count_disabled_all())}</code> items in <code>{(dsbl.count_disabling_chats())}</code> chats.\n"
        "<b>Action:</b>\n"
        f"     <b>Del:</b> Applied in <code>{(dsbl.count_action_dis_all('del'))}</code> chats.\n"
    )
    await replymsg.edit_text(rply, parse_mode=enums.ParseMode.HTML)
    return

TINY_KEY = "51FE6NQvElAr9Z7HRNH1HInvuQ60NhsZmXX6rhM26cUQ21MJPY2xH4QbMO3y"

@Nikki.on_cmd("shorturl")
async def link_handler(_, ctx: Message):
    if len(ctx.command) == 1:
        return await ctx.reply_text("ɢɪᴠᴇ ᴀɴ ᴜʀʟ ᴡɪᴛʜ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ ғᴏʀ sʜᴏʀᴛᴇɴɪɴɢ.")
    url = (
        ctx.command[1]
        if ctx.command[1].startswith("http")
        else f"https://{ctx.command[1]}"
    )
    shortened_url, Err = get_shortlink(url)
    if shortened_url is None:
        message = f"sᴏᴍᴇᴛʜɪɴɢ ᴡᴇɴᴛ ᴡʀᴏɴɢ\n\n{Err}"
        await ctx.reply_text(message, quote=True)
        return
    message = f"ʜᴇʀᴇ ɪs ʏᴏᴜʀ sʜᴏʀᴛᴇɴᴇᴅ ᴜʀʟ :\n\n<code>{shortened_url}</code>"
    markup = InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("ᴠɪsɪᴛ", url=shortened_url)
                    ]
                ]
            )
    # i don't think this bot with get sending message error so no need of exceptions
    await ctx.reply_text(text=message, reply_markup=markup, quote=True)


def get_shortlink(url):
    """Very Hard"""
    shortened_url = None
    Err = None
    try:
        if TINY_KEY:
            s = Shortener(api_key=TINY_KEY)
            shortened_url = s.tinyurl.short(url)
    except Exception as error:
        Err = f"#ERROR: {error}"
        LOGGER.info(Err)
    return shortened_url, Err

@Nikki.on_cmd("bug")
async def report_bug(c: Nikki, m: Message):
    reply_message = m.reply_to_message
    
    if not reply_message:
        await m.reply_text("Please reply to a message to report it as a bug.")
        return
    
    if not reply_message.text:
        await m.reply_text("Please reply to a text message for bug reporting.")
        return
    
    bug_report_text = f"#BUG\n{reply_message.text.html}\nReported by: {m.from_user.id} ({m.from_user.mention})"
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("Update Channel", url=f"https://t.me/NikkiAssociation")]
    ])
    
    try:
        bug_report_message = await c.send_message(MESSAGE_DUMP, bug_report_text,ParseMode.HTML)
    except Exception:
        bug_report_message = await c.send_message(MESSAGE_DUMP, reply_message.text.html,ParseMode.HTML)
        await bug_report_message.reply_text(f"#BUG\nReported by: {m.from_user.id} ({m.from_user.mention})")
    
    await reply_message.delete()
    
    caption_text = "Bug successfully reported. Thank you!"
    await m.reply_photo(photo="./extras/Fire.jpg", caption=caption_text, reply_markup=keyboard)
    
    report_link = bug_report_message.link
    await c.send_message(OWNER_ID, f"New bug report:\n{report_link}", disable_web_page_preview=True)
  

def calcExpression(text):
    try:
        return float(eval(text))
    except (SyntaxError, ZeroDivisionError):
        return ""
    except TypeError:
        return float(eval(text.replace('(', '*(')))
    except Exception as e:
        logger.error(e, exc_info=True)
        return ""


def calc_btn(uid):
    CALCULATE_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("DEL", callback_data=f"calc|{uid}|DEL"),
                InlineKeyboardButton("AC", callback_data=f"calc|{uid}|AC"),
                InlineKeyboardButton("(", callback_data=f"calc|{uid}|("),
                InlineKeyboardButton(")", callback_data=f"calc|{uid}|)")
            ],
            [
                InlineKeyboardButton("7", callback_data=f"calc|{uid}|7"),
                InlineKeyboardButton("8", callback_data=f"calc|{uid}|8"),
                InlineKeyboardButton("9", callback_data=f"calc|{uid}|9"),
                InlineKeyboardButton("÷", callback_data=f"calc|{uid}|/")
            ],
            [
                InlineKeyboardButton("4", callback_data=f"calc|{uid}|4"),
                InlineKeyboardButton("5", callback_data=f"calc|{uid}|5"),
                InlineKeyboardButton("6", callback_data=f"calc|{uid}|6"),
                InlineKeyboardButton("×", callback_data=f"calc|{uid}|*")
            ],
            [
                InlineKeyboardButton("1", callback_data=f"calc|{uid}|1"),
                InlineKeyboardButton("2", callback_data=f"calc|{uid}|2"),
                InlineKeyboardButton("3", callback_data=f"calc|{uid}|3"),
                InlineKeyboardButton("-", callback_data=f"calc|{uid}|-"),
            ],
            [
                InlineKeyboardButton(".", callback_data=f"calc|{uid}|."),
                InlineKeyboardButton("0", callback_data=f"calc|{uid}|0"),
                InlineKeyboardButton("=", callback_data=f"calc|{uid}|="),
                InlineKeyboardButton("+", callback_data=f"calc|{uid}|+"),
            ]
        ]
    )
    return CALCULATE_BUTTONS


from pyrogram import Client, filters

@Nikki.on_cmd(["calc", "calculate", "calculator"])
async def calculate_handler(self, ctx):
    if not ctx.from_user:
        return

    # Send the reply text with a button markup
    try:
        # Sending a reply with a custom button markup
        await ctx.reply_text(
            text=f"Made by @{self.me.username}",
            reply_markup=calc_btn(ctx.from_user.id),
            disable_web_page_preview=True,
            quote=True,
        )
    except Exception as e:
        print(f"Error while sending message: {e}")

@Nikki.on_callback_query(filters.regex("^calc"))
async def calc_cb(self, query):
    _, uid, data = query.data.split("|")
    if query.from_user.id != int(uid):
        return await query.answer("Who are you??", show_alert=True, cache_time=5)
    try:
        text = query.message.text.split("\n")[0].strip().split("=")[0].strip()
        text = "" if f"Made by @{self.me.username}" in text else text
        inpt = text + query.data
        result = ""
        if data == "=":
            result = calcExpression(text)
            text = ""
        elif data == "DEL":
            text = text[:-1]
        elif data == "AC":
            text = ""
        else:
            dot_dot_check = re.findall(r"(\d*\.\.|\d*\.\d+\.)", inpt)
            opcheck = re.findall(r"([*/\+-]{2,})", inpt)
            if not dot_dot_check and not opcheck:
                if strOperands := re.findall(r"(\.\d+|\d+\.\d+|\d+)", inpt):
                    text += data
                    result = calcExpression(text)

        text = f"{text:<50}"
        if result:
            if text:
                text += f"\n{result:>50}"
            else:
                text = result
        text += f"\n\nMade by @{self.me.username}"
        await query.message.edit_msg(
            text=text,
            disable_web_page_preview=True,
            reply_markup=calc_btn(query.from_user.id),
        )
    except Exception as error:
        LOGGER.error(error)

@Nikki.on_cmd(["font", "fonts"])
async def style_buttons(c, m, cb=False):
    buttons = [
        [
            InlineKeyboardButton("𝚃𝚢𝚙𝚎𝚠𝚛𝚒𝚝𝚎𝚛", callback_data="style+typewriter"),
            InlineKeyboardButton("𝕆𝕦𝕥𝕝𝕚𝕟𝕖", callback_data="style+outline"),
            InlineKeyboardButton("𝐒𝐞𝐫𝐢𝐟", callback_data="style+serif"),
        ],
        [
            InlineKeyboardButton("𝑺𝒆𝒓𝒊𝒇", callback_data="style+bold_cool"),
            InlineKeyboardButton("𝑆𝑒𝑟𝑖𝑓", callback_data="style+cool"),
            InlineKeyboardButton("Sᴍᴀʟʟ Cᴀᴘs", callback_data="style+small_cap"),
        ],
        [
            InlineKeyboardButton("𝓈𝒸𝓇𝒾𝓅𝓉", callback_data="style+script"),
            InlineKeyboardButton("𝓼𝓬𝓻𝓲𝓹𝓽", callback_data="style+script_bolt"),
            InlineKeyboardButton("ᵗⁱⁿʸ", callback_data="style+tiny"),
        ],
        [
            InlineKeyboardButton("ᑕOᗰIᑕ", callback_data="style+comic"),
            InlineKeyboardButton("𝗦𝗮𝗻𝘀", callback_data="style+sans"),
            InlineKeyboardButton("𝙎𝙖𝙣𝙨", callback_data="style+slant_sans"),
        ],
        [
            InlineKeyboardButton("𝘚𝘢𝘯𝘴", callback_data="style+slant"),
            InlineKeyboardButton("𝖲𝖺𝗇𝗌", callback_data="style+sim"),
            InlineKeyboardButton("Ⓒ︎Ⓘ︎Ⓡ︎Ⓒ︎Ⓛ︎Ⓔ︎Ⓢ︎", callback_data="style+circles"),
        ],
        [
            InlineKeyboardButton("🅒︎🅘︎🅡︎🅒︎🅛︎🅔︎🅢︎", callback_data="style+circle_dark"),
            InlineKeyboardButton("𝔊𝔬𝔱𝔥𝔦𝔠", callback_data="style+gothic"),
            InlineKeyboardButton("𝕲𝖔𝖙𝖍𝖎𝖈", callback_data="style+gothic_bolt"),
        ],
        [
            InlineKeyboardButton("C͜͡l͜͡o͜͡u͜͡d͜͡s͜͡", callback_data="style+cloud"),
            InlineKeyboardButton("H̆̈ă̈p̆̈p̆̈y̆̈", callback_data="style+happy"),
            InlineKeyboardButton("S̑̈ȃ̈d̑̈", callback_data="style+sad"),
        ],
        [InlineKeyboardButton("ɴᴇxᴛ ➻", callback_data="nxt")],
    ]
    if not cb:
        await m.reply_text(
            text=m.text.split(None, 1)[1],
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True,
        )
    else:
        await m.answer()
        await m.message.edit_reply_markup(InlineKeyboardMarkup(buttons))


@Nikki.on_cb("nxt")
async def nxt(c, m):
    if m.data == "nxt":
        buttons = [
            [
                InlineKeyboardButton("🇸 🇵 🇪 🇨 🇮 🇦 🇱 ", callback_data="style+special"),
                InlineKeyboardButton("🅂🅀🅄🄰🅁🄴🅂", callback_data="style+squares"),
                InlineKeyboardButton(
                    "🆂︎🆀︎🆄︎🅰︎🆁︎🅴︎🆂︎", callback_data="style+squares_bold"
                ),
            ],
            [
                InlineKeyboardButton("ꪖꪀᦔꪖꪶꪊᥴ𝓲ꪖ", callback_data="style+andalucia"),
                InlineKeyboardButton("爪卂几ᘜ卂", callback_data="style+manga"),
                InlineKeyboardButton("S̾t̾i̾n̾k̾y̾", callback_data="style+stinky"),
            ],
            [
                InlineKeyboardButton(
                    "B̥ͦu̥ͦb̥ͦb̥ͦl̥ͦe̥ͦs̥ͦ", callback_data="style+bubbles"
                ),
                InlineKeyboardButton(
                    "U͟n͟d͟e͟r͟l͟i͟n͟e͟", callback_data="style+underline"
                ),
                InlineKeyboardButton("꒒ꍏꀷꌩꌃꀎꁅ", callback_data="style+ladybug"),
            ],
            [
                InlineKeyboardButton("R҉a҉y҉s҉", callback_data="style+rays"),
                InlineKeyboardButton("B҈i҈r҈d҈s҈", callback_data="style+birds"),
                InlineKeyboardButton("S̸l̸a̸s̸h̸", callback_data="style+slash"),
            ],
            [
                InlineKeyboardButton("s⃠t⃠o⃠p⃠", callback_data="style+stop"),
                InlineKeyboardButton(
                    "S̺͆k̺͆y̺͆l̺͆i̺͆n̺͆e̺͆", callback_data="style+skyline"
                ),
                InlineKeyboardButton("A͎r͎r͎o͎w͎s͎", callback_data="style+arrows"),
            ],
            [
                InlineKeyboardButton("ዪሀክቿነ", callback_data="style+qvnes"),
                InlineKeyboardButton("S̶t̶r̶i̶k̶e̶", callback_data="style+strike"),
                InlineKeyboardButton("F༙r༙o༙z༙e༙n༙", callback_data="style+frozen"),
            ],
            [InlineKeyboardButton("ʙᴀᴄᴋ", callback_data="nxt+0")],
        ]
        await m.answer()
        await m.message.edit_reply_markup(InlineKeyboardMarkup(buttons))
    else:
        await style_buttons(c, m, cb=True)


@Nikki.on_cb("style")
async def style(c, m):
    await m.answer()
    cmd, style = m.data.split("+")

    if style == "typewriter":
        cls = Fonts.typewriter
    if style == "outline":
        cls = Fonts.outline
    if style == "serif":
        cls = Fonts.serief
    if style == "bold_cool":
        cls = Fonts.bold_cool
    if style == "cool":
        cls = Fonts.cool
    if style == "small_cap":
        cls = Fonts.smallcap
    if style == "script":
        cls = Fonts.script
    if style == "script_bolt":
        cls = Fonts.bold_script
    if style == "tiny":
        cls = Fonts.tiny
    if style == "comic":
        cls = Fonts.comic
    if style == "sans":
        cls = Fonts.san
    if style == "slant_sans":
        cls = Fonts.slant_san
    if style == "slant":
        cls = Fonts.slant
    if style == "sim":
        cls = Fonts.sim
    if style == "circles":
        cls = Fonts.circles
    if style == "circle_dark":
        cls = Fonts.dark_circle
    if style == "gothic":
        cls = Fonts.gothic
    if style == "gothic_bolt":
        cls = Fonts.bold_gothic
    if style == "cloud":
        cls = Fonts.cloud
    if style == "happy":
        cls = Fonts.happy
    if style == "sad":
        cls = Fonts.sad
    if style == "special":
        cls = Fonts.special
    if style == "squares":
        cls = Fonts.square
    if style == "squares_bold":
        cls = Fonts.dark_square
    if style == "andalucia":
        cls = Fonts.andalucia
    if style == "manga":
        cls = Fonts.manga
    if style == "stinky":
        cls = Fonts.stinky
    if style == "bubbles":
        cls = Fonts.bubbles
    if style == "underline":
        cls = Fonts.underline
    if style == "ladybug":
        cls = Fonts.ladybug
    if style == "rays":
        cls = Fonts.rays
    if style == "birds":
        cls = Fonts.birds
    if style == "slash":
        cls = Fonts.slash
    if style == "stop":
        cls = Fonts.stop
    if style == "skyline":
        cls = Fonts.skyline
    if style == "arrows":
        cls = Fonts.arrows
    if style == "qvnes":
        cls = Fonts.rvnes
    if style == "strike":
        cls = Fonts.strike
    if style == "frozen":
        cls = Fonts.frozen
    new_text = cls(m.message.reply_to_message.text.split(None, 1)[1])
    try:
        await m.message.edit_text(new_text, reply_markup=m.message.reply_markup)
    except:
        pass

@Nikki.on_cmd("gifid")
async def get_gifid(_, m: Message):
    if m.reply_to_message and m.reply_to_message.animation:
        await m.reply_text(
            f"ɢɪғ ɪᴅ:\n<code>{m.reply_to_message.animation.file_id}</code>",
            parse_mode=enums.ParseMode.HTML,
        )
    else:
        await m.reply_text(text="ᴘʟᴇᴀsᴇ ʀᴇᴘʟʏ ᴛᴏ ᴀ ɢɪғ ᴛᴏ ɢᴇᴛ ɪᴛ's ɪᴅ.")
    return

@Nikki.on_cmd("tr")
async def tr(_, message):
    trl = Translator()

    if message.reply_to_message and (message.reply_to_message.text or message.reply_to_message.caption):
        target_lang = "en" if len(message.text.split()) == 1 else message.text.split()[1]
        text = message.reply_to_message.text if message.reply_to_message.text else message.reply_to_message.caption
    else:
        if len(message.text.split()) <= 2:
            await message.reply_text(
                "Provide a language code\n[Available options](https://telegra.ph/Lang-Codes-09-19).\nUsage: /tr en",
            )
            return
        target_lang, text = message.text.split(None, 2)[1], message.text.split(None, 2)[2]

    try:
        detectlang = await trl.detect(text)
        translated = await trl.translate(text, dest=target_lang)
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")
        return

    await message.reply_text(
        f"<b>Translated:</b> from {detectlang.lang} to {target_lang}\n<code>{translated.text}</code>",
    )

pattern = re.compile(r"^text/|json$|yaml$|xml$|toml$|x-sh$|x-shellscript$")
BASE = "https://pasty.lus.pm/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.104 Safari/537.36",
    "content-type": "application/json",
}

def paste(content: str):
    data = {"content": content}
    resp = resp_post(f"{BASE}api/v1/pastes", data=json.dumps(data), headers=headers)
    if not resp.ok:
        return
    resp = resp.json()
    return BASE + resp['id']


@Nikki.on_cmd("paste")
async def paste_func(_, message: Message):
    r = message.reply_to_message
    m = await message.reply_text("Pasting...")

    if not r:
        await m.edit("Please Reply to text or give some content after paste command or reply to a document to paste their content.")
        return
    if r:
        if not r.text and not r.document:
            return await m.edit("Only text and documents are supported")

        if r.text:
            content = r.text
            exe = "txt"
        if r.document:
            if r.document.file_size > 40000:
                return await m.edit("You can only paste files smaller than 40KB.")

            if not pattern.search(r.document.mime_type):
                return await m.edit("Only text files can be pasted.")

            doc = await message.reply_to_message.download()
            exe = doc.rsplit(".",1)[-1]
            async with aiofiles.open(doc, mode="r") as f:
                fdata = await f.read()
                content = fdata

            remove(doc)
    try:
        link = paste(content)
    except Exception as e:
        await m.edit_text(e)
        return
    if not link:
        await m.edit_text("Failed to post!")
        return
    kb = [[InlineKeyboardButton(text="View", url=link + f".{exe}")]]
    try:
        await m.edit_text("Pasted to Pasty!", reply_markup=InlineKeyboardMarkup(kb))
    except Exception as e:
        if link:
            return await m.edit_text(f"Pasted to Pasty!\n [link]({link + f'.{exe}'})",)
        return await m.edit_text(f"Failed to post. Due to following error:\n{e}")

@Nikki.on_cmd(["dice", "dados"])
async def dice(c: Nikki, m: Message):
    dicen = await c.send_dice(m.chat.id, reply_to_message_id=m.id)
    await dicen.reply_text(
        f"Result: {dicen.dice.value}", quote=True
    )

@Nikki.on_cmd("cat")
async def cat(c: Nikki, m: Message):
    r = requests.get("https://api.thecatapi.com/v1/images/search")
    rj = r.json()

    if rj[0]["url"].endswith(".gif"):
        await m.reply_animation(rj[0]["url"], caption="Meow")
    else:
        await m.reply_photo(rj[0]["url"], caption="Meow")

@Nikki.on_cmd("token")
async def getbotinfo(c: Nikki, m: Message):
    if len(m.command) == 1:
        return await m.reply_text("Please provide a bot token.", reply_to_message_id=m.id)
    
    text = m.text.split(maxsplit=1)[1]
    req = requests.get(f"https://api.telegram.org/bot{text}/getme")
    fullres = req.json()
    
    if not fullres["ok"]:
        await m.reply_text("Invalid bot token.")
    else:
        res = fullres["result"]
        bot_info_text = (
            f"Bot Name: {res['first_name']}\n"
            f"Bot Username: @{res['username']}\n"
            f"Bot ID: {res['id']}"
        )
    await m.reply_text(bot_info_text, reply_to_message_id=m.id)

@Nikki.on_cmd("dog")
async def dog(c: Nikki, m: Message):
    response = requests.get("https://random.dog/woof.json")
    data = response.json()

    await m.reply_photo(data["url"], caption="🐶 Woof!")

def cleanhtml(raw_html):
    cleanr = re.compile("<.*?>")
    return re.sub(cleanr, "", raw_html)

def escape_definition(definition):
    for key, value in definition.items():
        if isinstance(value, str):
            definition[key] = html.escape(cleanhtml(value))
    return definition

@Nikki.on_cmd("pypi")
async def pypi_command(c: Nikki, m: Message):
    if len(m.command) == 1:
        return await m.reply("ᴜsᴀɢᴇ: /pypi ᴘᴀᴄᴋᴀɢᴇ_ɴᴀᴍᴇ.")

    package_name = m.text.split(maxsplit=1)[1]
    r = requests.get(f"https://pypi.org/pypi/{package_name}/json")
    if r.status_code != 200:
        return await m.reply(f"Package '{package_name}' not found.")

    json = r.json()
    pypi_info = escape_definition(json["info"])

    message = (
        f"**ᴘᴀᴄᴋᴀɢᴇ ɴᴀᴍᴇ**: **{pypi_info['name']}**\n"
        f"**ᴀᴜᴛʜᴏʀ**: {pypi_info['author']}\n"
        f"**ᴀᴜᴛʜᴏʀ ᴇᴍᴀɪʟ**: {pypi_info['author_email']}\n"
        f"**ᴘʟᴀᴛғᴏʀᴍ**: {pypi_info['platform']}\n"
        f"**ᴠᴇʀsɪᴏɴ**: `{pypi_info['version']}`\n"
        f"**sᴜᴍᴍᴀʀʏ**: {pypi_info['summary']}"
    )

    if pypi_info["home_page"] and pypi_info["home_page"] != "UNKNOWN":
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="ᴘᴀᴄᴋᴀɢᴇ ʜᴏᴍᴇ ᴘᴀɢᴇ",
                        url=pypi_info["home_page"],
                    )
                ]
            ]
        )
    else:
        kb = None
    await m.reply_text(
        text=message,
        disable_web_page_preview=True,
        reply_markup=kb,
        quote=True,
    )

__PLUGIN__ = "Uᴛɪʟs"
__alt_name__ = [
    "cat",
    "dog",
    "dice",
    "fonts",
    "write",
    "shorturl",
    "math",
    "figlet",
    "gifid",
    "token",
    "pypi",
    "tr",
    "paste",
    "stat",
]

__HELP__ = """
**Dᴇsᴄʀɪᴘᴛɪᴏɴ :**
ʜᴇʀᴇ sᴏᴍᴇ ᴇxᴛʀᴀ ᴄᴏᴍᴍᴀɴᴅ ғᴏʀ ᴛʜɪs ʙᴏᴛ
────────────────────────

**Usᴇʀ Cᴏᴍᴍᴀɴᴅs :**
/cat : sᴇɴᴅs ᴀ ʀᴀɴᴅᴏᴍ ᴄᴀᴛ ᴘʜᴏᴛᴏ.
/dog : sᴇɴᴅs ᴀ ʀᴀɴᴅᴏᴍ ᴅᴏɢ ᴘʜᴏᴛᴏ.
/dice : sᴇɴᴅs ᴀ ᴅɪᴄᴇ ᴀɴᴅ ɪᴛs ɴᴜᴍʙᴇʀ.
/fonts : ᴄᴏɴᴠᴇʀᴛs sɪᴍᴩʟᴇ ᴛᴇxᴛ ᴛᴏ ʙᴇᴀᴜᴛɪғᴜʟ ᴛᴇxᴛ ʙʏ ᴄʜᴀɴɢɪɴɢ ɪᴛ's ғᴏɴᴛ.
/write : ᴡʀɪᴛᴇs ᴛʜᴇ ɢɪᴠᴇɴ ᴛᴇxᴛ.
/shorturl : sʜᴏʀᴛᴇɴs ᴛʜᴇ ɢɪᴠᴇɴ ᴜʀʟ.
/calc : sɪᴍᴘʟᴇ ᴍᴀᴛʜ ᴄᴀʟᴄᴜʟᴀᴛᴏʀ ᴜsɪɴɢ ɪɴʟɪɴᴇ ʙᴜᴛᴛᴏɴs.
/figlet : ᴍᴀᴋᴇs ғɪɢʟᴇᴛ ᴏғ ᴛʜᴇ ɢɪᴠᴇɴ ᴛᴇxᴛ.
/gifid : ʀᴇᴘʟʏ ᴛᴏ ᴀ ɢɪғ ᴛᴏ ᴍᴇ ᴛᴏ ᴛᴇʟʟ ʏᴏᴜ ɪᴛs ғɪʟᴇ ɪᴅ.
/token : ɢᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ғʀᴏᴍ ᴛʜᴇ ᴘʀᴏᴠɪᴅᴇᴅ ʙᴏᴛ ᴛᴏᴋᴇɴ.
/pypi : sᴇᴀʀᴄʜᴇs ғᴏʀ ᴀ ᴘᴀᴄᴋᴀɢᴇ ɪɴ ᴛʜᴇ ᴘʏᴛʜᴏɴ ᴘᴀᴄᴋᴀɢᴇ Iɴᴅᴇx (PʏPI).
/tr : ᴛʀᴀɴsʟᴀᴛᴇs ᴛʜᴇ ᴛᴇxᴛ ɪɴᴛᴏ ᴛʜᴇ ɢɪᴠᴇɴ ʟᴀɴɢᴜᴀɢᴇ (ᴅᴇғᴀᴜʟᴛs ᴛᴏ ᴛʜᴇ ᴄʜᴀᴛ's ᴅᴇғᴀᴜʟᴛ ʟᴀɴɢᴜᴀɢᴇ).
/paste : ᴘᴀsᴛᴇ ᴛʜᴇ ʀᴇᴘʟɪᴇᴅ ᴛᴇxᴛ/ᴅᴏᴄᴜᴍᴇɴᴛ.
/stat : ɢᴇᴛ ᴛᴏᴛᴀʟ ᴍᴇssᴀɢᴇ ᴄᴏᴜɴᴛ ᴏғ ᴀ ᴄʜᴀᴛ."""
