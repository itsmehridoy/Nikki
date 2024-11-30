import os
from asyncio import sleep
from datetime import datetime
from traceback import format_exc

from pyrogram import enums
from pyrogram.errors import EntityBoundsInvalid, MediaCaptionTooLong, RPCError
from pyrogram.raw.functions.channels import GetFullChannel
from pyrogram.raw.functions.users import GetFullUser
from pyrogram.types import Message

from Powers import (DEV_USERS, LOGGER, OWNER_ID, SUDO_USERS,
                    WHITELIST_USERS)
from Powers.bot_class import Nikki
from Powers.database.antispam_db import GBan
from Powers.database.users_db import Users
from Powers.utils.custom_filters import command
from Powers.utils.extract_user import extract_user
from Config import Config

gban_db = GBan()


async def count(c: Nikki, chat):
    try:
        administrator = []
        async for admin in c.get_chat_members(
            chat_id=chat, filter=enums.ChatMembersFilter.ADMINISTRATORS
        ):
            administrator.append(admin)
        total_admin = administrator
        bot = []
        async for tbot in c.get_chat_members(
            chat_id=chat, filter=enums.ChatMembersFilter.BOTS
        ):
            bot.append(tbot)

        total_bot = bot
        bot_admin = 0
        ban = []
        async for banned in c.get_chat_members(
            chat, filter=enums.ChatMembersFilter.BANNED
        ):
            ban.append(banned)

        total_banned = ban
        for x in total_admin:
            for y in total_bot:
                if x == y:
                    bot_admin += 1
        total_admin = len(total_admin)
        total_bot = len(total_bot)
        total_banned = len(total_banned)
        return total_bot, total_admin, bot_admin, total_banned
    except Exception as e:
        total_bot = total_admin = bot_admin = total_banned = "`Can't fetch because I am not part of the chat.`"

    return total_bot, total_admin, bot_admin, total_banned


async def user_info(c: Nikki, user, already=False):
    if not already:
        user = await c.get_users(user_ids=user)
    if not user.first_name:
        return ["Deleted account", None]

    gbanned, reason_gban = gban_db.get_gban(user.id)
    if gbanned:
        gban = True
        reason = reason_gban
    else:
        gban = False
        reason = "User is not gbanned"

    user_id = user.id
    userrr = await c.resolve_peer(user_id)
    about = "NA"
    try:
        ll = await c.invoke(
            GetFullUser(
                id=userrr
            )
        )
        about = ll.full_user.about
    except Exception:
        pass
    username = user.username
    first_name = user.first_name
    last_name = user.last_name
    mention = user.mention(f"{first_name}")
    dc_id = user.dc_id
    is_verified = user.is_verified
    is_restricted = user.is_restricted
    photo_id = user.photo.big_file_id if user.photo else None
    is_support = True if user_id == DEV_USERS else False
    if user_id == Nikki.id:
        is_support = "A person is a great support to himself"
    omp = "Hmmm.......Who is that again?"
    if is_support or Nikki.id:
        if user_id == DEV_USERS:
            omp = "Dev"
        elif user_id == SUDO_USERS:
            omp = "Sudoer"
        elif user_id == WHITELIST_USERS:
            omp = "Whitelist"
        elif user_id == Nikki.id:
            omp = "I am the targeted user"
        elif user_id == OWNER_ID:
            omp = "Owner of the bot"
        if user_id == DEV_USERS and user_id == OWNER_ID:
            omp = "Dev and Owner"
        
    is_scam = user.is_scam
    is_bot = user.is_bot
    is_fake = user.is_fake
    status = user.status
    last_date = "Unable to fetch"
    if is_bot is True:
      last_date = "Targeted user is a bot"
    if status == enums.UserStatus.RECENTLY:
      last_date = "User was seen recently"
    if status == enums.UserStatus.LAST_WEEK:
      last_date = "User was seen last week"
    if status == enums.UserStatus.LAST_MONTH:
      last_date = "User was seen last month"
    if status == enums.UserStatus.LONG_AGO:
      last_date = "User was seen long ago or may be I am blocked by the user  :("
    if status == enums.UserStatus.ONLINE:
      last_date = "User is online"
    if status == enums.UserStatus.OFFLINE: 
      try:
        last_date = datetime.fromtimestamp(user.status.date).strftime("%Y-%m-%d %H:%M:%S")
      except Exception:
        last_date = "User is offline"

    caption = f"""
<b><i><u>⚡️ Extracted User info From Telegram ⚡️</b></i></u>

<b>🆔 User ID</b>: <code>{user_id}</code>
<b>📎 Link To Profile</b>: <a href='tg://user?id={user_id}'>Click Here🚪</a>
<b>🫵 Mention</b>: {mention}
<b>🗣 First Name</b>: <code>{first_name}</code>
<b>🔅 Second Name</b>: <code>{last_name}</code>
<b>🔍 Username</b>: {("@" + username) if username else "NA"}
<b>✍️ Bio</b>: `{about}`
<b>🧑‍💻 Support</b>: {is_support}
<b>🥷 Support user type</b>: <code>{omp}</code>
<b>💣 Gbanned</b>: {gban}
<b>☠️ Gban reason</b>: <code>{reason}</code>
<b>🌐 DC ID</b>: {dc_id}
<b>✋ RESTRICTED</b>: {is_restricted}
<b>✅ VERIFIED</b>: {is_verified}
<b>❌ FAKE</b> : {is_fake}
<b>⚠️ SCAM</b> : {is_scam} 
<b>🤖 BOT</b>: {is_bot}
<b>👀 Last seen</b>: <code>{last_date}</code>

"""

    return caption, photo_id


async def chat_info(c: Nikki, chat, already=False):
    u_name = False
    if not already:
        try:
            chat = await c.get_chat(chat)
            try:
                chat_r = (await c.resolve_peer(chat.id))
                ll = await c.invoke(
                    GetFullChannel(
                        channel=chat_r
                    )
                )    
                u_name = ll.chats[0].usernames
            except Exception:
                pass 
        except Exception:
            try:
                chat_r = await c.resolve_peer(chat)
                chat = await c.get_chat(chat_r.channel_id)
                try:
                    ll = await c.invoke(
                        GetFullChannel(
                            channel=chat_r
                        )
                    )    
                    u_name = ll.chats[0].usernames
                except Exception:
                    pass
            except KeyError as e:
                caption = f"Failed to find the chat due to\n{e}"
                return caption, None
    chat_id = chat.id
    if u_name:
        username = " ".join([f"@{i}"for i in u_name])
    elif not u_name:
        username = chat.username
    total_bot, total_admin, total_bot_admin, total_banned = await count(c, chat.id)
    title = chat.title
    type_ = str(chat.type).split(".")[1]
    is_scam = chat.is_scam
    is_fake = chat.is_fake
    description = chat.description
    members = chat.members_count
    is_restricted = chat.is_restricted
    dc_id = chat.dc_id
    photo_id = chat.photo.big_file_id if chat.photo else None
    can_save = chat.has_protected_content
    linked_chat = chat.linked_chat

    caption = f"""
🔰 <b>CHAT INFO</b> 🔰

<b>🆔 ID</b>: <code>{chat_id}</code>
<b>🚀 Chat Title</b>: {title}
<b>✨ Chat Type</b>: {type_}
<b>🌐 DataCentre ID</b>: {dc_id}
<b>🔍 Username</b>: {("@" + username) if username else "NA"}
<b>⚜️ Administrators</b>: {total_admin}
<b>🤖 Bots</b>: {total_bot}
<b>🚫 Banned</b>: {total_banned}
<b>⚜️ Admin 🤖 Bots</b>: {total_bot_admin}
<b>⁉️ Scam</b>: {is_scam}
<b>❌ Fake</b>: {is_fake}
<b>✋ Restricted</b>: {is_restricted}
<b>👨🏿‍💻 Description</b>: <code>{description}</code>
<b>👪 Total members</b>: {members}
<b>🚫 Has Protected Content</b>: {can_save}
<b>🔗 Linked Chat</b>: <code>{linked_chat.id if linked_chat else "Not Linked"}</code>

"""

    return caption, photo_id


@Nikki.on_message(command(["info", "whois"]))
async def info_func(c: Nikki, message: Message):
    if message.reply_to_message and message.reply_to_message.sender_chat:
        await message.reply_text("This is not a user, but rather a channel. Use `/chinfo` to fetch its information.")
        return
    user, _, user_name = await extract_user(c, message)

    if not user:
        await message.reply_text("Can't find user to fetch info!")

    m = await message.reply_text(
        f"Fetching {('@' + user_name) if user_name else 'user'} info from telegram's database..."
    )

    try:
        info_caption, photo_id = await user_info(c, user)

    except Exception as e:
        LOGGER.error(e)
        LOGGER.error(format_exc())
        return await m.edit(str(e))

    if not photo_id:
        await m.delete()
        await sleep(2)
        return await message.reply_text(info_caption, disable_web_page_preview=True)
    photo = await c.download_media(photo_id)

    await m.delete()
    await sleep(2)
    try:
        await message.reply_photo(photo, caption=info_caption, quote=False)
    except MediaCaptionTooLong:
        x = await message.reply_photo(photo)
        try:
            await x.reply_text(info_caption)
        except EntityBoundsInvalid:
            await x.delete()
            await message.reply_text(info_caption)
        except RPCError as rpc:
            await message.reply_text(rpc)
            LOGGER.error(rpc)
            LOGGER.error(format_exc())
    except Exception as e:
        await message.reply_text(text=e)
        LOGGER.error(e)
        LOGGER.error(format_exc())

    os.remove(photo)

    return


@Nikki.on_message(command(["chinfo", "chatinfo", "chat_info"]))
async def chat_info_func(c: Nikki, message: Message):
    splited = message.text.split()
    if len(splited) == 1:
        if message.reply_to_message and message.reply_to_message.sender_chat:
            chat = message.reply_to_message.sender_chat.id
        else:  
            chat = message.chat.id

    else:
        chat = splited[1]

    try:
        chat = int(chat)
    except (ValueError, Exception) as ef:
        if "invalid literal for int() with base 10:" in str(ef):
            chat = str(chat)
            if chat.startswith("https://"):
                chat = '@'+chat.split("/")[-1]
        else:
            return await message.reply_text(
                f"Got and exception {ef}\n**Usage:**/chinfo [USERNAME|ID]"
            )

    m = await message.reply_text(
        f"Fetching chat info of chat from telegram's database....."
    )
    
    try:
        info_caption, photo_id = await chat_info(c, chat=chat)
        if info_caption.startswith("Failed to find the chat due"):
            await message.reply_text(info_caption)
            return
    except Exception as e:
        await m.delete()
        await sleep(0.5)
        return await message.reply_text(f"**GOT AN ERROR:**\n {e}")
    if not photo_id:
        await m.delete()
        await sleep(2)
        return await message.reply_text(info_caption, disable_web_page_preview=True)

    photo = await c.download_media(photo_id)
    await m.delete()
    await sleep(2)
    try:
        await message.reply_photo(photo, caption=info_caption, quote=False)
    except MediaCaptionTooLong:
        x = await message.reply_photo(photo)
        try:
            await x.reply_text(info_caption)
        except EntityBoundsInvalid:
            await x.delete()
            await message.reply_text(info_caption)
        except RPCError as rpc:
            await message.reply_text(rpc)
            LOGGER.error(rpc)
            LOGGER.error(format_exc())
    except Exception as e:
        await message.reply_text(text=e)
        LOGGER.error(e)
        LOGGER.error(format_exc())

    os.remove(photo)

    return

#for id
@Nikki.on_cmd("id")
async def id_info(c: Nikki, m: Message):

    ChatType = enums.ChatType
    user_id, _, _ = await extract_user(c, m)
    try:
        if user_id and len(m.text.split()) == 2:
            txt = f"Given user's id: <code>{user_id}</code>"
            await m.reply_text(txt, parse_mode=enums.ParseMode.HTML)
            return
        elif m.chat.type in [ChatType.SUPERGROUP, ChatType.GROUP] and not m.reply_to_message:
            await m.reply_text(text=f"This Group's ID is <code>{m.chat.id}</code>\nYour ID <code>{m.from_user.id}</code>")
            return

        elif m.chat.type == ChatType.PRIVATE and not m.reply_to_message:
            await m.reply_text(text=f"Your ID is <code>{m.chat.id}</code>.")
            return
    except Exception as e:
        await m.reply_text(e)
        return
    if user_id:
        if m.reply_to_message and m.reply_to_message.forward_from:
            user1 = m.reply_to_message.from_user
            user2 = m.reply_to_message.forward_from
            orig_sender = await mention_html(user2.first_name, user2.id)
            orig_id = f"<code>{user2.id}</code>"
            fwd_sender = await mention_html(user1.first_name, user1.id)
            fwd_id = f"<code>{user1.id}</code>"
            await m.reply_text(
                text=f"""Original Sender - {orig_sender} (<code>{orig_id}</code>)
Forwarder - {fwd_sender} (<code>{fwd_id}</code>)""",
                parse_mode=enums.ParseMode.HTML,
            )
        else:
            try:
                user = await c.get_users(user_id)
            except PeerIdInvalid:
                await m.reply_text(
                    text="""Failed to get user
      Peer ID invalid, I haven't seen this user anywhere earlier, maybe username would help to know them!"""
                )
                return

            await m.reply_text(
                f"{(await mention_html(user.first_name, user.id))}'s ID is <code>{user.id}</code>.",
                parse_mode=enums.ParseMode.HTML,
            )
    elif m.chat.type == ChatType.PRIVATE:
        text=f"Your ID is <code>{m.chat.id}</code>."
        if m.reply_to_message:
            if m.forward_from:
                text+=f"Forwarded from user ID <code>{m.forward_from.id}</code>."
            elif m.forward_from_chat:
                text+=f"Forwarded from user ID <code>{m.forward_from_chat.id}</code>."
        await m.reply_text(text)
    else:
        text=f"Chat ID <code>{m.chat.id}</code>\nYour ID <code>{m.from_user.id}</code>"
        await m.reply_text(text)
    return
