from html import escape

from pyrogram import filters
from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.types import (CallbackQuery, InlineKeyboardButton,
                            InlineKeyboardMarkup, Message)

from Powers import HELP_COMMANDS
from Powers.bot_class import Nikki
from Powers.database.disable_db import Disabling


@Nikki.on_cmd("disable", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_change_info", is_both=True)
async def disableit(_, m: Message):
    if len(m.text.split()) < 2:
        return await m.reply_text("What to disable?")
    disable_cmd_keys = sorted(
        k
        for j in [HELP_COMMANDS[i]["disablable"] for i in list(HELP_COMMANDS.keys())]
        for k in j
    )

    db = Disabling(m.chat.id)
    disable_list = db.get_disabled()

    if str(m.text.split(None, 1)[1]) in disable_list:
        return await m.reply_text("It's already disabled!")

    if str((m.text.split(None, 1)[1]).lower()) in disable_cmd_keys:
        db.add_disable((str(m.text.split(None, 1)[1])).lower())
        await m.reply_text(f"Disabled {m.text.split(None, 1)[1]}!")
        return
    await m.reply_text("Can't do it sorry!")
    return


@Nikki.on_cmd("disabledel", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_change_info", is_both=True)
async def set_dsbl_action(_, m: Message):
    db = Disabling(m.chat.id)

    status = db.get_action()
    cur = status != "none"
    args = m.text.split(" ", 1)

    if len(args) >= 2:
        if args[1].lower() == "on":
            db.set_action("del")
            await m.reply_text("Oke done!")
        elif args[1].lower() == "off":
            db.set_action("none")
            await m.reply_text("Oke i will not delete!")
        else:
            await m.reply_text("what are you trying to do ??")
    else:
        await m.reply_text(f"Current settings:- {cur}")
    return


@Nikki.on_cmd("enable", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_change_info", is_both=True)
async def enableit(_, m: Message):
    if len(m.text.split()) < 2:
        return await m.reply_text("What to enable?")
    db = Disabling(m.chat.id)
    disable_list = db.get_disabled()
    if str(m.text.split(None, 1)[1]) not in disable_list:
        return await m.reply_text("It's not disabled!")
    db.remove_disabled((str(m.text.split(None, 1)[1])).lower())
    return await m.reply_text(f"Enabled {m.text.split(None, 1)[1]}!")


@Nikki.on_cmd("disableable", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_change_info", is_both=True)
async def disabling(_, m: Message):
    disable_cmd_keys = sorted(
        k
        for j in [HELP_COMMANDS[i]["disablable"] for i in list(HELP_COMMANDS.keys())]
        for k in j
    )
    tes = "List of commnds that can be disabled:\n" + "\n".join(
        f" • <code>{escape(i)}</code>" for i in disable_cmd_keys
    )
    return await m.reply_text(tes)


@Nikki.on_cmd("disabled", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_change_info", is_both=True)
async def disabled(_, m: Message):
    db = Disabling(m.chat.id)
    disable_list = db.get_disabled()
    if not disable_list:
        await m.reply_text("No disabled items!")
        return
    tex = "Disabled commands:\n" + "\n".join(
        f" • <code>{escape(i)}</code>" for i in disable_list
    )
    return await m.reply_text(tex)


@Nikki.on_cmd("enableall", group_only=True, self_admin=True)
@Nikki.adminsOnly(only_owner=True)
async def rm_alldisbl(_, m: Message):
    db = Disabling(m.chat.id)
    all_dsbl = db.get_disabled()
    if not all_dsbl:
        await m.reply_text("No disabled commands in this chat")
        return
    await m.reply_text(
        "Are you sure you want to enable all?",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Confirm",
                        callback_data="enableallcmds",
                    ),
                    InlineKeyboardButton("Cancel", callback_data="close_admin"),
                ],
            ],
        ),
    )
    return


@Nikki.on_cb("enableallcmds")
async def enablealll(_, q: CallbackQuery):
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
    db = Disabling(q.message.chat.id)
    db.rm_all_disabled()
    await q.message.edit_text("Enabled all!", show_alert=True)
    return


__PLUGIN__ = "Dɪsᴀʙʟᴇ"

__HELP__ = """
**Dᴇsᴄʀɪᴘᴛɪᴏɴ :**
ɴᴏᴛ ᴇᴠᴇʀʏᴏɴᴇ ᴡᴀɴᴛs ᴇᴠᴇʀʏ ғᴇᴀᴛᴜʀᴇ ᴛʜᴀᴛ ᴍᴇ ᴏғғᴇʀs. sᴏᴍᴇ ᴄᴏᴍᴍᴀɴᴅs ᴀʀᴇ ʙᴇsᴛ ʟᴇғᴛ ᴜɴᴜsᴇᴅ; ᴛᴏ ᴀᴠᴏɪᴅ sᴘᴀᴍ ᴀɴᴅ ᴀʙᴜsᴇ.

ᴛʜɪs ᴀʟʟᴏᴡs ʏᴏᴜ ᴛᴏ ᴅɪsᴀʙʟᴇ sᴏᴍᴇ ᴄᴏᴍᴍᴏɴʟʏ ᴜsᴇᴅ ᴄᴏᴍᴍᴀɴᴅs, sᴏ ɴᴏ one ᴄᴀɴ ᴜsᴇ ᴛʜᴇᴍ. ɪᴛ'ʟʟ ᴀʟsᴏ ᴀʟʟᴏᴡ ʏᴏᴜ ᴛᴏ ᴀᴜᴛᴏᴅᴇʟᴇᴛᴇ ᴛʜᴇᴍ, sᴛᴏᴘᴘɪɴɢ ᴘᴇᴏᴘʟᴇ ғʀᴏᴍ ʙʟᴜᴇᴛᴇxᴛɪɴɢ.
────────────────────────

**Usᴇʀ Cᴏᴍᴍᴀɴᴅs :**
๏ /disabled: ʟɪsᴛ ᴛʜᴇ ᴅɪsᴀʙʟᴇᴅ ᴄᴏᴍᴍᴀɴᴅs ɪɴ ᴛʜɪs ᴄʜᴀᴛ.

**Tʜᴇ Fᴏʟʟᴏᴡɪɴɢ Cᴏᴍᴍᴀɴᴅs Aʀᴇ Aᴅᴍɪɴ Oɴʟʏ :**
๏ /disable ᴄᴏᴍᴍᴀɴᴅ ɴᴀᴍᴇ: sᴛᴏᴘ ᴜsᴇʀs ғʀᴏᴍ ᴜsɪɴɢ "ᴄᴏᴍᴍᴀɴᴅ-ɴᴀᴍᴇ" ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.
๏ /enable ɪᴛᴇᴍ ɴᴀᴍᴇ: ᴀʟʟᴏᴡ ᴜsᴇʀs ғʀᴏᴍ ᴜsɪɴɢ "ᴄᴏᴍᴍᴀɴᴅ-ɴᴀᴍᴇ" ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.
๏ /disabledel <ʏᴇs/ɴᴏ/ᴏɴ/ᴏғғ>: ᴅᴇʟᴇᴛᴇ ᴅɪsᴀʙʟᴇᴅ ᴄᴏᴍᴍᴀɴᴅs ᴡʜᴇɴ ᴜsᴇᴅ ʙʏ ɴᴏɴ-ᴀᴅᴍɪɴs.
๏ /disableable: ʟɪsᴛ ᴀʟʟ ᴅɪsᴀʙʟᴇᴀʙʟᴇ ᴄᴏᴍᴍᴀɴᴅs."""
