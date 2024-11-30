from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.errors import PeerIdInvalid, RPCError, UserNotParticipant
from pyrogram.types import CallbackQuery, Message

from Powers import LOGGER, SUPPORT_GROUP
from Powers.bot_class import Nikki
from Powers.database.approve_db import Approve
from Powers.utils.extract_user import extract_user
from Powers.utils.kbhelpers import ikb
from Powers.utils.parser import mention_html


@Nikki.on_cmd("approve", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_change_info", is_user=True)
async def approve_user(c: Nikki, m: Message):
    db = Approve(m.chat.id)

    chat_title = m.chat.title

    try:
        user_id, user_first_name, _ = await extract_user(c, m)
    except Exception:
        return

    if not user_id:
        await m.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!",
        )
        return
    try:
        member = await m.chat.get_member(user_id)
    except UserNotParticipant:
        await m.reply_text("This user is not in this chat!")
        return

    except RPCError as ef:
        await m.reply_text(
            f"<b>Error</b>: <code>{ef}</code>\nReport it to @{SUPPORT_GROUP}",
        )
        return
    if member.status in (CMS.ADMINISTRATOR, CMS.OWNER):
        await m.reply_text(
            "User is already admin - blacklists and locks already don't apply to them.",
        )
        return
    already_approved = db.check_approve(user_id)
    if already_approved:
        await m.reply_text(
            f"{(await mention_html(user_first_name, user_id))} is already approved in {chat_title}",
        )
        return
    db.add_approve(user_id, user_first_name)
    try:
        await m.chat.unban_member(user_id=user_id)
    except RPCError as g:
        await m.reply_text(f"Error: {g}")
        return
    await m.reply_text(
        (
            f"{(await mention_html(user_first_name, user_id))} has been approved in {chat_title}!\n"
            "They will now be ignored by blacklists, locks and antiflood!"
        ),
    )
    return

@Nikki.on_cmd(["disapprove", "unapprove"], group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_change_info", is_user=True)
async def disapprove_user(c: Nikki, m: Message):
    db = Approve(m.chat.id)

    chat_title = m.chat.title
    try:
        user_id, user_first_name, _ = await extract_user(c, m)
    except Exception:
        return
    already_approved = db.check_approve(user_id)
    if not user_id:
        await m.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!",
        )
        return
    try:
        member = await m.chat.get_member(user_id)
    except UserNotParticipant:
        if already_approved:  # If user is approved and not in chat, unapprove them.
            db.remove_approve(user_id)
            LOGGER.info(f"{user_id} disapproved in {m.chat.id} as UserNotParticipant")
        await m.reply_text("This user is not in this chat, unapproved them.")
        return
    except RPCError as ef:
        await m.reply_text(
            f"<b>Error</b>: <code>{ef}</code>\nReport it to @{SUPPORT_GROUP}",
        )
        return

    if member.status in (CMS.OWNER, CMS.ADMINISTRATOR):
        await m.reply_text("This user is an admin, they can't be disapproved.")
        return

    if not already_approved:
        await m.reply_text(
            f"{(await mention_html(user_first_name, user_id))} isn't approved yet!",
        )
        return

    db.remove_approve(user_id)
    LOGGER.info(f"{user_id} disapproved by {m.from_user.id} in {m.chat.id}")

    # Set permission same as of current user by fetching them from chat!
    await m.chat.restrict_member(
        user_id=user_id,
        permissions=m.chat.permissions,
    )

    await m.reply_text(
        f"{(await mention_html(user_first_name, user_id))} is no longer approved in {chat_title}.",
    )
    return

@Nikki.on_cmd("approved", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_change_info", is_user=True)
async def check_approved(_, m: Message):
    db = Approve(m.chat.id)

    chat = m.chat
    chat_title = chat.title
    msg = "The following users are approved:\n"
    approved_people = db.list_approved()

    if not approved_people:
        await m.reply_text(f"No users are approved in {chat_title}.")
        return

    for user_id, user_name in approved_people:
        try:
            await chat.get_member(user_id)  # Check if user is in chat or not
        except UserNotParticipant:
            db.remove_approve(user_id)
            continue
        except PeerIdInvalid:
            pass
        msg += f"- `{user_id}`: {user_name}\n"
    await m.reply_text(msg)
    LOGGER.info(f"{m.from_user.id} checking approved users in {m.chat.id}")
    return


@Nikki.on_cmd("approval", group_only=True)
async def check_approval(c: Nikki, m: Message):
    db = Approve(m.chat.id)

    try:
        user_id, user_first_name, _ = await extract_user(c, m)
    except Exception:
        return
    check_approve = db.check_approve(user_id)

    if not user_id:
        await m.reply_text(
            "I don't know who you're talking about, you're going to need to specify a user!",
        )
        return
    if check_approve:
        await m.reply_text(
            f"{(await mention_html(user_first_name, user_id))} is an approved user. Locks, antiflood, and blacklists won't apply to them.",
        )
    else:
        await m.reply_text(
            f"{(await mention_html(user_first_name, user_id))} is not an approved user. They are affected by normal commands.",
        )
    return


@Nikki.on_cmd("unapproveall", group_only=True, self_admin=True)
@Nikki.adminsOnly(only_owner=True)
async def unapproveall_users(_, m: Message):
    db = Approve(m.chat.id)
    all_approved = db.list_approved()
    if not all_approved:
        await m.reply_text("No one is approved in this chat.")
        return
    await m.reply_text(
        "Are you sure you want to remove everyone who is approved in this chat?",
        reply_markup=ikb(
            [[("Confirm", "unapprove_all"), ("Cancel!", "close_admin")]],
        ),
    )
    return


@Nikki.on_cb("unapprove_all")
async def unapproveall_callback(_, q: CallbackQuery):
    user_id = q.from_user.id
    db = Approve(q.message.chat.id)
    approved_people = db.list_approved()
    user_status = (await q.message.chat.get_member(user_id)).status
    if user_status not in {CMS.OWNER, CMS.ADMINISTRATOR}:
        await q.answer(
            "You need to be an admin to do this.",
            show_alert=True,
        )
        return
    if user_status != CMS.OWNER:
        await q.answer(
            f"You need to be the chat owner of {q.message.chat.title} to do this.",
            show_alert=True,
        )
        return
    db.unapprove_all()
    for i in approved_people:
        await q.message.chat.restrict_member(
            user_id=i[0],
            permissions=q.message.chat.permissions,
        )
    await q.message.delete()
    await q.answer("Disapproved all users!", show_alert=True)
    return

__PLUGIN__ = "Aᴘᴘʀᴏᴠᴇ"

_DISABLE_CMDS_ = ["approval"]

__alt_name__ = [
    "approved",
    "approve",
    "unapprove",
    "disapprove",
    "unapproveall",
    "approval",
]

__HELP__ = """
**Dᴇsᴄʀɪᴘᴛɪᴏɴ :**
sᴏᴍᴇᴛɪᴍᴇs, ʏᴏᴜ ᴍɪɢʜᴛ ᴛʀᴜsᴛ ᴀ ᴜsᴇʀ ɴᴏᴛ ᴛᴏ sᴇɴᴅ ᴜɴᴡᴀɴᴛᴇᴅ ᴄᴏɴᴛᴇɴᴛ.
ᴍᴀʏʙᴇ ɴᴏᴛ ᴇɴᴏᴜɢʜ ᴛᴏ ᴍᴀᴋᴇ ᴛʜᴇᴍ ᴀᴅᴍɪɴ, ʙᴜᴛ ʏᴏᴜ ᴍɪɢʜᴛ be ᴏᴋ ᴡɪᴛʜ ʟᴏᴄᴋs, ʙʟᴏᴄᴋʟɪsᴛs, ᴀɴᴅ ᴀɴᴛɪғʟᴏᴏᴅ ɴᴏᴛ ᴀᴘᴘʟʏɪɴɢ ᴛᴏ ᴛʜᴇᴍ.

ᴛʜᴀᴛ's ᴡʜᴀᴛ ᴀᴘᴘʀᴏᴠᴀʟs ᴀʀᴇ ғᴏʀ - ᴀᴘᴘʀᴏᴠᴇ ᴏғ ᴛʀᴜsᴛ ᴡᴏʀᴛʜʏ ᴜsᴇʀs ᴛᴏ ᴀʟʟᴏᴡ ᴛʜᴇᴍ ᴛᴏ sᴇɴᴅ 
────────────────────────

**Cᴏᴍᴍᴀɴᴅs :**
๏ /approval: ᴄʜᴇᴄᴋ ᴀ ᴜsᴇʀ ᴀᴘᴘʀᴏᴠᴀʟ sᴛᴀᴛᴜs ɪɴ ᴛʜɪs ᴄʜᴀᴛ.

**Tʜᴇ Fᴏʟʟᴏᴡɪɴɢ Cᴏᴍᴍᴀɴᴅs Aʀᴇ Aᴅᴍɪɴ Oɴʟʏ :**
๏ /approve : ᴀᴘᴘʀᴏᴠᴇ ᴏғ ᴀ ᴜsᴇʀ. ʟᴏᴄᴋs, ʙʟᴀᴄᴋʟɪsᴛs, ᴀɴᴅ ᴀɴᴛɪғʟᴏᴏᴅ ᴡᴏɴ'ᴛ ᴀᴘᴘʟʏ ᴛᴏ ᴛʜᴇᴍ ᴀɴʏᴍᴏʀᴇ.
๏ /unapprove : ᴜɴᴀᴘᴘʀᴏᴠᴇ ᴏғ ᴀ ᴜsᴇʀ ᴛʜᴇʏ ᴡɪʟʟ ɴᴏᴡ ʙᴇ sᴜʙᴊᴇᴄᴛ ᴛᴏ ʟᴏᴄᴋs, ʙʟᴏᴄᴋʟɪsᴛs, ᴀɴᴅ ᴀɴᴛɪғʟᴏᴏᴅ ᴀɢᴀɪɴ.
๏ /approved : ʟɪsᴛ ᴀʟʟ ᴀᴘᴘʀᴏᴠᴇᴅ ᴜsᴇʀs.
๏ /unapproveall : ᴜɴᴀᴘᴘʀᴏᴠᴇ ᴀʟʟ ᴜsᴇʀs ɪɴ ᴀ ᴄʜᴀᴛ. ᴛʜɪs ᴄᴀɴɴᴏᴛ ʙᴇ ᴜɴᴅᴏɴᴇ."""
