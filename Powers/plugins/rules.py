from pyrogram import filters
from pyrogram.types import CallbackQuery, Message

from Powers.bot_class import Nikki
from Powers.database.rules_db import Rules
from Powers.utils.custom_filters import admin_filter, command
from Powers.utils.kbhelpers import ikb
from Powers.utils.string import build_keyboard, parse_button


@Nikki.on_cmd("rules", group_only=True)
async def get_rules(_, m: Message):
    db = Rules(m.chat.id)
    msg_id = m.reply_to_message.id if m.reply_to_message else m.id

    rules = db.get_rules()
    if m and not m.from_user:
        return

    if not rules:
        await m.reply_text(
            text="ᴛʜᴇ ᴀᴅᴍɪɴs ғᴏʀ ᴛʜɪs group ʜᴀᴠᴇ ɴᴏᴛ sᴇᴛᴜᴘ ʀᴜʟᴇs! ᴛʜᴀᴛ ᴅᴏᴇsɴ's ᴍᴇᴀɴ ʏᴏᴜ ᴄᴀɴ ʙʀᴇᴀᴋ ᴛʜᴇ ᴅᴇᴄᴏʀᴜᴍ ᴏғ ᴛʜɪs ɢʀᴏᴜᴘ\n\nʀᴜʟᴇs ʙʏ ᴍᴇ\n➤Rᴇsᴘᴇᴄᴛ ᴇᴠᴇʀʏʙᴏᴅʏ\n➤ Dᴏɴ'ᴛ ᴘᴍ ᴏʀ ᴅᴍ ᴡɪᴛʜᴏᴜᴛ ʜɪs/ʜᴇʀ ᴘᴇʀᴍɪssɪᴏɴ\n➤ Dᴏɴ'ᴛ sᴀʏ ᴀʙᴜsᴇ ʟᴀɴɢᴜᴀɢᴇ!",
            quote=True,
        )
        return

    if priv_rules_status := db.get_privrules():
        pm_kb = ikb(
            [
                [
                    (
                        "ʀᴜʟᴇs",
                        f"https://t.me/{Nikki.username}?start=rules_{m.chat.id}",
                        "url",
                    ),
                ],
            ],
        )
        await m.reply_text(
            text="Click on the below button to see this group rules!",
            quote=True,
            reply_markup=pm_kb,
            reply_to_message_id=msg_id,
        )
        return

    formated = rules
    teks, button = await parse_button(formated)
    button = await build_keyboard(button)
    button = ikb(button) if button else None
    textt = teks
    await m.reply_text(
        text=f"""ᴛʜᴇ ʀᴜʟᴇs ғᴏʀ <b>{m.chat.title} ᴀʀᴇ:</b>\n
{textt}""",
        disable_web_page_preview=True,
        reply_to_message_id=msg_id,
        reply_markup=button
    )
    return


@Nikki.on_cmd("setrules", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_change_info", is_both=True)
async def set_rules(_, m: Message):
    db = Rules(m.chat.id)
    if m and not m.from_user:
        return

    if m.reply_to_message and m.reply_to_message.text:
        rules = m.reply_to_message.text.markdown
    elif (not m.reply_to_message) and len(m.text.split()) >= 2:
        rules = m.text.split(None, 1)[1]
    else:
        return await m.reply_text("Provide some text to set as rules !!")

    if len(rules) > 4000:
        rules = rules[:3949]
        await m.reply_text("Rules are truncated to 3950 characters!")

    db.set_rules(rules)
    await m.reply_text(text="Successfully set rules for this group.")
    return


@Nikki.on_cmd(["pmrules", "privaterules"], group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_change_info", is_both=True)
async def priv_rules(_, m: Message):
    db = Rules(m.chat.id)
    if m and not m.from_user:
        return

    if len(m.text.split()) == 2:
        option = (m.text.split())[1]
        if option in ("on", "yes"):
            db.set_privrules(True)
            msg = f"Private Rules have been turned <b>on</b> for chat <b>{m.chat.title}</b>"
        elif option in ("off", "no"):
            db.set_privrules(False)
            msg = f"Private Rules have been turned <b>off</b> for chat <b>{m.chat.title}</b>"
        else:
            msg = "Option not valid, choose from <code>on</code>, <code>yes</code>, <code>off</code>, <code>no</code>"
        await m.reply_text(msg)
    elif len(m.text.split()) == 1:
        curr_pref = db.get_privrules()
        msg = (
            f"Current Preference for Private rules in this chat is: <b>{curr_pref}</b>"
        )
        await m.reply_text(msg)
    else:
        await m.reply_text(text="Please check help on how to use this this command.")

    return


@Nikki.on_cmd("clearrules", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_change_info", is_both=True)
async def clear_rules(_, m: Message):
    db = Rules(m.chat.id)
    if m and not m.from_user:
        return

    rules = db.get_rules()
    if not rules:
        await m.reply_text(
            text="ᴛʜᴇ ᴀᴅᴍɪɴs ғᴏʀ ᴛʜɪs group ʜᴀᴠᴇ ɴᴏᴛ sᴇᴛᴜᴘ ʀᴜʟᴇs! ᴛʜᴀᴛ ᴅᴏᴇsɴ's ᴍᴇᴀɴ ʏᴏᴜ ᴄᴀɴ ʙʀᴇᴀᴋ ᴛʜᴇ ᴅᴇᴄᴏʀᴜᴍ ᴏғ ᴛʜɪs ɢʀᴏᴜᴘ\n\nʀᴜʟᴇs ʙʏ ᴍᴇ\n➤Rᴇsᴘᴇᴄᴛ ᴇᴠᴇʀʏʙᴏᴅʏ\n➤ Dᴏɴ'ᴛ ᴘᴍ ᴏʀ ᴅᴍ ᴡɪᴛʜᴏᴜᴛ ʜɪs/ʜᴇʀ ᴘᴇʀᴍɪssɪᴏɴ\n➤ Dᴏɴ'ᴛ sᴀʏ ᴀʙᴜsᴇ ʟᴀɴɢᴜᴀɢᴇ!"
        )
        return

    await m.reply_text(
        text="Are you sure you want to clear rules?",
        reply_markup=ikb(
            [[("ᴄᴏɴғɪʀᴍ", "clear_rules"), ("ᴄᴀɴᴄᴇʟ ❌", "close_admin")]],
        ),
    )
    return


@Nikki.on_cb("clear_rules")
async def clearrules_callback(_, q: CallbackQuery):
    Rules(q.message.chat.id).clear_rules()
    await q.message.edit_text(text="Successfully cleared rules for this group!")
    await q.answer("Rules for the chat have been cleared!", show_alert=True)
    return


__PLUGIN__ = "Rᴜʟᴇs"

__alt_name__ = ["setrules", "rules", "clearrules"]

__buttons__ = [
    [
        ("Fᴏʀᴍᴀᴛᴛɪɴɢ", "formatting.md_formatting")],
]

__HELP__ = """
**Dᴇsᴄʀɪᴘᴛɪᴏɴ :**

ᴇᴠᴇʀʏ ᴄʜᴀᴛ ᴡᴏʀᴋs ᴡɪᴛʜ ᴅɪғғᴇʀᴇɴᴛ ʀᴜʟᴇs; ᴛʜɪs ᴍᴏᴅᴜʟᴇ ᴡɪʟʟ ʜᴇʟᴘ ᴍᴀᴋᴇ ᴛʜᴏsᴇ ʀᴜʟᴇs ᴄʟᴇᴀʀᴇʀ!
────────────────────────
**Usᴇʀ Cᴏᴍᴍᴀɴᴅs :**
๏ /rules: ᴄʜᴇᴄᴋ ᴛʜᴇ ᴄᴜʀʀᴇɴᴛ ᴄʜᴀᴛ ʀᴜʟᴇs.

**Tʜᴇ Fᴏʟʟᴏᴡɪɴɢ Cᴏᴍᴍᴀɴᴅs Aʀᴇ Aᴅᴍɪɴ Oɴʟʏ :**
๏ /setrules ᴛᴇxᴛ: sᴇᴛ ᴛʜᴇ ʀᴜʟᴇs ғᴏʀ ᴛʜɪs ᴄʜᴀᴛ. sᴜᴘᴘᴏʀᴛs ᴍᴀʀᴋᴅᴏᴡɴ, ʙᴜᴛᴛᴏɴs, ғɪʟʟɪɴɢs, ᴇᴛᴄ.
๏ /privaterules ʏᴇs/ɴᴏ/ᴏɴ/ᴏғғ: ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ ᴡʜᴇᴛʜᴇʀ ᴛʜᴇ ʀᴜʟᴇs sʜᴏᴜʟᴅ ʙᴇ sᴇɴᴛ ɪɴ ᴘʀɪᴠᴀᴛᴇ.
๏ /resetrules: ʀᴇsᴇᴛ ᴛʜᴇ ᴄʜᴀᴛ ʀᴜʟᴇs ᴛᴏ ᴅᴇғᴀᴜʟᴛ."""
