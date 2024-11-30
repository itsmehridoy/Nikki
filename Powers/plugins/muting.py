from random import choice
from traceback import format_exc

from pyrogram import enums
from pyrogram.errors import (ChatAdminRequired, RightForbidden, RPCError,
                             UserNotParticipant)
from pyrogram.filters import regex
from pyrogram.types import (CallbackQuery, ChatPermissions, Message)

from Powers import LOGGER
from Powers.bot_class import Nikki
from Powers.utils.caching import ADMIN_CACHE, admin_cache_reload
from Powers.utils.extract_user import extract_user
from Powers.utils.parser import mention_html
from Powers.utils.string import extract_time

@Nikki.on_cmd("tmute", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_restrict_members", is_both=True)
async def tmute_usr(c: Nikki, m: Message):
    if len(m.text.split()) == 1 and not m.reply_to_message:
        await m.reply_text("I can't mute nothing!")
        return

    try:
        user_id, user_first_name, _ = await extract_user(c, m)
    except Exception:
        return

    if not user_id:
        await m.reply_text("Cannot find user to mute !")
        return
    if user_id == Nikki.id:
        await m.reply_text("Huh, why would I mute myself?")
        return

    try:
        admins_group = {i[0] for i in ADMIN_CACHE[m.chat.id]}
    except KeyError:
        admins_group = await admin_cache_reload(m, "mute")

    if user_id in admins_group:
        await m.reply_text(text="This user is an admin, I cannot mute them!")
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
        await m.reply_text("You haven't specified a time to mute this user for!")
        return

    split_reason = reason.split(None, 1)
    time_val = split_reason[0].lower()
    reason = split_reason[1] if len(split_reason) > 1 else ""
    mutetime = await extract_time(m, time_val)

    if not mutetime:
        return

    try:
        await m.chat.restrict_member(
            user_id,
            ChatPermissions(),
            mutetime,
        )
        if m.from_user:
            admin_name = m.from_user.first_name
            admin_id = m.from_user.id
            admin = await mention_html(admin_name, admin_id)
        else:
            admin = "**ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ.**"
        muted = await mention_html(user_first_name, user_id)
        txt = f"• <b>ᴍᴜᴛᴇ ᴇᴠᴇɴᴛ</b>\n• <b>ᴍᴜᴛᴇᴅ ʙʏ</b>: {admin}\n• <b>ᴜsᴇʀ</b>: {muted}"
        if reason:
            txt += f"\n<b>• ʀᴇᴀsᴏɴ</b>: {reason}"
        if mutetime:
            txt += f"\n<b>• ᴍᴜᴛᴇᴅ ғᴏʀ</b>: {time_val}"
        try:
            await m.reply_text(
                reply_to_message_id=r_id,
                text=txt,
            )
        except Exception:
            await m.reply_text(
                reply_to_message_id=r_id,
                text=txt,
            )
    except ChatAdminRequired:
        await m.reply_text(text="I'm not admin or I don't have rights.")
    except RightForbidden:
        await m.reply_text(text="I don't have enough rights to ban this user.")
    except UserNotParticipant:
        await m.reply_text("How can I mute a user who is not a part of this chat?")
    except RPCError as ef:
        await m.reply_text(
            text=f"""Some error occured, report it using `/bug`

      <b>Error:</b> <code>{ef}</code>"""
        )
        LOGGER.error(ef)

    return


@Nikki.on_cmd("dtmute", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_restrict_members", is_both=True)
async def dtmute_usr(c: Nikki, m: Message):
    if len(m.text.split()) == 1 and not m.reply_to_message:
        await m.reply_text("I can't mute nothing!")
        return

    if not m.reply_to_message:
        return await m.reply_text("No replied message and user to delete and mute!")

    reason = None
    user_id = m.reply_to_message.from_user.id
    user_first_name = m.reply_to_message.from_user.first_name

    if not user_id:
        await m.reply_text("Cannot find user to mute !")
        return
    if user_id == Nikki.id:
        await m.reply_text("Huh, why would I mute myself?")
        return

    try:
        admins_group = {i[0] for i in ADMIN_CACHE[m.chat.id]}
    except KeyError:
        admins_group = await admin_cache_reload(m, "mute")

    if user_id in admins_group:
        await m.reply_text(text="This user is an admin, I cannot mute them!")
        return

    if m.reply_to_message and len(m.text.split()) >= 2:
        reason = m.text.split(None, 1)[1]
    elif not m.reply_to_message and len(m.text.split()) >= 3:
        reason = m.text.split(None, 2)[2]
    else:
        await m.reply_text("Read /help !!")
        return

    if not reason:
        await m.reply_text("You haven't specified a time to mute this user for!")
        return

    split_reason = reason.split(None, 1)
    time_val = split_reason[0].lower()
    reason = split_reason[1] if len(split_reason) > 1 else ""

    mutetime = await extract_time(m, time_val)

    if not mutetime:
        return
    try:
        await m.chat.restrict_member(
            user_id,
            ChatPermissions(),
            mutetime,
        )
        await m.reply_to_message.delete()
        if m.from_user:
            admin_name = m.from_user.first_name
            admin_id = m.from_user.id
            admin = await mention_html(admin_name, admin_id)
        else:
            admin = "**ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ.**"
        muted = await mention_html(user_first_name, user_id)
        txt = f"• <b>ᴍᴜᴛᴇ ᴇᴠᴇɴᴛ</b>\n• <b>ᴍᴜᴛᴇᴅ ʙʏ</b>: {admin}\n• <b>ᴜsᴇʀ</b>: {muted}"
        if reason:
            txt += f"\n<b>• ʀᴇᴀsᴏɴ</b>: {reason}"
        if mutetime:
            txt += f"\n<b>• ᴍᴜᴛᴇ ғᴏʀ</b>: {time_val}"
        try:
            await m.reply_text(
                text=txt,
            )
        except Exception:
            await m.reply_text(
                text=txt,
            )
    except ChatAdminRequired:
        await m.reply_text(text="I'm not admin or I don't have rights.")
    except RightForbidden:
        await m.reply_text(text="I don't have enough rights to ban this user.")
    except UserNotParticipant:
        await m.reply_text("How can I mute a user who is not a part of this chat?")
    except RPCError as ef:
        await m.reply_text(
            text=f"""Some error occured, report it using `/bug`

      <b>Error:</b> <code>{ef}</code>"""
        )
        LOGGER.error(ef)

    return


@Nikki.on_cmd("stmute", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_restrict_members", is_both=True)
async def stmute_usr(c: Nikki, m: Message):
    if len(m.text.split()) == 1 and not m.reply_to_message:
        await m.reply_text("I can't mute nothing!")
        return

    try:
        user_id, _, _ = await extract_user(c, m)
    except Exception:
        return

    if not user_id:
        await m.reply_text("Cannot find user to mute !")
        return
    if user_id == Nikki.id:
        await m.reply_text("Huh, why would I mute myself?")
        return

    try:
        admins_group = {i[0] for i in ADMIN_CACHE[m.chat.id]}
    except KeyError:
        admins_group = await admin_cache_reload(m, "mute")

    if user_id in admins_group:
        await m.reply_text(text="This user is an admin, I cannot mute them!")
        return

    if m.reply_to_message and len(m.text.split()) >= 2:
        reason = m.text.split(None, 1)[1]
    elif not m.reply_to_message and len(m.text.split()) >= 3:
        reason = m.text.split(None, 2)[2]
    else:
        await m.reply_text("Read /help !!")
        return

    if not reason:
        await m.reply_text("You haven't specified a time to mute this user for!")
        return

    split_reason = reason.split(None, 1)
    time_val = split_reason[0].lower()
    reason = split_reason[1] if len(split_reason) > 1 else ""

    mutetime = await extract_time(m, time_val)

    if not mutetime:
        return

    try:
        await m.chat.restrict_member(
            user_id,
            ChatPermissions(),
            mutetime,
        )
        await m.delete()
        if m.reply_to_message:
            await m.reply_to_message.delete()
    except ChatAdminRequired:
        await m.reply_text(text="I'm not admin or I don't have rights.")
    except RightForbidden:
        await m.reply_text(text="I don't have enough rights to ban this user.")
    except UserNotParticipant:
        await m.reply_text("How can I mute a user who is not a part of this chat?")
    except RPCError as ef:
        await m.reply_text(
            text=f"""Some error occured, report it using `/bug`

      <b>Error:</b> <code>{ef}</code>"""
        )
        LOGGER.error(ef)

    return


@Nikki.on_cmd("mute", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_restrict_members", is_both=True)
async def mute_usr(c: Nikki, m: Message):
    if len(m.text.split()) == 1 and not m.reply_to_message:
        await m.reply_text("I can't mute nothing!")
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
        await m.reply_text("Cannot find user to mute")
        return
    if user_id == Nikki.id:
        await m.reply_text("Huh, why would I mute myself?")
        return

    try:
        admins_group = {i[0] for i in ADMIN_CACHE[m.chat.id]}
    except KeyError:
        admins_group = await admin_cache_reload(m, "mute")

    if user_id in admins_group:
        await m.reply_text(text="This user is an admin, I cannot mute them!")
        return

    try:
        await m.chat.restrict_member(
            user_id,
            ChatPermissions(),
        )
        if m.from_user:
            admin_name = m.from_user.first_name
            admin_id = m.from_user.id
            admin = await mention_html(admin_name, admin_id)
        else:
            admin = "**ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ.**"
        muted = await mention_html(user_first_name, user_id)
        txt = f"• <b>ᴍᴜᴛᴇ ᴇᴠᴇɴᴛ</b>\n• <b>ᴍᴜᴛᴇᴅ ʙʏ</b>: {admin}\n• <b>ᴜsᴇʀ</b>: {muted}"
        if reason:
            txt += f"\n<b>• ʀᴇᴀsᴏɴ</b>: {reason}"
        try:
            await m.reply_text(
                reply_to_message_id=r_id,
                text=txt,
            )
        except Exception:
            await m.reply_text(
                reply_to_message_id=r_id,
                text=txt,
            )
    except ChatAdminRequired:
        await m.reply_text(text="I'm not admin or I don't have rights.")
    except RightForbidden:
        await m.reply_text(text="I don't have enough rights to ban this user.")
    except UserNotParticipant:
        await m.reply_text("How can I mute a user who is not a part of this chat?")
    except RPCError as ef:
        await m.reply_text(
            text=f"""Some error occured, report it using `/bug`

      <b>Error:</b> <code>{ef}</code>"""
        )
        LOGGER.error(ef)

    return


@Nikki.on_cmd("smute", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_restrict_members", is_both=True)
async def smute_usr(c: Nikki, m: Message):
    if len(m.text.split()) == 1 and not m.reply_to_message:
        await m.reply_text("I can't mute nothing!")
        return

    try:
        user_id, _, _ = await extract_user(c, m)
    except Exception:
        return

    if not user_id:
        await m.reply_text("Cannot find user to mute")
        return
    if user_id == Nikki.id:
        await m.reply_text("Huh, why would I mute myself?")
        return

    try:
        admins_group = {i[0] for i in ADMIN_CACHE[m.chat.id]}
    except KeyError:
        admins_group = await admin_cache_reload(m, "mute")

    if user_id in admins_group:
        await m.reply_text(text="This user is an admin, I cannot mute them!")
        return

    try:
        await m.chat.restrict_member(
            user_id,
            ChatPermissions(),
        )
        await m.delete()
        if m.reply_to_message:
            await m.reply_to_message.delete()
            return
        return
    except ChatAdminRequired:
        await m.reply_text(text="I'm not admin or I don't have rights.")
    except RightForbidden:
        await m.reply_text(text="I don't have enough rights to ban this user.")
    except UserNotParticipant:
        await m.reply_text("How can I mute a user who is not a part of this chat?")
    except RPCError as ef:
        await m.reply_text(
            text=f"""Some error occured, report it using `/bug`

      <b>Error:</b> <code>{ef}</code>"""
        )
        LOGGER.error(ef)

    return


@Nikki.on_cmd("dmute", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_restrict_members", is_both=True)
async def dmute_usr(c: Nikki, m: Message):
    if len(m.text.split()) == 1 and not m.reply_to_message:
        await m.reply_text("I can't mute nothing!")
        return
    if not m.reply_to_message:
        return await m.reply_text("No replied message and user to delete and mute!")

    reason = None
    if m.reply_to_message:
        if len(m.text.split()) >= 2:
            reason = m.text.split(None, 1)[1]
    else:
        if len(m.text.split()) >= 3:
            reason = m.text.split(None, 2)[2]
    user_id = m.reply_to_message.from_user.id
    user_first_name = m.reply_to_message.from_user.first_name

    if not user_id:
        await m.reply_text("Cannot find user to mute")
        return
    if user_id == Nikki.id:
        await m.reply_text("Huh, why would I mute myself?")
        return

    try:
        admins_group = {i[0] for i in ADMIN_CACHE[m.chat.id]}
    except KeyError:
        admins_group = await admin_cache_reload(m, "mute")

    if user_id in admins_group:
        await m.reply_text(text="This user is an admin, I cannot mute them!")
        return

    try:
        await m.chat.restrict_member(
            user_id,
            ChatPermissions(),
        )
        await m.reply_to_message.delete()
        if m.from_user:
            admin_name = m.from_user.first_name
            admin_id = m.from_user.id
            admin = await mention_html(admin_name, admin_id)
        else:
            admin = "**ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ.**"
        muted = await mention_html(user_first_name, user_id)
        txt = f"• <b>ᴍᴜᴛᴇ ᴇᴠᴇɴᴛ</b>\n• <b>ᴍᴜᴛᴇᴅ ʙʏ</b>: {admin}\n• <b>ᴜsᴇʀ</b>: {muted}"
        if reason:
            txt += f"\n<b>• ʀᴇᴀsᴏɴ</b>: {reason}"
        try:
            await m.reply_text(
                text=txt,
            )
        except Exception:
            await m.reply_text(
                text=txt,
            )
    except ChatAdminRequired:
        await m.reply_text(text="I'm not admin or I don't have rights.")
    except RightForbidden:
        await m.reply_text(text="I don't have enough rights to ban this user.")
    except UserNotParticipant:
        await m.reply_text("How can I mute a user who is not a part of this chat?")
    except RPCError as ef:
        await m.reply_text(
            text=f"""Some error occured, report it using `/bug`

      <b>Error:</b> <code>{ef}</code>"""
        )
        LOGGER.error(ef)

    return


@Nikki.on_cmd("unmute", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_restrict_members", is_both=True)
async def unmute_usr(c: Nikki, m: Message):
    if len(m.text.split()) == 1 and not m.reply_to_message:
        await m.reply_text("I can't unmute nothing!")
        return

    try:
        user_id, user_first_name, _ = await extract_user(c, m)
    except Exception:
        return

    if user_id == Nikki.id:
        await m.reply_text("Huh, why would I unmute myself if you are using me?")
        return
    try:
        statu = (await m.chat.get_member(user_id)).status
        if statu not in [enums.ChatMemberStatus.BANNED,enums.ChatMemberStatus.RESTRICTED]:
            await m.reply_text("User is not muted in this chat\nOr using this command as reply to his message")
            return
    except Exception as e:
        LOGGER.error(e)
        LOGGER.exception(format_exc())
    try:
        await m.chat.unban_member(user_id)
        if m.from_user:
            admin_name = m.from_user.first_name
            admin_id = m.from_user.id
            admin = await mention_html(admin_name, admin_id)
        else:
            admin = "**ᴀɴᴏɴʏᴍᴏᴜs ᴀᴅᴍɪɴ.**"
        unmuted = await mention_html(user_first_name, user_id)
        txt=f"• <b>ᴜɴᴍᴜᴛᴇ ᴇᴠᴇɴᴛ</b>\n• <b>ᴜɴᴍᴜᴛᴇᴅ ʙʏ</b>: {admin}\n• <b>ᴜsᴇʀ</b>: {unmuted}"
        await m.reply_text(
            text=txt,
       )
    except ChatAdminRequired:
        await m.reply_text(text="I'm not admin or I don't have rights.")
    except UserNotParticipant:
        await m.reply_text("How can I unmute a user who is not a part of this chat?")
    except RightForbidden:
        await m.reply_text(text="I don't have enough rights to ban this user.")
    except RPCError as ef:
        await m.reply_text(
            text=f"""Some error occured, report it using `/bug`

      <b>Error:</b> <code>{ef}</code>"""
        )
        LOGGER.error(ef)
    return

__PLUGIN__ = "Mᴜᴛɪɴɢ"

__alt_name__ = [
    "mute",
    "smute",
    "dmute",
    "tmute",
    "stmute",
    "dtmute",
    "unmute",
]

__HELP__ = """
**Dᴇsᴄʀɪᴘᴛɪᴏɴ :**
sᴏᴍᴇ ᴘᴇᴏᴘʟᴇ ɴᴇᴇᴅ ᴛᴏ ʙᴇ ᴘᴜʙʟɪᴄʟʏ ᴍᴜᴛᴇs; sᴘᴀᴍᴍᴇʀs, ᴀɴɴᴏʏᴀɴᴄᴇs, ᴏʀ ᴊᴜsᴛ ᴛʀᴏʟʟs.

ᴛʜɪs ᴍᴏᴅᴜʟᴇ ᴀʟʟᴏᴡs ʏᴏᴜ ᴛᴏ ᴅᴏ ᴛʜᴀᴛ ᴇᴀsɪʟʏ, ʙʏ ᴇxᴘᴏsɪɴɢ sᴏᴍᴇ ᴄᴏᴍᴍᴏɴ ᴀᴄᴋᴛɪᴏɴs, sᴏ ᴇᴠᴇʀʏᴏɴᴇ ᴡɪʟʟ sᴇᴇ!
────────────────────────

**Tʜᴇ Fᴏʟʟᴏᴡɪɴɢ Cᴏᴍᴍᴀɴᴅs Aʀᴇ Aᴅᴍɪɴ Oɴʟʏ :**
๏ /mute: ᴍᴜᴛᴇ ᴛʜᴇ ᴜsᴇʀ ʀᴇᴘʟɪᴇᴅ ᴛᴏ ᴏʀ ᴍᴇɴᴛɪᴏɴᴇᴅ.
๏ /smute: sɪʟᴇɴᴄᴇs ᴀ ᴜsᴇʀ ᴡɪᴛʜᴏᴜᴛ ɴᴏᴛɪғʏɪɴɢ. ᴄᴀɴ ᴀʟsᴏ ʙᴇ ᴜsᴇᴅ ᴀs ᴀ ʀᴇᴘʟʏ, ᴍᴜᴛɪɴɢ ᴛʜᴇ ʀᴇᴘʟɪᴇᴅ ᴛᴏ ᴜsᴇʀ.
๏ /dmute: ᴍᴜᴛᴇ ᴀ ᴜsᴇʀ ʙʏ ʀᴇᴘʟʏ, ᴀɴᴅ ᴅᴇʟᴇᴛᴇ ᴛʜᴇɪʀ ᴍᴇssᴀɢᴇ.
๏ /tmute ᴜsᴇʀʜᴀɴᴅʟᴇ x ᴛɪᴍᴇ: ᴍᴜᴛᴇs ᴀ ᴜsᴇʀ ғᴏʀ x ᴛɪᴍᴇ. 
๏ /stmute ᴜsᴇʀʜᴀɴᴅʟᴇ x ᴛɪᴍᴇ: ᴍᴜᴛᴇs ᴀ ᴜsᴇʀ ғᴏʀ x ᴛɪᴍᴇ ᴡɪᴛʜᴏᴜᴛ ɴᴏᴛɪғʏɪɴɢ. 
๏ /dtmute ᴜsᴇʀʜᴀɴᴅʟᴇ x ᴛɪᴍᴇ: ᴍᴜᴛᴇ ᴛʜᴇ ʀᴇᴘʟɪᴇᴅ ᴜsᴇʀ, ᴀɴᴅ ᴅᴇʟᴇᴛᴇ ᴛʜᴇ ʀᴇᴘʟɪᴇᴅ ᴍᴇssᴀɢᴇ.
๏ /unmute: ᴜɴᴍᴜᴛᴇs the ᴜsᴇʀ ᴍᴇɴᴛɪᴏɴᴇᴅ ᴏʀ ʀᴇᴘʟɪᴇᴅ ᴛᴏ."""
