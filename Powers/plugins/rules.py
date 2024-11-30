from pyrogram import filters
from pyrogram.enums import ChatMemberStatus as CMS
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, Message

from Powers.bot_class import Nikki
from Powers.database.rules_db import Rules
from Powers.utils.kbhelpers import ikb
from Powers.utils.string import build_keyboard, parse_button
from Powers.plugins.formatting import gen_formatting_kb

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

    priv_rules_status = db.get_privrules()

    if priv_rules_status:
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
            text="ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʙᴇʟᴏᴡ ʙᴜᴛᴛᴏɴ ᴛᴏ sᴇᴇ ᴛʜɪs ɢʀᴏᴜᴘ ʀᴜʟᴇs!",
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

    rules = None

    if not rules:
        return await m.reply_text("ᴘʀᴏᴠɪᴅᴇ sᴏᴍᴇ ᴛᴇxᴛ ᴛᴏ sᴇᴛ ᴀs ʀᴜʟᴇs !!")

    if len(rules) > 4000:
        rules = rules[:3949]  # Split Rules if len > 4000 chars
        await m.reply_text("Rᴜʟᴇs ᴀʀᴇ ᴛʀᴜɴᴄᴀᴛᴇᴅ ᴛᴏ 𝟹𝟿𝟻𝟶 ᴄʜᴀʀᴀᴄᴛᴇʀs!")

    db.set_rules(rules)
    await m.reply_text(text="sᴜᴄᴄᴇssғᴜʟʟʏ sᴇᴛ ʀᴜʟᴇs ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ.")


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
            msg = f"ᴘʀɪᴠᴀᴛᴇ ʀᴜʟᴇs ʜᴀᴠᴇ ʙᴇᴇɴ ᴛᴜʀɴᴇᴅ <b>ᴏɴ</b> ғᴏʀ ᴄʜᴀᴛ <b>{m.chat.title}</b>"
        elif option in ("off", "no"):
            db.set_privrules(False)
            msg = f"Private Rules have been turned <b>off</b> for chat <b>{m.chat.title}</b>"
        else:
            msg = "ᴏᴘᴛɪᴏɴ ɴᴏᴛ ᴠᴀʟɪᴅ, ᴄʜᴏᴏsᴇ ғʀᴏᴍ <code>on</code>, <code>yes</code>, <code>off</code>, <code>no</code>"
        await m.reply_text(msg)
    elif len(m.text.split()) == 1:
        curr_pref = db.get_privrules()
        msg = (
            f"ᴄᴜʀʀᴇɴᴛ ᴘʀᴇғᴇʀᴇɴᴄᴇ ғᴏʀ ᴘʀɪᴠᴀᴛᴇ ʀᴜʟᴇs ɪɴ ᴛʜɪs ᴄʜᴀᴛ ɪs: <b>{curr_pref}</b>"
        )
        await m.reply_text(msg)
    else:
        await m.reply_text(text="Pʟᴇᴀsᴇ ᴄʜᴇᴄᴋ ʜᴇʟᴘ ᴏɴ ʜᴏᴡ ᴛᴏ ᴜsᴇ ᴛʜɪs ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ.")

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
        text="ᴀʀᴇ ʏᴏᴜ sᴜʀᴇ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴄʟᴇᴀʀ ʀᴜʟᴇs?",
        reply_markup=ikb(
            [[("ᴄᴏɴғɪʀᴍ", "clear_rules"), ("ᴄᴀɴᴄᴇʟ ❌", "close_admin")]],
        ),
    )
    return


@Nikki.on_cb("clear_rules")
async def clearrules_callback(_, q: CallbackQuery):
    user_id = q.from_user.id
    user_status = (await q.message.chat.get_member(user_id)).status
    if user_status not in {CMS.OWNER, CMS.ADMINISTRATOR}:
        await q.answer(
            "You need to be an admin to do this.",
            show_alert=True,
        )
        return
    Rules(q.message.chat.id).clear_rules()
    await q.message.edit_text(text="sᴜᴄᴄᴇssғᴜʟʟʏ ᴄʟᴇᴀʀᴇᴅ ʀᴜʟᴇs ғᴏʀ ᴛʜɪs ɢʀᴏᴜᴘ!")
    await q.answer("Rᴜʟᴇs ғᴏʀ ᴛʜᴇ ᴄʜᴀᴛ ʜᴀᴠᴇ ʙᴇᴇɴ ᴄʟᴇᴀʀᴇᴅ!", show_alert=True)
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
