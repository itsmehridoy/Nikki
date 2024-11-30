from traceback import format_exc

from pyrogram import enums
from pyrogram.errors import (ChatAdminRequired, PeerIdInvalid, RightForbidden,
                             RPCError, UserAdminInvalid)
from pyrogram.filters import regex
from pyrogram.types import (CallbackQuery, ChatPrivileges, Message)

from Powers import LOGGER
from Powers.bot_class import Nikki
from Powers.utils.caching import ADMIN_CACHE, admin_cache_reload
from Powers.utils.extract_user import extract_user
from Powers.utils.parser import mention_html
from Powers.utils.string import extract_time

@Nikki.on_cmd("tban", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_restrict_members", is_both=True)
async def tban_usr(c: Nikki, m: Message):
    if len(m.text.split()) == 1 and not m.reply_to_message:
        await m.reply_text(text="I can't ban nothing!")
        return

    try:
        user_id, user_first_name, _ = await extract_user(c, m)
    except Exception:
        return

    if not user_id:
        await m.reply_text("Cannot find the user to ban")
        return
    if user_id == Nikki.id:
        await m.reply_text("WTF?? Why would I ban myself?")
        return

    r_id = m.reply_to_message.id if m.reply_to_message else m.id

    if m.reply_to_message and len(m.text.split()) >= 2:
        reason = m.text.split(None, 1)[1]
    elif not m.reply_to_message and len(m.text.split()) >= 3:
        reason = m.text.split(None, 2)[2]
    else:
        await m.reply_text("Read /help !!")
        return

    if not reason:
        await m.reply_text("You haven't specified a time to ban this user for!")
        return

    split_reason = reason.split(None, 1)
    time_val = split_reason[0].lower()
    reason = split_reason[1] if len(split_reason) > 1 else ""

    bantime = await extract_time(m, time_val)

    if not bantime:
        return

    try:
        admins_group = {i[0] for i in ADMIN_CACHE[m.chat.id]}
    except KeyError:
        admins_group = await admin_cache_reload(m, "ban")

    if user_id in admins_group:
        await m.reply_text(text="ᴡʜʏ ᴡᴏᴜʟᴅ ɪ ʙᴀɴ ᴀɴ ᴀᴅᴍɪɴ? ᴛʜᴀᴛ sᴏᴜɴᴅs ʟɪᴋᴇ ᴀ ᴘʀᴇᴛᴛʏ ᴅᴜᴍʙ ɪᴅᴇᴀ.")
        return

    admin_mention = m.from_user.mention if m.from_user else "ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ."
    try:
        await m.reply_to_message.delete()
        await m.chat.ban_member(
            user_id,
            until_date=bantime)
        banned_mention = user_first_name if m.from_user else "Unknown User"
        txt = f"• <b>ʙᴀɴ ᴇᴠᴇɴᴛ</b>\n• <b>ʙᴀɴɴᴇᴅ ʙʏ</b>: {admin_mention}\n• <b>ᴜsᴇʀ</b>: {banned_mention}"
        if reason:
            txt += f"\n<b>• ʀᴇᴀsᴏɴ</b>: {reason}"
        if time_val:
            txt += f"\n<b>• ʙᴀɴɴᴇᴅ ғᴏʀ </b>:{time_val}"
        try:
            await m.reply_text(
                reply_to_message_id=r_id,
                text=txt,
                parse_mode=enums.ParseMode.HTML,
            )
        except Exception:
            await m.reply_text(
                reply_to_message_id=r_id,
                text=txt,
                parse_mode=enums.ParseMode.HTML,
            )
    except ChatAdminRequired:
        await m.reply_text(text="I'm not an admin or I don't have rights.")
    except PeerIdInvalid:
        await m.reply_text(
            "I have not seen this user yet...!\nMind forwarding one of their messages so I can recognize them?",
        )
    except UserAdminInvalid:
        await m.reply_text(
            text="Cannot act on this user, maybe I wasn't the one who changed their permissions."
        )
    except RightForbidden:
        await m.reply_text(text="I don't have enough rights to ban this user.")
    except RPCError as ef:
        await m.reply_text(
            (
                f"""Some error occurred, report it using `/bug`

      <b>Error:</b> <code>{ef}</code>"""
            )
        )
        LOGGER.error(ef)
        LOGGER.error(format_exc())

    return

@Nikki.on_cmd("stban", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_restrict_members", is_both=True)
async def stban_usr(c: Nikki, m: Message):
    if len(m.text.split()) == 1 and not m.reply_to_message:
        await m.reply_text(text="I can't ban nothing!")
        return

    try:
        user_id, _, _ = await extract_user(c, m)
    except Exception:
        return

    if not user_id:
        await m.reply_text("Cannot find user to ban")
        return
    if user_id == Nikki.id:
        await m.reply_text("What the heck? Why would I ban myself?")
        return

    if m.reply_to_message and len(m.text.split()) >= 2:
        reason = m.text.split(None, 1)[1]
    elif not m.reply_to_message and len(m.text.split()) >= 3:
        reason = m.text.split(None, 2)[2]
    else:
        await m.reply_text("Read /help !!")
        return

    if not reason:
        await m.reply_text("You haven't specified a time to ban this user for!")
        return

    split_reason = reason.split(None, 1)
    time_val = split_reason[0].lower()
    reason = split_reason[1] if len(split_reason) > 1 else ""

    bantime = await extract_time(m, time_val)

    if not bantime:
        return

    try:
        admins_group = {i[0] for i in ADMIN_CACHE[m.chat.id]}
    except KeyError:
        admins_group = await admin_cache_reload(m, "ban")

    if user_id in admins_group:
        await m.reply_text(text="ᴡʜʏ ᴡᴏᴜʟᴅ ɪ ʙᴀɴ ᴀɴ ᴀᴅᴍɪɴ? ᴛʜᴀᴛ sᴏᴜɴᴅs ʟɪᴋᴇ ᴀ ᴘʀᴇᴛᴛʏ ᴅᴜᴍʙ ɪᴅᴇᴀ.")
        return

    try:
        await m.chat.ban_member(user_id, until_date=bantime)
        await m.delete()
        if m.reply_to_message:
            await m.reply_to_message.delete()
            return
        return
    except ChatAdminRequired:
        await m.reply_text(text="I'm not admin or I don't have rights.")
    except PeerIdInvalid:
        await m.reply_text(
            "I have not seen this user yet...!\nMind forwarding one of their message so I can recognize them?",
        )
    except UserAdminInvalid:
        await m.reply_text(
            text="Cannot act on this user, maybe I wasn't the one who changed their permissions."
        )
    except RightForbidden:
        await m.reply_text(text="I don't have enough rights to ban this user.")
    except RPCError as ef:
        await m.reply_text(
            text=f"""Some error occured, report it using `/bug`

      <b>Error:</b> <code>{ef}</code>"""
        )
        LOGGER.error(ef)
        LOGGER.error(format_exc())
    return


@Nikki.on_cmd("dtban", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_restrict_members", is_both=True)
async def dtban_usr(c: Nikki, m: Message):
    if len(m.text.split()) == 1 and not m.reply_to_message:
        await m.reply_text(text="I can't ban nothing!")
        return

    if not m.reply_to_message:
        await m.reply_text(
            "Reply to a message with this command to temp ban and delete the message.",
        )
        return

    user_id = m.reply_to_message.from_user.id
    user_first_name = m.reply_to_message.from_user.first_name

    if not user_id:
        await m.reply_text("Cannot find user to ban")
        return
    if user_id == Nikki.id:
        await m.reply_text("Huh, why would I ban myself?")
        return

    if m.reply_to_message and len(m.text.split()) >= 2:
        reason = m.text.split(None, 1)[1]
    elif not m.reply_to_message and len(m.text.split()) >= 3:
        reason = m.text.split(None, 2)[2]
    else:
        await m.reply_text("Read /help !!")
        return

    if not reason:
        await m.reply_text("You haven't specified a time to ban this user for!")
        return

    split_reason = reason.split(None, 1)
    time_val = split_reason[0].lower()
    reason = split_reason[1] if len(split_reason) > 1 else ""

    bantime = await extract_time(m, time_val)

    if not bantime:
        return

    try:
        admins_group = {i[0] for i in ADMIN_CACHE[m.chat.id]}
    except KeyError:
        admins_group = await admin_cache_reload(m, "ban")

    if user_id in admins_group:
        await m.reply_text(text="ᴡʜʏ ᴡᴏᴜʟᴅ ɪ ʙᴀɴ ᴀɴ ᴀᴅᴍɪɴ? ᴛʜᴀᴛ sᴏᴜɴᴅs ʟɪᴋᴇ ᴀ ᴘʀᴇᴛᴛʏ ᴅᴜᴍʙ ɪᴅᴇᴀ.")
        return

    try:
        if m.from_user:
            admin_name = m.from_user.first_name
            admin_id = m.from_user.id
            admin = await mention_html(admin_name, admin_id)
        else:
            admin = "ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ."
        
        banned = await mention_html(user_first_name, user_id)
        chat_title = m.chat.title
        await m.chat.ban_member(user_id, until_date=bantime)
        await m.reply_to_message.delete()
        txt = f"• <b>ʙᴀɴ ᴇᴠᴇɴᴛ</b>\n• <b>ʙᴀɴɴᴇᴅ ʙʏ</b>: {admin}\n• <b>ᴜsᴇʀ</b>: {banned}"
        if reason:
            txt += f"\n<b>• ʀᴇᴀsᴏɴ</b>: {reason}"
        if bantime:
            txt += f"\n<b>• ʙᴀɴɴᴇᴅ ғᴏʀ</b>: {time_val}"
        try:
            await m.reply_text(
                text=txt,
                parse_mode=enums.ParseMode.HTML,
            )
        except Exception:
            await m.reply_text(
                text=txt,
                parse_mode=enums.ParseMode.HTML,
            )
    except ChatAdminRequired:
        await m.reply_text(text="I'm not admin or I don't have rights.")
    except PeerIdInvalid:
        await m.reply_text(
            "I have not seen this user yet...!\nMind forwarding one of their message so I can recognize them?",
        )
    except UserAdminInvalid:
        await m.reply_text(
            text="Cannot act on this user, maybe I wasn't the one who changed their permissions."
        )
    except RightForbidden:
        await m.reply_text(text="I don't have enough rights to ban this user.")
    except RPCError as ef:
        await m.reply_text(
            text=f"""Some error occured, report it using `/bug`

      <b>Error:</b> <code>{ef}</code>"""
        )
        LOGGER.error(ef)
        LOGGER.error(format_exc())
    return

@Nikki.on_cmd("kick", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_restrict_members", is_both=True)
async def kick_usr(c: Nikki, m: Message):
    if len(m.text.split()) == 1 and not m.reply_to_message:
        await m.reply_text(text="I can't kick nothing!")
        return

    reason = None

    if m.reply_to_message:
        r_id = m.reply_to_message.id
        if len(m.text.split()) >= 2:
            reason = m.text.split(None, 1)[1]
    else:
        r_id = m.id
        if len(m.text.split()) >= 3:
            reason = m.text.split(None, 2)[2]
    try:
        user_id, user_first_name, _ = await extract_user(c, m)
    except Exception:
        return

    if not user_id:
        await m.reply_text("Cannot find user to kick")
        return

    if user_id == Nikki.id:
        await m.reply_text("Huh, why would I kick myself?")
        return

    try:
        admins_group = {i[0] for i in ADMIN_CACHE[m.chat.id]}
    except KeyError:
        admins_group = await admin_cache_reload(m, "kick")

    if user_id in admins_group:
        await m.reply_text(text="ᴡʜʏ ᴡᴏᴜʟᴅ ɪ ʙᴀɴ ᴀɴ ᴀᴅᴍɪɴ? ᴛʜᴀᴛ sᴏᴜɴᴅs ʟɪᴋᴇ ᴀ ᴘʀᴇᴛᴛʏ ᴅᴜᴍʙ ɪᴅᴇᴀ.")
        return

    try:
        if m.from_user:
            admin_name = m.from_user.first_name
            admin_id = m.from_user.id
            admin = await mention_html(admin_name, admin_id)
        else:
            admin = "ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ."
        kicked = await mention_html(user_first_name, user_id)
        await m.chat.ban_member(user_id)
        txt = f"• <b>ᴋɪᴄᴋ ᴇᴠᴇɴᴛ</b>\n• <b>ᴋɪᴄᴋᴇᴅ ʙʏ</b>: {admin}\n• <b>ᴜsᴇʀ</b>: {kicked}"
        if reason:
            txt += f"\n<b>• ʀᴇᴀsᴏɴ</b>: {reason}"
        try:
            await m.reply_text(
                reply_to_message_id=r_id,
                text=txt,
                parse_mode=enums.ParseMode.HTML,
            )
        except:
            await m.reply_text(
                reply_to_message_id=r_id,
                text=txt,
                parse_mode=enums.ParseMode.HTML,
            )
        await m.chat.unban_member(user_id)
    except ChatAdminRequired:
        await m.reply_text(text="I'm not admin or I don't have rights.")
    except PeerIdInvalid:
        await m.reply_text(
            "I have not seen this user yet...!\nMind forwarding one of their message so I can recognize them?",
        )
    except UserAdminInvalid:
        await m.reply_text(
            text="Cannot act on this user, maybe I wasn't the one who changed their permissions."
        )
    except RightForbidden:
        await m.reply_text(text="I don't have enough rights to ban this user.")
    except RPCError as ef:
        await m.reply_text(
            text=f"""Some error occured, report it using `/bug`

      <b>Error:</b> <code>{ef}</code>"""
        )
        LOGGER.error(ef)
        LOGGER.error(format_exc())

    return


@Nikki.on_cmd("skick", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_restrict_members", is_both=True)
async def skick_usr(c: Nikki, m: Message):
    if len(m.text.split()) == 1 and not m.reply_to_message:
        await m.reply_text(text="I can't kick nothing!")
        return

    try:
        user_id, _, _ = await extract_user(c, m)
    except Exception:
        return

    if not user_id:
        await m.reply_text("Cannot find user to kick")
        return

    if user_id == Nikki.id:
        await m.reply_text("Huh, why would I kick myself?")
        return
      
    try:
        admins_group = {i[0] for i in ADMIN_CACHE[m.chat.id]}
    except KeyError:
        admins_group = await admin_cache_reload(m, "kick")

    if user_id in admins_group:
        await m.reply_text(text="ᴡʜʏ ᴡᴏᴜʟᴅ ɪ ʙᴀɴ ᴀɴ ᴀᴅᴍɪɴ? ᴛʜᴀᴛ sᴏᴜɴᴅs ʟɪᴋᴇ ᴀ ᴘʀᴇᴛᴛʏ ᴅᴜᴍʙ ɪᴅᴇᴀ.")
        return

    try:
        await m.chat.ban_member(user_id)
        await m.delete()
        if m.reply_to_message:
            await m.reply_to_message.delete()
        await m.chat.unban_member(user_id)
    except ChatAdminRequired:
        await m.reply_text(text="I'm not admin or I don't have rights.")
    except PeerIdInvalid:
        await m.reply_text(
            "I have not seen this user yet...!\nMind forwarding one of their message so I can recognize them?",
        )
    except UserAdminInvalid:
        await m.reply_text(
            text="Cannot act on this user, maybe I wasn't the one who changed their permissions."
        )
    except RightForbidden:
        await m.reply_text(text="I don't have enough rights to kick this user.")
    except RPCError as ef:
        await m.reply_text(
            text=f"""Some error occured, report it using `/bug`

      <b>Error:</b> <code>{ef}</code>"""
        )
        LOGGER.error(ef)
        LOGGER.error(format_exc())

    return


@Nikki.on_cmd("dkick", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_restrict_members", is_both=True)
async def dkick_usr(c: Nikki, m: Message):
    if len(m.text.split()) == 1 and not m.reply_to_message:
        await m.reply_text(text="I can't kick nothing!")
        return
    if not m.reply_to_message:
        return await m.reply_text("Reply to a message to delete it and kick the user!")

    reason = None

    user_id = m.reply_to_message.from_user.id
    user_first_name = m.reply_to_message.from_user.first_name

    if not user_id:
        await m.reply_text("Cannot find user to kick")
        return

    if user_id == Nikki.id:
        await m.reply_text("Huh, why would I kick myself?")
        return

    try:
        admins_group = {i[0] for i in ADMIN_CACHE[m.chat.id]}
    except KeyError:
        admins_group = await admin_cache_reload(m, "kick")

    if user_id in admins_group:
        await m.reply_text(text="ᴡʜʏ ᴡᴏᴜʟᴅ ɪ ʙᴀɴ ᴀɴ ᴀᴅᴍɪɴ? ᴛʜᴀᴛ sᴏᴜɴᴅs ʟɪᴋᴇ ᴀ ᴘʀᴇᴛᴛʏ ᴅᴜᴍʙ ɪᴅᴇᴀ.")
        return

    try:
        await m.reply_to_message.delete()
        await m.chat.ban_member(user_id)
        admin_name = m.from_user.first_name if m.from_user else "ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ."
        admin_id = m.from_user.id if m.from_user else 0
        admin = await mention_html(admin_name, admin_id)
        kicked = await mention_html(user_first_name, user_id)
        chat_title = m.chat.title
        txt = f"• <b>ᴋɪᴄᴋ ᴇᴠᴇɴᴛ</b>\n• <b>ᴋɪᴄᴋᴇᴅ ʙʏ</b>: {admin}\n• <b>ᴜsᴇʀ</b>: {kicked}"
        if reason:
            txt += f"\n<b>• ʀᴇᴀsᴏɴ</b>: {reason}"
        try:
            await m.reply_text(
                text=txt,
                parse_mode=enums.ParseMode.HTML,
            )
        except:
            await m.reply_text(
                text=txt,
                parse_mode=enums.ParseMode.HTML,
            )
        await m.chat.unban_member(user_id)
    except ChatAdminRequired:
        await m.reply_text(text="I'm not an admin or I don't have rights.")
    except PeerIdInvalid:
        await m.reply_text(
            "I have not seen this user yet...!\nMind forwarding one of their messages so I can recognize them?",
        )
    except UserAdminInvalid:
        await m.reply_text(
            text="Cannot act on this user, maybe I wasn't the one who changed their permissions."
        )
    except RightForbidden:
        await m.reply_text(text="I don't have enough rights to kick this user.")
    except RPCError as ef:
        await m.reply_text(
            text=f"""Some error occurred, report it using `/bug`

      <b>Error:</b> <code>{ef}</code>"""
        )
        LOGGER.error(ef)
        LOGGER.error(format_exc())

    return

@Nikki.on_cmd("unban", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_restrict_members", is_both=True)
async def unban_usr(c: Nikki, m: Message):
    try:
        if len(m.text.split()) == 1 and not m.reply_to_message:
            await m.reply_text(text="I can't unban nothing!")
            return

        if m.reply_to_message and not m.reply_to_message.from_user:
            user_id, user_first_name = (
                m.reply_to_message.sender_chat.id,
                m.reply_to_message.sender_chat.title,
            )
        else:
            try:
                user_id, user_first_name, _ = await extract_user(c, m)
            except Exception:
                return

        if m.reply_to_message and len(m.text.split()) >= 2:
            reason = m.text.split(None, 2)[1]
        elif not m.reply_to_message and len(m.text.split()) >= 3:
            reason = m.text.split(None, 2)[2]
        else:
            reason = None

        statu = (await m.chat.get_member(user_id)).status
        if statu not in [enums.ChatMemberStatus.BANNED, enums.ChatMemberStatus.RESTRICTED]:
            await m.reply_text("User is not banned in this chat\nOr using this command as a reply to his message")
            return

        admin = m.from_user.mention if m.from_user else "ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ."
        await m.chat.unban_member(user_id)
        unbanned = await mention_html(user_first_name, user_id)
        txt = f"• <b>ᴜɴʙᴀɴ ᴇᴠᴇɴᴛ</b>\n• <b>ᴜɴʙᴀɴɴᴇᴅ ʙʏ</b>: {admin}\n• <b>ᴜsᴇʀ</b>: {unbanned}"
        if reason:
            txt += f"\n<b>• ʀᴇᴀsᴏɴ</b>: {reason}"
        await m.reply_text(
            text=txt,
            quote=True,
        )
    except ChatAdminRequired:
        await m.reply_text(text="I'm not an admin or I don't have rights.")
    except RightForbidden:
        await m.reply_text(text="I don't have enough rights to unban this user.")
    except RPCError as ef:
        await m.reply_text(
            text=f"""Some error occurred, report it using `/bug`

      <b>Error:</b> <code>{ef}</code>"""
        )
        LOGGER.error(ef)
        LOGGER.error(format_exc())

    return

@Nikki.on_cmd("sban", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_restrict_members", is_both=True)
async def sban_usr(c: Nikki, m: Message):
    if len(m.text.split()) == 1 and not m.reply_to_message:
        await m.reply_text(text="I can't ban nothing!")
        return

    if m.reply_to_message and not m.reply_to_message.from_user:
        user_id = m.reply_to_message.sender_chat.id
    else:
        try:
            user_id, _, _ = await extract_user(c, m)
        except Exception:
            return

    if not user_id:
        await m.reply_text("Cannot find user to ban")
        return
    if user_id == m.chat.id:
        await m.reply_text("That's an admin!")
        return
    if user_id == Nikki.id:
        await m.reply_text("Huh, why would I ban myself?")
        return
      
    try:
        admins_group = {i[0] for i in ADMIN_CACHE[m.chat.id]}
    except KeyError:
        admins_group = await admin_cache_reload(m, "ban")

    if user_id in admins_group:
        await m.reply_text(text="ᴡʜʏ ᴡᴏᴜʟᴅ ɪ ʙᴀɴ ᴀɴ ᴀᴅᴍɪɴ? ᴛʜᴀᴛ sᴏᴜɴᴅs ʟɪᴋᴇ ᴀ ᴘʀᴇᴛᴛʏ ᴅᴜᴍʙ ɪᴅᴇᴀ.")
        return

    try:
        await m.chat.ban_member(user_id)
        await m.delete()
        if m.reply_to_message:
            await m.reply_to_message.delete()
    except ChatAdminRequired:
        await m.reply_text(text="I'm not admin or I don't have rights.")
    except PeerIdInvalid:
        await m.reply_text(
            "I have not seen this user yet...!\nMind forwarding one of their message so I can recognize them?",
        )
    except UserAdminInvalid:
        await m.reply_text(
            text="Cannot act on this user, maybe I wasn't the one who changed their permissions."
        )
    except RightForbidden:
        await m.reply_text(text="I don't have enough rights to ban this user.")
    except RPCError as ef:
        await m.reply_text(
            text=f"""Some error occured, report it using `/bug`

      <b>Error:</b> <code>{ef}</code>"""
        )
        LOGGER.error(ef)
        LOGGER.error(format_exc())
    return


@Nikki.on_cmd("dban", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_restrict_members", is_both=True)
async def dban_usr(c: Nikki, m: Message):
    if len(m.text.split()) == 1 and not m.reply_to_message:
        await m.reply_text(text="I can't ban nothing!")
        return

    if not m.reply_to_message:
        return await m.reply_text("Reply to a message to delete it and ban the user!")

    if m.reply_to_message and not m.reply_to_message.from_user:
        user_id, user_first_name = (
            m.reply_to_message.sender_chat.id,
            m.reply_to_message.sender_chat.title,
        )
    else:
        user_id, user_first_name = (
            m.reply_to_message.from_user.id,
            m.reply_to_message.from_user.first_name,
        )

    if not user_id:
        await m.reply_text("Cannot find user to ban")
        return
    if user_id == m.chat.id:
        await m.reply_text("That's an admin!")
        return
    if user_id == Nikki.id:
        await m.reply_text("Huh, why would I ban myself?")
        return
      
    try:
        admins_group = {i[0] for i in ADMIN_CACHE[m.chat.id]}
    except KeyError:
        admins_group = await admin_cache_reload(m, "ban")

    if user_id in admins_group:
        await m.reply_text(text="ᴡʜʏ ᴡᴏᴜʟᴅ ɪ ʙᴀɴ ᴀɴ ᴀᴅᴍɪɴ? ᴛʜᴀᴛ sᴏᴜɴᴅs ʟɪᴋᴇ ᴀ ᴘʀᴇᴛᴛʏ ᴅᴜᴍʙ ɪᴅᴇᴀ.")
        return

    reason = None
    if len(m.text.split()) >= 2:
        reason = m.text.split(None, 1)[1]

    try:
        await m.reply_to_message.delete()
        await m.chat.ban_member(user_id)
        admin_mention = m.from_user.mention if m.from_user else "ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ."
        user_mention = m.reply_to_message.from_user.mention if m.reply_to_message.from_user else "Unknown User"
        txt = f"• <b>ʙᴀɴ ᴇᴠᴇɴᴛ</b>\n• <b>ʙᴀɴɴᴇᴅ ʙʏ</b>: {admin_mention}\n• <b>ᴜsᴇʀ</b>: {user_mention}"
        if reason:
            txt += f"\n<b>• ʀᴇᴀsᴏɴ</b>: {reason}"
        try:
            await c.send_message(
                m.chat.id,
                text=txt,
                parse_mode=enums.ParseMode.HTML,
            )
        except Exception:
            await c.send_message(
                m.chat.id,
                txt,
                parse_mode=enums.ParseMode.HTML,
            )
    except ChatAdminRequired:
        await m.reply_text(text="I'm not an admin or I don't have rights.")
    except PeerIdInvalid:
        await m.reply_text(
            "I have not seen this user yet...!\nMind forwarding one of their messages so I can recognize them?",
        )
    except UserAdminInvalid:
        await m.reply_text(
            text="Cannot act on this user, maybe I wasn't the one who changed their permissions."
        )
    except RightForbidden:
        await m.reply_text(text="I don't have enough rights to ban this user.")
    except RPCError as ef:
        await m.reply_text(
            text=f"""Some error occurred, report it using `/bug`

      <b>Error:</b> <code>{ef}</code>"""
        )
        LOGGER.error(ef)
        LOGGER.error(format_exc())

    return

@Nikki.on_cmd("ban", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_restrict_members", is_both=True)
async def ban_usr(c: Nikki, m: Message):
    if len(m.text.split()) == 1 and not m.reply_to_message:
        await m.reply_text(text="I can't ban nothing!")
        return
    if m.reply_to_message and not m.reply_to_message.from_user:
        user_id, user_first_name = (
            m.reply_to_message.sender_chat.id,
            m.reply_to_message.sender_chat.title,
        )
    else:
        try:
            user_id, user_first_name, _ = await extract_user(c, m)
        except Exception:
            return

    if not user_id:
        await m.reply_text("Cannot find user to ban")
        return
    if user_id == m.chat.id:
        await m.reply_text("That's an admin!")
        return
    if user_id == Nikki.id:
        await m.reply_text("Huh, why would I ban myself?")
        return

    try:
        admins_group = {i[0] for i in ADMIN_CACHE[m.chat.id]}
    except KeyError:
        admins_group = await admin_cache_reload(m, "ban")

    if user_id in admins_group:
        await m.reply_text(text="ᴡʜʏ ᴡᴏᴜʟᴅ ɪ ʙᴀɴ ᴀɴ ᴀᴅᴍɪɴ? ᴛʜᴀᴛ sᴏᴜɴᴅs ʟɪᴋᴇ ᴀ ᴘʀᴇᴛᴛʏ ᴅᴜᴍʙ ɪᴅᴇᴀ.")
        return

    reason = None
    if m.reply_to_message:
        r_id = m.reply_to_message.id
        if len(m.text.split()) >= 2:
            reason = m.text.split(None, 1)[1]
    else:
        r_id = m.id
        if len(m.text.split()) >= 3:
            reason = m.text.split(None, 2)[2]

    try:
        if m.from_user:
            banned_by = m.from_user.mention
        else:
            banned_by = "ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ."
        
        await m.chat.ban_member(user_id)
        banned = await mention_html(user_first_name, user_id)
        txt = f"• <b>ʙᴀɴ ᴇᴠᴇɴᴛ</b>\n• <b>ʙᴀɴɴᴇᴅ ʙʏ</b>: {banned_by}</b>\n• <b>ᴜsᴇʀ</b>: {banned}</b>"
        if reason:
            txt += f"\n<b>• ʀᴇᴀsᴏɴ</b>: {reason}"
        try:
            await m.reply_text(
                reply_to_message_id=r_id,
                text=txt,
                parse_mode=enums.ParseMode.HTML,
            )
        except Exception:
            await m.reply_text(
                reply_to_message_id=r_id,
                text=txt,
                parse_mode=enums.ParseMode.HTML,
            )
    except ChatAdminRequired:
        await m.reply_text(text="I'm not admin or I don't have rights.")
    except PeerIdInvalid:
        await m.reply_text(
            "I have not seen this user yet...!\nMind forwarding one of their messages so I can recognize them?",
        )
    except UserAdminInvalid:
        await m.reply_text(
            text="Cannot act on this user, maybe I wasn't the one who changed their permissions."
        )
    except RightForbidden:
        await m.reply_text(text="I don't have enough rights to ban this user.")
    except RPCError as ef:
        await m.reply_text(
            text=f"""Some error occurred, report it using `/bug`

      <b>Error:</b> <code>{ef}</code>"""
        )
        LOGGER.error(ef)
        LOGGER.error(format_exc())
    return

@Nikki.on_cmd("kickme", group_only=True)
async def kickme(c: Nikki, m: Message):
    try:
        mem = await c.get_chat_member(m.chat.id,m.from_user.id)
        if mem.status in [enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER]:
            try:
                await c.promote_chat_member(
                    m.chat.id,
                    m.from_user.id,
                    ChatPrivileges(can_manage_chat=False)
                )
            except Exception:
                await m.reply_text("I can't demote you so I can't ban you")
                return
        await m.chat.ban_member(m.from_user.id)
        txt = "Yeah, you're right - get out."
        await m.reply_text(txt)
        await m.chat.unban_member(m.from_user.id)
    except RPCError as ef:
        if "400 USER_ADMIN_INVALID" in ef:
            await m.reply_text("Looks like I can't kick you (⊙_⊙)")
            return
        elif "400 CHAT_ADMIN_REQUIRED" in ef:
            await m.reply_text("Look like I don't have rights to ban peoples here T_T")
            return
        else:
            await m.reply_text(
                text=f"""Some error occured, report it using `/bug`

        <b>Error:</b> <code>{ef}</code>"""
            )
    except Exception as ef:
        await m.reply_text(
            text=f"""Some error occured, report it using `/bug`

      <b>Error:</b> <code>{ef}</code>"""
        )
    return

__PLUGIN__ = "Bᴀɴs"

_DISABLE_CMDS_ = ["kickme"]

__alt_name__ = [
    "ban",
    "kickme",
    "kick",
    "skick",
    "dkick",
    "sban",
    "dban",
    "tban",
    "stban",
    "dtban",
    "unban",
]

__HELP__ = """
**Dᴇsᴄʀɪᴘᴛɪᴏɴ :**
sᴏᴍᴇ ᴘᴇᴏᴘʟᴇ ɴᴇᴇᴅ ᴛᴏ ʙᴇ ᴘᴜʙʟɪᴄʟʏ ʙᴀɴɴᴇᴅ; sᴘᴀᴍᴍᴇʀs, ᴀɴɴᴏʏᴀɴᴄᴇs, ᴏʀ ᴊᴜsᴛ ᴛʀᴏʟʟs.

ᴛʜɪs ᴍᴏᴅᴜʟᴇ ᴀʟʟᴏᴡs ʏᴏᴜ ᴛᴏ ᴅᴏ ᴛʜᴀᴛ ᴇᴀsɪʟʏ, ʙʏ ᴇxᴘᴏsɪɴɢ sᴏᴍᴇ ᴄᴏᴍᴍᴏɴ ᴀᴄᴋᴛɪᴏɴs, sᴏ ᴇᴠᴇʀʏᴏɴᴇ ᴡɪʟʟ sᴇᴇ!
────────────────────────

**Cᴏᴍᴍᴀɴᴅs :**
๏ /kickme: ᴋɪᴄᴋs ᴛʜᴇ ᴜsᴇʀ ᴡʜᴏ ɪssᴜᴇᴅ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ.

**Tʜᴇ Fᴏʟʟᴏᴡɪɴɢ Cᴏᴍᴍᴀɴᴅs Aʀᴇ Aᴅᴍɪɴ Oɴʟʏ :**
๏ /kick: ᴋɪᴄᴋ ᴛʜᴇ ᴜsᴇʀ ʀᴇᴘʟɪᴇᴅ ᴏʀ ᴛᴀɢɢᴇᴅ.
๏ /skick: ᴋɪᴄᴋ ᴛʜᴇ ᴜsᴇʀ ʀᴇᴘʟɪᴇᴅ , ᴛᴀɢɢᴇᴅ ᴀɴᴅ ᴅᴇʟᴇᴛᴇ ʏᴏᴜʀ ᴍᴇsssᴀɢᴇ.
๏ /dkick: ᴋɪᴄᴋ ᴛʜᴇ ᴜsᴇʀ ʀᴇᴘʟɪᴇᴅ ᴀɴᴅ ᴅᴇʟᴇᴛᴇ ᴛʜᴇɪʀ ᴍᴇssᴀɢᴇ.
๏ /ban: ʙᴀɴs ᴛʜᴇ ᴜsᴇʀ ʀᴇᴘʟɪᴇᴅ ᴛᴏ ᴏʀ ᴛᴀɢɢᴇᴅ.
๏ /sban: ʙᴀɴs ᴛʜᴇ ᴜsᴇʀ ʀᴇᴘʟɪᴇᴅ ᴏʀ ᴛᴀɢɢᴇᴅ ᴀɴᴅ ᴅᴇʟᴇᴛᴇ ʏᴏᴜʀ ᴍᴇsssᴀɢᴇ.
๏ /dban: ʙᴀɴs ᴛʜᴇ ᴜsᴇʀ ʀᴇᴘʟɪᴇᴅ ᴀɴᴅ ᴅᴇʟᴇᴛᴇ ᴛʜᴇɪʀ ᴍᴇssᴀɢᴇ.
๏ /tban ᴜsᴇʀʜᴀɴᴅʟᴇ x ᴛɪᴍᴇ: ʙᴀɴs ᴀ ᴜsᴇʀ ғᴏʀ x ᴛɪᴍᴇ.
๏ /stban ᴜsᴇʀʜᴀɴᴅʟᴇ x ᴛɪᴍᴇ: sɪʟᴇɴᴛʟʏ bans ᴀ ᴜsᴇʀ ғᴏʀ x ᴛɪᴍᴇ.
๏ /dtban ᴜsᴇʀʜᴀɴᴅʟᴇ x ᴛɪᴍᴇ: sɪʟᴇɴᴛʟʏ bans ᴀ ᴜsᴇʀ ғᴏʀ x ᴛɪᴍᴇ ᴀɴᴅ ᴅᴇʟᴇᴛᴇ ᴛʜᴇ ʀᴇᴘʟɪᴇᴅ ᴍᴇssᴀɢᴇ.
๏ /unban: ᴜɴʙᴀɴs ᴛʜᴇ ᴜsᴇʀ ʀᴇᴘʟɪᴇᴅ ᴛᴏ ᴏʀ ᴛᴀɢɢᴇᴅ."""
