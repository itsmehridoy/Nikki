from html import escape as escape_html

from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.errors import ChatAdminRequired, RightForbidden, RPCError
from pyrogram.filters import regex
from pyrogram.types import CallbackQuery, Message

from Powers import LOGGER, SUPPORT_GROUP
from Powers.bot_class import Nikki
from Powers.database.pins_db import Pins
from Powers.utils.kbhelpers import ikb
from Powers.utils.string import build_keyboard, parse_button


@Nikki.on_cmd("pin", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_pin_messages", is_both=True)
async def pin_message(Nikki, m: Message):
    pin_args = m.text.split(None, 1)
    if m.reply_to_message:
        try:
            disable_notification = True

            if len(pin_args) >= 2 and pin_args[1] in ["alert", "notify", "loud"]:
                disable_notification = False

            if m.chat:
                chat_id = m.chat.id
                link_chat_id = m.chat.username if m.chat.username else str(chat_id).replace("-100", "")
                message_link = f"https://t.me/{link_chat_id}/{m.reply_to_message.id}"

                await m.reply_to_message.pin(disable_notification=disable_notification)

                await m.reply_text(
                    text=f"I have Pinned {'and Notified ' if not disable_notification else ''}[this message]({message_link})!",
                    disable_web_page_preview=True,
                )
            else:
                await m.reply_text("Chat information is not available.")
        except ChatAdminRequired:
            await m.reply_text(text="I'm not an admin or I don't have rights.")
        except RightForbidden:
            await m.reply_text(text="I don't have enough rights to pin messages.")
        except RPCError as ef:
            await m.reply_text(
                text=f"""Some error occurred, report to @{SUPPORT_GROUP}

      <b>Error:</b> <code>{ef}</code>"""
            )
            LOGGER.error(ef)
    else:
        await m.reply_text("Reply to a message to pin it!")

@Nikki.on_cmd("spin", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_pin_messages", is_both=True)
async def silent_pin_message(Nikki, m: Message):
    pin_args = m.text.split(None, 1)
    if m.reply_to_message:
        try:
            await m.reply_to_message.pin(disable_notification=True)  # Pin silently
            
        except ChatAdminRequired:
            await m.reply_text(text="I'm not an admin or I don't have rights.")
        except RightForbidden:
            await m.reply_text(text="I don't have enough rights to pin messages.")
        except RPCError as ef:
            await m.reply_text(
                text=f"""Some error occurred, report to @{SUPPORT_GROUP}

      <b>Error:</b> <code>{ef}</code>"""
            )
            LOGGER.error(ef)
    else:
        await m.reply_text("Reply to a message to pin it!")

    return

@Nikki.on_cmd("unpin", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_pin_messages", is_both=True)
async def unpin_message(c: Nikki, m: Message):
    try:
        if m.reply_to_message:
            await m.reply_to_message.unpin()
            LOGGER.info(
                f"{m.from_user.id} unpinned msgid: {m.reply_to_message.id} in {m.chat.id}",
            )
            await m.reply_text(text="Unpinned last message.")
        else:
            m_id = (await c.get_chat(m.chat.id)).pinned_message.id
            await c.unpin_chat_message(m.chat.id,m_id)
            await m.reply_text(text="Unpinned last pinned message!")
    except ChatAdminRequired:
        await m.reply_text(text="I'm not admin or I don't have rights.")
    except RightForbidden:
        await m.reply_text(text="I don't have enough rights to unpin messages.")
    except RPCError as ef:
        await m.reply_text(
            text=f"""Some error occured, report it using `/bug`

      <b>Error:</b> <code>{ef}</code>"""
        )
        LOGGER.error(ef)

    return

@Nikki.on_cmd("unpinall", group_only=True, self_admin=True)
@Nikki.adminsOnly(only_owner=True)
async def unpinall_message(_, m: Message):
    await m.reply_text(
        "Do you really want to unpin all messages in this chat?",
        reply_markup=ikb([[("Yes", "unpin_all_in_this_chat"), ("No", "close_admin")]]),
    )
    return


@Nikki.on_cb("unpin_all_in_this_chat")
async def unpinall_calllback(c: Nikki, q: CallbackQuery):
    user_id = q.from_user.id
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
    try:
        await c.unpin_all_chat_messages(q.message.chat.id)
        await q.message.edit_text(text="Unpinned all messages in this chat.")
    except ChatAdminRequired:
        await q.message.edit_text(text="I'm not admin or I don't have rights.")
    except RightForbidden:
        await q.message.edit_text(text="I don't have enough rights to unpin messages.")
    except RPCError as ef:
        await q.message.edit_text(
            text=f"""Some error occured, report to @{SUPPORT_GROUP}

      <b>Error:</b> <code>{ef}</code>"""
        )
        LOGGER.error(ef)
    return


@Nikki.on_cmd("antichannelpin", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_change_info", is_both=True)
async def anti_channel_pin(_, m: Message):
    pinsdb = Pins(m.chat.id)

    if len(m.text.split()) == 1:
        status = pinsdb.get_settings()["antichannelpin"]
        await m.reply_text(text=f"Current AntiChannelPin status: {status}")
        return

    if len(m.text.split()) == 2:
        if m.command[1] in ("yes", "on", "true"):
            pinsdb.antichannelpin_on()
            LOGGER.info(f"{m.from_user.id} enabled antichannelpin in {m.chat.id}")
            msg = "Turned on AntiChannelPin, now all message pinned by channel will be unpinned automtically!"
        elif m.command[1] in ("no", "off", "false"):
            pinsdb.antichannelpin_off()
            LOGGER.info(f"{m.from_user.id} disabled antichannelpin in {m.chat.id}")
            msg = "Turned off AntiChannelPin, now all message pinned by channel will stay pinned!"
        else:
            await m.reply_text(
                text="Please check help on how to use this this command."
            )
            return

    await m.reply_text(msg)
    return


@Nikki.on_cmd("pinned", group_only=True, self_admin=True)
async def pinned_message(c: Nikki, m: Message):
    chat_title = m.chat.title
    chat = await c.get_chat(chat_id=m.chat.id)
    msg_id = m.reply_to_message.id if m.reply_to_message else m.id

    if chat.pinned_message:
        pinned_id = chat.pinned_message.id
        if m.chat.username:
            link_chat_id = m.chat.username
            message_link = f"https://t.me/{link_chat_id}/{pinned_id}"
        elif (str(m.chat.id)).startswith("-100"):
            link_chat_id = (str(m.chat.id)).replace("-100", "")
            message_link = f"https://t.me/c/{link_chat_id}/{pinned_id}"

        await m.reply_text(
            f"The pinned message of {escape_html(chat_title)} is [here]({message_link}).",
            reply_to_message_id=msg_id,
            disable_web_page_preview=True,
        )
    else:
        await m.reply_text(f"There is no pinned message in {escape_html(chat_title)}.")


@Nikki.on_cmd("cleanlinked", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_change_info", is_both=True)
async def clean_linked(_, m: Message):
    pinsdb = Pins(m.chat.id)

    if len(m.text.split()) == 1:
        status = pinsdb.get_settings()["cleanlinked"]
        await m.reply_text(text=f"Current AntiChannelPin status: {status}")
        return

    if len(m.text.split()) == 2:
        if m.command[1] in ("yes", "on", "true"):
            pinsdb.cleanlinked_on()
            LOGGER.info(f"{m.from_user.id} enabled CleanLinked in {m.chat.id}")
            msg = "Turned on CleanLinked! Now all the messages from linked channel will be deleted!"
        elif m.command[1] in ("no", "off", "false"):
            pinsdb.cleanlinked_off()
            LOGGER.info(f"{m.from_user.id} disabled CleanLinked in {m.chat.id}")
            msg = "Turned off CleanLinked! Messages from linked channel will not be deleted!"
        else:
            await m.reply_text(
                text="Please check help on how to use this this command."
            )
            return

    await m.reply_text(msg)
    return


@Nikki.on_cmd("permapin", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_pin_messages", is_both=True)
async def perma_pin(_, m: Message):
    if m.reply_to_message or len(m.text.split()) > 1:
        LOGGER.info(f"{m.from_user.id} used permampin in {m.chat.id}")
        if m.reply_to_message:
            text = m.reply_to_message.text
        elif len(m.text.split()) > 1:
            text = m.text.split(None, 1)[1]
        teks, button = await parse_button(text)
        button = await build_keyboard(button)
        button = ikb(button) if button else None
        z = await m.reply_text(teks, reply_markup=button)
        await z.pin()
    else:
        await m.reply_text("Reply to a message or enter text to pin it.")
    await m.delete()
    return


__PLUGIN__ = "Pɪɴs"

__alt_name__ = [
    "pin",
    "spin"
    "unpin", 
    "unpinall", 
    "antichannelpin",
    "pinned"
    "cleanlinked"
    "permapin",
]

__HELP__ = """
**Dᴇsᴄʀɪᴘᴛɪᴏɴ :**
ᴀʟʟ ᴛʜᴇ ᴘɪɴ ʀᴇʟᴀᴛᴇᴅ ᴄᴏᴍᴍᴀɴᴅs ᴄᴀɴ ʙᴇ ғᴏᴜɴᴅ ʜᴇʀᴇ; ᴋᴇᴇᴘ ʏᴏᴜʀ ᴄʜᴀᴛ ᴜᴘ ᴛᴏ ᴅᴀᴛᴇ ᴏɴ ᴛʜᴇ ʟᴀᴛᴇsᴛ ɴᴇᴡs ᴡɪᴛʜ ᴀ sɪᴍᴘʟᴇ ᴘɪɴɴᴇᴅ ᴍᴇssᴀɢᴇ!

────────────────────────

**Usᴇʀ Cᴏᴍᴍᴀɴᴅs:**
๏ /pinned: ɢᴇᴛ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴘɪɴɴᴇᴅ ᴍᴇssᴀɢᴇ.

**Tʜᴇ Fᴏʟʟᴏᴡɪɴɢ Cᴏᴍᴍᴀɴᴅs Aʀᴇ Aᴅᴍɪɴ Oɴʟʏ :**
๏ /pin: sɪʟᴇɴᴛʟʏ ᴘɪɴs ᴛʜᴇ ᴍᴇssᴀɢᴇ ʀᴇᴘʟɪᴇᴅ ᴛᴏ - ᴀᴅᴅ loud, notify ᴏʀ alert ᴛᴏ ɢɪᴠᴇ ɴᴏᴛɪғɪᴄᴀᴛᴏɴ ᴛᴏ ᴜsᴇʀs.
๏ /spin: sᴀᴍᴇ ᴀs `/pin` ʙᴜᴛ sɪʟᴇɴᴛʟʏ
๏ /unpin: ᴜɴᴘɪɴs ᴛʜᴇ ʟᴀsᴛ ᴘɪɴɴᴇᴅ ᴍᴇssᴀɢᴇ.
๏ /unpinall: ᴜɴᴘɪɴs ᴀʟʟ ᴛʜᴇ ᴘɪɴɴᴇᴅ ᴍᴇssᴀɢᴇ ɪɴ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴄʜᴀᴛ.
๏ /antichannelpin ᴏɴ/ᴏғғ/ʏᴇs/ɴᴏ: ᴛᴏɢɢʟᴇ ᴀɴᴛɪ-ᴄʜᴀɴɴᴇʟ-ᴘɪɴ sᴛᴀᴛᴜs. ᴀʟʟ ᴛʜᴇ ᴍᴇssᴀɢᴇs ғʀᴏᴍ ʟɪɴᴋᴇᴅ ᴄʜᴀɴɴᴇʟ ᴡɪʟʟ ʙᴇ ᴜɴᴘɪɴɴᴇᴅ ɪғ ᴇɴᴀʙʟᴇᴅ!
๏ /cleanlinked ᴏɴ/ᴏғғ/ʏᴇs/ɴᴏ: ᴛᴏɢɢʟᴇ ᴄʟᴇᴀɴʟɪɴᴋᴇᴅ sᴛᴀᴛᴜs. ᴀʟʟ ᴛʜᴇ ᴍᴇssᴀɢᴇs ғʀᴏᴍ ʟɪɴᴋᴇᴅ ᴄʜᴀɴɴᴇʟ ᴡɪʟʟ be ᴅᴇʟᴇᴛᴇᴅ ɪғ ᴇɴᴀʙʟᴇᴅ
๏ /permapin ᴛᴇxᴛ: ᴘɪɴ ᴀ ᴄᴜsᴛᴏᴍ ᴍᴇssᴀɢᴇs ᴠɪᴀ ʙᴏᴛ. ᴛʜɪs ᴍᴇssᴀɢᴇ ᴄᴀɴ ᴄᴏɴᴛᴀɪɴ ᴍᴀʀᴋᴅᴏᴡɴ, ᴀɴᴅ ᴄᴀɴ ʙᴇ ᴜsᴇᴅ in ʀᴇᴘʟɪᴇs ᴛᴏ ᴛʜᴇ ᴍᴇᴅɪᴀ ɪɴᴄʟᴜᴅᴇ ᴀᴅᴅɪᴛɪᴏɴᴀʟ ʙᴜᴛᴛᴏɴs ᴀɴᴅ ᴛᴇxᴛ."""
