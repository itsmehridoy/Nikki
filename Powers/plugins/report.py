import traceback
from pyrogram import filters
from pyrogram.enums import ChatMembersFilter as cmf
from pyrogram.enums import ChatType
from pyrogram.errors import RPCError
from pyrogram.types import CallbackQuery, Message
from Powers.bot_class import Nikki
from Powers.database.reporting_db import Reporting
from Powers.utils.kbhelpers import ikb
from Powers.utils.caching import ADMIN_CACHE, admin_cache_reload
from Powers.utils.parser import mention_html

@Nikki.on_message(filters.regex(r"(?i)@admins?"))
async def tag_admins(_, m: Message):
    if m.chat.type == "private":
        await m.reply_text("This command is only for use in supergroups.")
        return    
    db = Reporting(m.chat.id)
    if not db.get_settings():
        return    
    try:
        admin_list = ADMIN_CACHE.get(m.chat.id)  # Use .get() to avoid KeyError
        if admin_list is None:
            admin_list = await admin_cache_reload(m, "adminlist")
    except KeyError:
        admin_list = await admin_cache_reload(m, "adminlist")
    
    user_admins = [i for i in admin_list if not i[1].lower().endswith("bot")]
    mention_users = [await mention_html("\u2063", admin[0]) for admin in user_admins]
    mention_users.sort(key=lambda x: x[1])
    mention_str = "".join(mention_users)
    
    await m.reply_text(
        f"{await mention_html(m.from_user.first_name, m.from_user.id)} ʀᴇᴘᴏʀᴛᴇᴅ ᴛʜᴇ ᴍᴇssᴀɢᴇ ᴛᴏ ᴀᴅᴍɪɴs!{mention_str}"
    )

@Nikki.on_cmd("reports", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_change_info", is_user=True)
async def report_setting(_, m: Message):
    args = m.text.split()
    db = Reporting(m.chat.id)

    if m.chat.type == ChatType.PRIVATE:
        if len(args) >= 2:
            option = args[1].lower()
            if option in ("yes", "on", "true"):
                db.set_settings(True)
                await m.reply_text(
                    "Turned on reporting! You'll be notified whenever anyone reports something in groups you are admin."
                )

            elif option in ("no", "off", "false"):
                db.set_settings(False)
                await m.reply_text("Turned off reporting! You won't get any reports.")
        else:
            await m.reply_text(f"Your current report preference is: `{db.get_settings()}`")
    elif len(args) >= 2:
        option = args[1].lower()
        if option in ("yes", "on", "true"):
            db.set_settings(True)
            await m.reply_text(
                "Turned on reporting! Admins who have turned on reports will be notified when /report or @admin is called.",
                quote=True,
            )

        elif option in ("no", "off", "false"):
            db.set_settings(False)
            await m.reply_text(
                "Turned off reporting! No admins will be notified on /report or @admin.",
                quote=True,
            )
    else:
        await m.reply_text(f"This group's current setting is: `{db.get_settings()}`")

@Nikki.on_cmd("report", group_only=True)
async def report_watcher(c: Nikki, m: Message):

    if not m.reply_to_message:
        await m.reply_text("Please reply to a message you want to report.")
        return
        
    if not m.from_user:
        return

    me = await c.get_me()
    db = Reporting(m.chat.id)

    if m.chat and m.reply_to_message and db.get_settings():
        reported_msg_id = m.reply_to_message.id
        reported_user = m.reply_to_message.from_user
        chat_name = m.chat.title or m.chat.username

        if reported_user.id == me.id:
            await m.reply_text("Nice try.")
            return
            
        if m.chat.username:
            msg = (
                f"<b> • ʀᴇᴘᴏʀᴛ: </b>{m.chat.title}\n"
                f"<b> • ʀᴇᴘᴏʀᴛ ʙʏ:</b> {await mention_html(m.from_user.first_name, m.from_user.id)} (<code>{m.from_user.id}</code>)\n"
                f"<b> • ʀᴇᴘᴏʀᴛᴇᴅ ᴜsᴇʀ:</b> {await mention_html(reported_user.first_name, reported_user.id)} (<code>{reported_user.id}</code>)\n"
            )

        else:
            msg = f"{await mention_html(m.from_user.first_name, m.from_user.id)} is calling for admins in '{chat_name}'!\n"

        link_chat_id = str(m.chat.id).replace("-100", "")
        link = f"https://t.me/c/{link_chat_id}/{reported_msg_id}"

        reply_markup = ikb(
            [
                [("➡ Message", link, "url")],
                [
                    (
                        "⚠ Kick",
                        f"report_{m.chat.id}=kick={reported_user.id}={reported_msg_id}",
                    ),
                    (
                        "⛔️ Ban",
                        f"report_{m.chat.id}=ban={reported_user.id}={reported_msg_id}",
                    ),
                ],
                [
                    (
                        "❎ Delete Message",
                        f"report_{m.chat.id}=del={reported_user.id}={reported_msg_id}",
                    ),
                ],
            ],
        )

        await m.reply_text(
            f"{await mention_html(m.from_user.first_name, m.from_user.id)} reported the message to the admins.",
            quote=True,
        )

        async for admin in c.get_chat_members(m.chat.id, filter=cmf.ADMINISTRATORS):
            if admin.user.is_bot or admin.user.is_deleted:
                continue
            if Reporting(admin.user.id).get_settings():
                try:
                    await c.send_message(
                        admin.user.id,
                        msg,
                        reply_markup=reply_markup,
                        disable_web_page_preview=True,
                    )
                    try:
                        await m.reply_to_message.forward(admin.user.id)
                        if len(m.text.split()) > 1:
                            await m.forward(admin.user.id)
                    except Exception:
                        pass
                except Exception:
                    pass
                except RPCError as ef:
                    pass
    return ""

@Nikki.on_callback_query(filters.regex("^report_"))
async def report_buttons(c: Nikki, q: CallbackQuery):
    splitter = str(q.data).replace("report_", "").split("=")
    chat_id = int(splitter[0])
    action = splitter[1]
    user_id = int(splitter[2])
    message_id = int(splitter[3])
    
    if action == "kick":
        try:
            await c.ban_chat_member(chat_id, user_id)
            await q.answer("✅ Successfully kicked")
            await c.unban_chat_member(chat_id, user_id)
            return
        except RPCError as err:
            await q.answer(f"🛑 Failed to Kick\n<b>Error:</b>\n<code>{err}</code>", show_alert=True)
    elif action == "ban":
        try:
            await c.ban_chat_member(chat_id, user_id)
            await q.answer("✅ Successfully Banned")
            return
        except RPCError as err:
            await q.answer(f"🛑 Failed to Ban\n<b>Error:</b>\n<code>{err}</code>", show_alert=True)
    else:
        pass
        
__PLUGIN__ = "Rᴇᴘᴏʀᴛs"

__alt_name__ = ["reports", "report"]

__HELP__ = """
**Dᴇsᴄʀɪᴘᴛɪᴏɴ:**
ᴡᴇ'ʀᴇ ᴀʟʟ ʙᴜsʏ ᴘᴇᴏᴘʟᴇ ᴡʜᴏ ᴅᴏɴ'ᴛ ʜᴀᴠᴇ ᴛɪᴍᴇ ᴛᴏ ᴍᴏɴɪᴛᴏʀ ᴏᴜʀ ɢʀᴏᴜᴘs 24/7. ʙᴜᴛ ʜᴏᴡ ᴅᴏ ʏᴏᴜ ʀᴇᴀᴄᴛ ɪғ sᴏᴍᴇᴏɴᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ɪs sᴘᴀᴍᴍɪɴɢ?

ᴘʀᴇsᴇɴᴛɪɴɢ ʀᴇᴘᴏʀᴛs; ɪғ sᴏᴍᴇᴏɴᴇ ɪɴ ʏᴏᴜʀ group ᴛʜɪɴᴋs sᴏᴍᴇᴏɴᴇ ɴᴇᴇᴅs ʀᴇᴘᴏʀᴛɪɴɢ, ᴛʜᴇʏ ɴᴏᴡ ʜᴀᴠᴇ ᴀɴ ᴇᴀsʏ ᴡᴀʏ ᴛᴏ ᴄᴀʟʟ ᴀʟʟ ᴀᴅᴍɪɴs.
────────────────────────

**Usᴇʀ Cᴏᴍᴍᴀɴᴅs:**
๏ /report: ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ ᴛᴏ ʀᴇᴘᴏʀᴛ ɪᴛ ғᴏʀ ᴀᴅᴍɪɴs ᴛᴏ ʀᴇᴠɪᴇᴡ.
๏ @admin|@admins: sᴀᴍᴇ ᴀs /report

**Tʜᴇ Fᴏʟʟᴏᴡɪɴɢ Cᴏᴍᴍᴀɴᴅs Aʀᴇ Aᴅᴍɪɴ Oɴʟʏ:**
๏ /reports ʏᴇs/ɴᴏ/ᴏɴ/ᴏғғ: ᴇɴᴀʙʟᴇ/ᴅɪsᴀʙʟᴇ ᴜsᴇʀ ʀᴇᴘᴏʀᴛs.

ᴛᴏ ʀᴇᴘᴏʀᴛ ᴀ ᴜsᴇʀ, sɪᴍᴘʟʏ ʀᴇᴘʟʏ ᴛᴏ ʜɪs ᴍᴇssᴀɢᴇ ᴡɪᴛʜ @admins or /report; ʙᴏᴛ ᴡɪʟʟ ᴛʜᴇɴ ʀᴇᴘʟʏ ᴡɪᴛʜ ᴀ ᴍᴇssᴀɢᴇ sᴛᴀᴛɪɴɢ ᴛʜᴀᴛ ᴀᴅᴍɪɴs ʜᴀᴠᴇ ʙᴇᴇɴ ɴᴏᴛɪғɪᴇᴅ. ᴛʜɪs ᴍᴇssᴀɢᴇ ᴛᴀɢs ᴀʟʟ ᴛʜᴇ ᴄʜᴀᴛ ᴀᴅᴍɪɴs; sᴀᴍᴇ ᴀs ɪғ ᴛʜᴇʏ ʜᴀᴅ ʙᴇᴇɴ @'ᴇᴅ.

**ɴᴏᴛᴇ:** ᴛʜᴀᴛ ᴛʜᴇ ʀᴇᴘᴏʀᴛ ᴄᴏᴍᴍᴀɴᴅs ᴅᴏ ɴᴏᴛ ᴡᴏʀᴋ ᴡʜᴇɴ ᴀᴅᴍɪɴs ᴜsᴇ ᴛʜᴇᴍ; ᴏʀ ᴡʜᴇɴ ᴜsᴇᴅ ᴛᴏ ʀᴇᴘᴏʀᴛ ᴀɴ ᴀᴅᴍɪɴ."""
