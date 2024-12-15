import asyncio
import os
import shutil
import socket
import aiohttp
from datetime import datetime
from io import BytesIO
from time import gmtime, time
from traceback import format_exc
from base64 import b64decode
from inspect import getfullargspec
from pyrogram.filters import command
from pyrogram.types import Message
from pyrogram.errors import (
    ChannelInvalid,
    ChannelPrivate,
    ChatAdminRequired,
    EntityBoundsInvalid,
    FloodWait,
    MessageTooLong,
    PeerIdInvalid,
    RPCError,
)
from pyrogram.enums import ChatMembersFilter
from Config import Config
from extras.formatters import alpha_to_int
from Powers.bot_class import Nikki
from Powers.database import get_served_chats, get_served_users
from Powers.database import MongoDB
from Powers.database.chats_db import Chats
from Powers import LOGGER, MESSAGE_DUMP, UPTIME
from Powers.plugins.utils import clean_my_db
from Powers.misc import SUDOERS
from Powers.utils.pastebin import AnonyBin
from Powers.utils.clean_file import remove_markdown_and_html
from Powers.utils.parser import mention_markdown
import speedtest

async def take_screenshot(url: str, full: bool = False):
    url = "https://" + url if not url.startswith("http") else url
    payload = {
        "url": url,
        "width": 1920,
        "height": 1080,
        "scale": 1,
        "format": "jpeg",
    }
    if full:
        payload["full"] = True

    async with aiohttp.ClientSession() as session:
        async with session.post("https://webscreenshot.vercel.app/api", data=payload) as response:
            data = await response.json()

    if "image" not in data:
        return None
    
    b = data["image"].replace("data:image/jpeg;base64,", "")
    file = BytesIO(b64decode(b))
    file.name = "webss.jpg"
    return file

async def eor(msg: Message, **kwargs):
    func = (
        (msg.edit_text if msg.from_user.is_self else msg.reply)
        if msg.from_user
        else msg.reply
    )
    spec = getfullargspec(func.__wrapped__).args
    return await func(**{k: v for k, v in kwargs.items() if k in spec})

@Nikki.on_cmd("webss")
async def take_ss(_, message: Message):
    if len(message.command) < 2:
        return await eor(message, text="ɢɪᴠᴇ ᴀ ᴜʀʟ ᴛᴏ ғᴇᴛᴄʜ sᴄʀᴇᴇɴsʜᴏᴛ.")

    if len(message.command) == 2:
        url = message.text.split(None, 1)[1]
        full = False
    elif len(message.command) == 3:
        url = message.text.split(None, 2)[1]
        full = message.text.split(None, 2)[2].lower().strip() in ["yes", "y", "1", "true"]
    else:
        return await eor(message, text="ɪɴᴠᴀʟɪᴅ ᴄᴏᴍᴍᴀɴᴅ.")

    m = await eor(message, text="ᴄᴀᴘᴛᴜʀɪɴɢ sᴄʀᴇᴇɴsʜᴏᴛ...")

    try:
        photo = await take_screenshot(url, full)
        if not photo:
            return await m.edit("ғᴀɪʟᴇᴅ ᴛᴏ ᴛᴇᴋᴇ sᴄʀᴇᴇɴsʜᴏᴛ.")
        
        m = await m.edit("ᴜᴘʟᴏᴀᴅɪɴɢ...")
        await message.reply_document(photo)
        await m.delete()
    except Exception as e:
        await m.edit(f"Error: {str(e)}")
# try
IS_BROADCASTING = False

@Nikki.on_message(command("broadcast") & SUDOERS)
async def braodcast_message(Nikki, message):
    global IS_BROADCASTING
    if message.reply_to_message:
        x = message.reply_to_message.id
        y = message.chat.id
    else:
        if len(message.command) < 2:
            return await message.reply_text("**ᴇxᴀᴍᴘʟᴇ :**\n\n/broadcast [ᴍᴇssᴀɢᴇ ᴏʀ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ]")
        query = message.text.split(None, 1)[1]
        if "-pin" in query:
            query = query.replace("-pin", "")
        if "-nobot" in query:
            query = query.replace("-nobot", "")
        if "-pinloud" in query:
            query = query.replace("-pinloud", "")
        if "-user" in query:
            query = query.replace("-user", "")
        if query == "":
            return await message.reply_text("» ᴘʟᴇᴀsᴇ ᴘʀᴏᴠɪᴅᴇ sᴏᴍᴇ ᴛᴇxᴛ ᴛᴏ ʙʀᴏᴀᴅᴄᴀsᴛ.")

    IS_BROADCASTING = True
    await message.reply_text("» sᴛᴀʀᴛᴇᴅ ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ...")

    if "-nobot" not in message.text:
        sent = 0
        pin = 0
        chats = []
        schats = await get_served_chats()
        for chat in schats:
            chats.append(int(chat["chat_id"]))
        for i in chats:
            try:
                m = (
                    await Nikki.forward_messages(i, y, x)
                    if message.reply_to_message
                    else await Nikki.send_message(i, text=query)
                )
                if "-pin" in message.text:
                    try:
                        await m.pin(disable_notification=True)
                        pin += 1
                    except:
                        continue
                elif "-pinloud" in message.text:
                    try:
                        await m.pin(disable_notification=False)
                        pin += 1
                    except:
                        continue
                sent += 1
                await asyncio.sleep(0.2)
            except FloodWait as fw:
                flood_time = int(fw.value)
                if flood_time > 200:
                    continue
                await asyncio.sleep(flood_time)
            except:
                continue
        try:
            await message.reply_text("» ʙʀᴏᴀᴅᴄᴀsᴛᴇᴅ ᴍᴇssᴀɢᴇ ᴛᴏ {0} ᴄʜᴀᴛs ᴡɪᴛʜ {1} ᴘɪɴs ғʀᴏᴍ ᴛʜᴇ ʙᴏᴛ.".format(sent, pin))
        except:
            pass

    if "-user" in message.text:
        susr = 0
        served_users = []
        susers = await get_served_users()
        for user in susers:
            served_users.append(int(user["user_id"]))
        for i in served_users:
            try:
                m = (
                    await Nikki.forward_messages(i, y, x)
                    if message.reply_to_message
                    else await Nikki.send_message(i, text=query)
                )
                susr += 1
                await asyncio.sleep(0.2)
            except FloodWait as fw:
                flood_time = int(fw.value)
                if flood_time > 200:
                    continue
                await asyncio.sleep(flood_time)
            except:
                pass
        try:
            await message.reply_text("» ʙʀᴏᴀᴅᴄᴀsᴛᴇᴅ ᴍᴇssᴀɢᴇ ᴛᴏ {0} ᴜsᴇʀs.".format(susr))
        except:
            pass

@Nikki.on_message(command("stats") & SUDOERS)
async def get_stats(_, message):
    users = len(await get_served_users())
    chats = len(await get_served_chats())
    await message.reply_text(f"Current stats of {Nikki.name}:\n\n{users} users\n{chats} chats")

@Nikki.on_message(command("ping") & SUDOERS)
async def ping(_, m: Message):
    LOGGER.info(f"{m.from_user.id} used ping cmd in {m.chat.id}")
    start = time()
    replymsg = await m.reply_text(text="Pinging...", quote=True)
    delta_ping = time() - start
    await replymsg.edit_text(f"<b>Pong!</b>\n{delta_ping * 1000:.3f} ms")
    return

@Nikki.on_message(command("chatlist") & SUDOERS)
async def chats(c: Nikki, m: Message):
    exmsg = await m.reply_text(text="Exporting Charlist...")
    all_chats = (Chats.list_chats_full()) or {}
    chatfile = """List of chats in my database.

        <b>Chat name | Chat ID | Members count</b>"""
    P = 1
    for chat in all_chats:
        try:
            if chat["_id"] < 0:
                # Skip negative chat IDs (invalid or deleted chats)
                continue

            chat_info = await c.get_chat(chat["_id"])
            chat_members = chat_info.members_count
            try:
                invitelink = chat_info.invite_link
            except KeyError:
                invitelink = "No Link!"
            chatfile += f"{P}. {chat['chat_name']} | {chat['_id']} | {chat_members} | {invitelink}\n"
            P += 1
        except ChatAdminRequired:
            pass
        except (ChannelPrivate, ChannelInvalid):
            Chats.remove_chat(chat["_id"])
        except PeerIdInvalid:
            LOGGER.warning(f"Peer not found {chat['_id']}")
        except FloodWait as ef:
            LOGGER.error("FloodWait required, Sleeping for 60s")
            LOGGER.error(ef)
            sleep(60)
        except RPCError as ef:
            LOGGER.error(ef)
            await m.reply_text(f"**Error:**\n{ef}")

    with BytesIO(str.encode(await remove_markdown_and_html(chatfile))) as f:
        f.name = "chatlist.txt"
        await m.reply_document(
            document=f,
            caption="Here is the list of chats in my Database.",
        )
    await exmsg.delete()
    return


@Nikki.on_message(command("uptime") & SUDOERS)
async def uptime(_, m: Message):
    up = strftime("%Hh %Mm %Ss", gmtime(time() - UPTIME))
    await m.reply_text(text=f"<b>Uptime:</b> <code>{up}</code>", quote=True)
    return

def testspeed(m):
    try:
        test = speedtest.Speedtest()
        test.get_best_server()
        m = m.edit("**⇆ ʀᴜɴɴɪɴɢ ᴅᴏᴡɴʟᴏᴀᴅ sᴩᴇᴇᴅᴛᴇsᴛ...**")
        test.download()
        m = m.edit("**⇆ ʀᴜɴɴɪɴɢ ᴜᴩʟᴏᴀᴅ sᴩᴇᴇᴅᴛᴇsᴛ...**")
        test.upload()
        test.results.share()
        result = test.results.dict()
        m = m.edit("**↻ sʜᴀʀɪɴɢ sᴩᴇᴇᴅᴛᴇsᴛ ʀᴇsᴜʟᴛs...**")
    except Exception as e:
        return m.edit(e)
    return result


@Nikki.on_message(command("spt") & SUDOERS)
async def speedtest_function(Nikki, message):
    m = await message.reply_text("💫 ᴛʀʏɪɴɢ ᴛᴏ ᴄʜᴇᴄᴋ ᴜᴩʟᴏᴀᴅ ᴀɴᴅ ᴅᴏᴡɴʟᴏᴀᴅ sᴩᴇᴇᴅ...")
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, testspeed, m)
    output = f"""✯ **sᴩᴇᴇᴅᴛᴇsᴛ ʀᴇsᴜʟᴛs** ✯
    
<u>**❥͜͡ᴄʟɪᴇɴᴛ :**</u>
**» __ɪsᴩ :__** {result['client']['isp']}
**» __ᴄᴏᴜɴᴛʀʏ :__** {result['client']['country']}
  
<u>**❥͜͡sᴇʀᴠᴇʀ :**</u>
**» __ɴᴀᴍᴇ :__** {result['server']['name']}
**» __ᴄᴏᴜɴᴛʀʏ :__** {result['server']['country']}, {result['server']['cc']}
**» __sᴩᴏɴsᴏʀ :__** {result['server']['sponsor']}
**» __ʟᴀᴛᴇɴᴄʏ :__** {result['server']['latency']}  
**» __ᴩɪɴɢ :__** {result['ping']}"""
    msg = await Nikki.send_photo(
        chat_id=message.chat.id, 
        photo=result["share"], 
        caption=output
    )
    await m.delete()

@Nikki.on_message(command("leavechat") & SUDOERS)
async def leave_chat(c: Nikki, m: Message):
    if len(m.text.split()) != 2:
        await m.reply_text("Supply a chat id which I should leave!", quoet=True)
        return
    chat_id = m.text.split(None, 1)[1]
    replymsg = await m.reply_text(f"Trying to leave chat {chat_id}...", quote=True)
    try:
        await c.leave_chat(chat_id)
        await replymsg.edit_text(f"Left <code>{chat_id}</code>.")
    except PeerIdInvalid:
        await replymsg.edit_text("Haven't seen this group in this session!")
    except RPCError as ef:
        LOGGER.error(ef)
        await replymsg.edit_text(f"Failed to leave chat!\nError: <code>{ef}</code>.")
    return
  
@Nikki.on_message(command("cleandb") & SUDOERS)
async def cleeeen(c: Nikki,m:Message):
    x = await m.reply_text("Cleaning the database...")
    try:
        z = await clean_my_db(c,True,m.from_user.id)
        try:
            await x.delete()
        except Exception:
            pass
        await m.reply_text(z)
        return
    except Exception as e:
        await m.reply_text(e)
        await x.delete()
        LOGGER.error(e)
        LOGGER.error(format_exc())
        return

@Nikki.on_message(command("restart") & SUDOERS)
async def restart_(_, message):
    response = await message.reply_text("ʀᴇsᴛᴀʀᴛɪɴɢ...")
    try:
        shutil.rmtree("downloads")
        shutil.rmtree("raw_files")
        shutil.rmtree("cache")
    except:
        pass
    await response.edit_text(
        "» ʀᴇsᴛᴀʀᴛ ᴘʀᴏᴄᴇss sᴛᴀʀᴛᴇᴅ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ ғᴏʀ ғᴇᴡ sᴇᴄᴏɴᴅs ᴜɴᴛɪʟ ᴛʜᴇ ʙᴏᴛ sᴛᴀʀᴛs..."
    )
    os.system(f"kill -9 {os.getpid()} && bash start")
