import os
from asyncio import sleep
from html import escape
from os import remove
from traceback import format_exc
from datetime import datetime, timedelta

from pyrogram.enums import ChatType, ChatMembersFilter as CMF, ChatMemberStatus as CMS, ParseMode
from pyrogram.errors import (ChatAdminInviteRequired, ChatAdminRequired,
                             FloodWait, RightForbidden, RPCError,
                             UserAdminInvalid, PeerIdInvalid)
from pyrogram.types import ChatPrivileges, Message, InlineKeyboardMarkup, InlineKeyboardButton
from Powers import DEV_USERS, LOGGER, OWNER_ID, SUPPORT_GROUP
from Powers.bot_class import Nikki
from Powers.database.approve_db import Approve
from Powers.utils.caching import (ADMIN_CACHE, TEMP_ADMIN_CACHE_BLOCK,
                                  admin_cache_reload)
from Powers.utils.extract_user import extract_user
from Powers.utils.parser import mention_html

@Nikki.on_cmd(["adminlist", "staff"], group_only=True)
async def adminlist_command(Nikki, message):
    try:
        lel = await message.reply_text("Fetching the list of administrators...")
        administrators = []
        
        async for member in Nikki.get_chat_members(
            message.chat.id, filter=CMF.ADMINISTRATORS
        ):
            if not member.user.is_bot:
                user_mention = ""
                
                if member.user.username:
                    user_mention = f"@{member.user.username}"
                else:
                    if member.user.first_name:
                        user_mention = await mention_html(
                            member.user.first_name, member.user.id
                        )
                
                if user_mention:
                    administrators.append(user_mention)

        if administrators:
            admin_list_text = "\n".join([f"💠 {admin}" for admin in administrators])
            response_text = f"<b>Admins in {message.chat.title}:</b>\n{admin_list_text}\n\n<i>Note: These are cached values.</i>"
        else:
            response_text = f"No administrators found in {message.chat.title}."
        
        await lel.edit_text(
            response_text,
            parse_mode=ParseMode.HTML,
        )
    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")

@Nikki.on_cmd(["admincache", "reload"], group_only=True)
async def reload_admins(_, m: Message):
    global TEMP_ADMIN_CACHE_BLOCK
    if (
        (m.chat.id in set(TEMP_ADMIN_CACHE_BLOCK.keys()))
        and (m.from_user.id not in DEV_USERS)
        and TEMP_ADMIN_CACHE_BLOCK[m.chat.id] == "manualblock"
    ):
        await m.reply_text("You can only refresh the admin cache in <b>{m.chat.title}</b> once every 10 minutes.")
        return
    try:
        await admin_cache_reload(m, "admincache")
        TEMP_ADMIN_CACHE_BLOCK[m.chat.id] = "manualblock"
        await m.reply_text("I have refreshed my admin cache.")
    except RPCError as ef:
        await m.reply_text(
            text=f"Some error occured, report it using `/bug` \n <b>Error:</b> <code>{ef}</code>"
        )
        LOGGER.error(ef)
        LOGGER.error(format_exc())
    return

@Nikki.on_cmd("zombies", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_restrict_members", is_both=True)
async def zombie_clean(c: Nikki, m: Message):
    zombie = 0
    wait = await m.reply_text("Searching ... and banning ...")
    async for member in c.get_chat_members(m.chat.id):
        if member.user.is_deleted:
            zombie += 1
            try:
                await c.ban_chat_member(m.chat.id, member.user.id)
            except UserAdminInvalid:
                zombie -= 1
            except FloodWait as e:
                await sleep(e.x)
    if zombie == 0:
        return await wait.edit_text("Group is clean!")
    return await wait.edit_text(
        text=f"<b>{zombie}</b> Zombies found and has been banned!",
    )

@Nikki.on_cmd("demote", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_promote_members", is_both=True)
async def demote_usr(c: Nikki, m: Message):
    global ADMIN_CACHE
    if len(m.text.split()) == 1 and not m.reply_to_message:
        await m.reply_text("I can't demote nothing.")
        return
    try:
        user_id, user_first_name, _ = await extract_user(c, m)
    except Exception:
        return
    if user_id == Nikki.id:
        await m.reply_text("Get an admin to demote me!")
        return
    # If user not already admin
    try:
        admin_list = {i[0] for i in ADMIN_CACHE[m.chat.id]}
    except KeyError:
        admin_list = {
            i[0] for i in (await admin_cache_reload(m, "demote_cache_update"))
        }
    if user_id not in admin_list:
        await m.reply_text(
            "This user is not an admin, how am I supposed to re-demote them?",
        )
        return
    try:
        await m.chat.promote_member(
            user_id=user_id,
            privileges=ChatPrivileges(can_manage_chat=False),
        )
        LOGGER.info(f"{m.from_user.id} demoted {user_id} in {m.chat.id}")
        # ----- Remove admin from cache -----
        try:
            admin_list = ADMIN_CACHE[m.chat.id]
            user = next(user for user in admin_list if user[0] == user_id)
            admin_list.remove(user)
            ADMIN_CACHE[m.chat.id] = admin_list
        except (KeyError, StopIteration):
            await admin_cache_reload(m, "demote_key_stopiter_error")
        await m.reply_text(
            ("{demoter} demoted {demoted} in <b>{chat_title}</b>!").format(
                demoter=(
                    await mention_html(
                        m.from_user.first_name,
                        m.from_user.id,
                    )
                ),
                demoted=(await mention_html(user_first_name, user_id)),
                chat_title=m.chat.title,
            ),
        )
    except ChatAdminRequired:
        await m.reply_text("I am not admin aroung here.")
    except RightForbidden:
        await m.reply_text("I can't demote users here.")
    except UserAdminInvalid:
        await m.reply_text(
            "Cannot act on this user, maybe I wasn't the one who changed their permissions."
        )
    except RPCError as ef:
        await m.reply_text(
            f"Some error occured, report it using `/bug` \n <b>Error:</b> <code>{ef}</code>"
        )
        LOGGER.error(ef)
        LOGGER.error(format_exc())
    return

@Nikki.on_cmd("fullpromote", group_only=True)
@Nikki.adminsOnly(only_owner=True)
async def fullpromote_usr(c: Nikki, m: Message):
    global ADMIN_CACHE
    if len(m.text.split()) == 1 and not m.reply_to_message:
        await m.reply_text(
            text="I can't promote nothing! Give me an username or user id or atleast reply to that user"
        )
        return
    try:
        user_id, user_first_name, user_name = await extract_user(c, m)
    except Exception:
        return
    bot = await c.get_chat_member(m.chat.id, c.me.id)
    if user_id == c.me.id:
        await m.reply_text("Huh, how can I even promote myself?")
        return
    if not bot.privileges.can_promote_members:
        return await m.reply_text(
            "I don't have enough permissions!",
        )  # This should be here
    user = await c.get_chat_member(m.chat.id, m.from_user.id)
    if m.from_user.id != OWNER_ID and user.status != CMS.OWNER:
        return await m.reply_text("This command can only be used by chat owner.")
    # If user is alreay admin
    try:
        admin_list = {i[0] for i in ADMIN_CACHE[m.chat.id]}
    except KeyError:
        admin_list = {
            i[0] for i in (await admin_cache_reload(m, "promote_cache_update"))
        }
    if user_id in admin_list:
        await m.reply_text(
            "This user is already an admin, how am I supposed to re-promote them?",
        )
        return
    try:
        await m.chat.promote_member(user_id=user_id, privileges=bot.privileges)
        title = ""
        if m.chat.type in [ChatType.SUPERGROUP, ChatType.GROUP]:
            title = "Admin"  # Default fullpromote title
            if len(m.text.split()) == 3 and not m.reply_to_message:
                title = " ".join(m.text.split()[2:16])  # trim title to 16 characters
            elif len(m.text.split()) >= 2 and m.reply_to_message:
                title = " ".join(m.text.split()[1:16])  # trim title to 16 characters

            try:
                await c.set_administrator_title(m.chat.id, user_id, title)
            except RPCError as e:
                LOGGER.error(e)
                LOGGER.error(format_exc())
            except Exception as e:
                LOGGER.error(e)
                LOGGER.error(format_exc())
        await m.reply_text(
            (
                "{promoter} promoted {promoted} in chat <b>{chat_title}</b> with full rights!"
            ).format(
                promoter=(await mention_html(m.from_user.first_name, m.from_user.id)),
                promoted=(await mention_html(user_first_name, user_id)),
                chat_title=f"{escape(m.chat.title)} title set to {title}"
                if title
                else f"{escape(m.chat.title)} title set to Default",
            ),
        )
        # If user is approved, disapprove them as they willbe promoted and get
        # even more rights
        if Approve(m.chat.id).check_approve(user_id):
            Approve(m.chat.id).remove_approve(user_id)
        # ----- Add admin to temp cache -----
        try:
            inp1 = user_name or user_first_name
            admins_group = ADMIN_CACHE[m.chat.id]
            admins_group.append((user_id, inp1))
            ADMIN_CACHE[m.chat.id] = admins_group
        except KeyError:
            await admin_cache_reload(m, "promote_key_error")
    except ChatAdminRequired:
        await m.reply_text(text="I'm not admin or I don't have rights......")
    except RightForbidden:
        await m.reply_text(text="I don't have enough rights to promote this user.")
    except UserAdminInvalid:
        await m.reply_text(
            text="Cannot act on this user, maybe I wasn't the one who changed their permissions."
        )
    except RPCError as e:
        await m.reply_text(
            text=f"Some error occured, report it using `/bug` \n <b>Error:</b> <code>{e}</code>"
        )
        LOGGER.error(e)
        LOGGER.error(format_exc())
    return

@Nikki.on_cmd("promote", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_promote_members", is_both=True)
async def promote_usr(c: Nikki, m: Message):
    global ADMIN_CACHE
    if len(m.text.split()) == 1 and not m.reply_to_message:
        await m.reply_text(
            text="I can't promote nothing!......reply to user to promote him/her...."
        )
        return
    try:
        user_id, user_first_name, user_name = await extract_user(c, m)
    except Exception:
        return
    bot = await c.get_chat_member(m.chat.id, Nikki.id)
    if user_id == Nikki.id:
        await m.reply_text("Huh, how can I even promote myself?")
        return
    if not bot.privileges.can_promote_members:
        return await m.reply_text(
            "I don't have enough permissions",
        )  # This should be here
    # If user is alreay admin
    try:
        admin_list = {i[0] for i in ADMIN_CACHE[m.chat.id]}
    except KeyError:
        admin_list = {
            i[0] for i in (await admin_cache_reload(m, "promote_cache_update"))
        }
    if user_id in admin_list:
        await m.reply_text(
            "This user is already an admin, how am I supposed to re-promote them?",
        )
        return
    try:
        await m.chat.promote_member(
            user_id=user_id,
            privileges=ChatPrivileges(
                can_change_info=bot.privileges.can_change_info,
                can_invite_users=bot.privileges.can_invite_users,
                can_delete_messages=bot.privileges.can_delete_messages,
                can_restrict_members=bot.privileges.can_restrict_members,
                can_pin_messages=bot.privileges.can_pin_messages,
                can_manage_chat=bot.privileges.can_manage_chat,
                can_manage_video_chats=bot.privileges.can_manage_video_chats,
            ),
        )
        title = ""
        if m.chat.type in [ChatType.SUPERGROUP, ChatType.GROUP]:
            title = "Admin"  # Deafult title
            if len(m.text.split()) >= 3 and not m.reply_to_message:
                title = " ".join(m.text.split()[2:16]) # trim title to 16 characters
            elif len(m.text.split()) >= 2 and m.reply_to_message:
                title = " ".join(m.text.split()[1:16]) # trim title to 16 characters
            try:
                await c.set_administrator_title(m.chat.id, user_id, title)
            except RPCError as e:
                LOGGER.error(e)
                LOGGER.error(format_exc())
            except Exception as e:
                LOGGER.error(e)
                LOGGER.error(format_exc())
        LOGGER.info(
            f"{m.from_user.id} promoted {user_id} in {m.chat.id} with title '{title}'",
        )
        await m.reply_text(
            ("{promoter} promoted {promoted} in chat <b>{chat_title}</b>!").format(
                promoter=(await mention_html(m.from_user.first_name, m.from_user.id)),
                promoted=(await mention_html(user_first_name, user_id)),
                chat_title=f"{escape(m.chat.title)} title set to {title}"
                if title
                else f"{escape(m.chat.title)} title set to default",
            ),
        )
        # If user is approved, disapprove them as they willbe promoted and get
        # even more rights
        if Approve(m.chat.id).check_approve(user_id):
            Approve(m.chat.id).remove_approve(user_id)
        # ----- Add admin to temp cache -----
        try:
            inp1 = user_name or user_first_name
            admins_group = ADMIN_CACHE[m.chat.id]
            admins_group.append((user_id, inp1))
            ADMIN_CACHE[m.chat.id] = admins_group
        except KeyError:
            await admin_cache_reload(m, "promote_key_error")
    except ChatAdminRequired:
        await m.reply_text(text="I'm not admin or I don't have rights.")
    except RightForbidden:
        await m.reply_text(text="I don't have enough rights to promote this user.")
    except UserAdminInvalid:
        await m.reply_text(
            text="Cannot act on this user, maybe I wasn't the one who changed their permissions."
        )
    except RPCError as e:
        await m.reply_text(
            text=f"Some error occured, report it using `/bug` \n <b>Error:</b> <code>{e}</code>"
        )
        LOGGER.error(e)
        LOGGER.error(format_exc())
    return
  
@Nikki.on_cmd("invitelink", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_invite_users", is_both=True)
async def generate_invite_link(c: Nikki, m):
    try:
        chat = m.chat
        link = await c.export_chat_invite_link(chat.id)
        await m.reply_text(
            f"Here's the invite link for {m.chat.title}:\n{link}",
            disable_web_page_preview=True,
        )
    except Exception as e:
        await m.reply_text(f"An error occurred while generating the invite link: {str(e)}")

@Nikki.on_cmd("setgtitle", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_change_info", is_both=True)
async def setgtitle(_, m: Message):
    if len(m.command) < 1:
        return await m.reply_text("Please read /help for using it!")
    gtit = m.text.split(None, 1)[1]
    try:
        await m.chat.set_title(gtit)
    except Exception as e:
        return await m.reply_text(f"Error: {e}")
    return await m.reply_text(
        f"Successfully Changed Group Title From {m.chat.title} To {gtit}",
    )

@Nikki.on_cmd(["setgdesc", "setdescription"], group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_change_info", is_both=True)
async def setgdes(_, m: Message):
    if len(m.command) < 1:
        return await m.reply_text("Please read /help for using it!")
    desp = m.text.split(None, 1)[1]
    try:
        await m.chat.set_description(desp)
    except Exception as e:
        return await m.reply_text(f"Error: {e}")
    return await m.reply_text(
        f"Successfully Changed Group description From {m.chat.description} To {desp}",
    )

@Nikki.on_cmd("title", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_promote_members", is_both=True)
async def set_user_title(c: Nikki, m: Message):
    if len(m.text.split()) == 1 and not m.reply_to_message:
        return await m.reply_text("To whom??")
    if m.reply_to_message:
        if len(m.text.split()) >= 2:
            reason = m.text.split(None, 1)[1]
    else:
        if len(m.text.split()) >= 3:
            reason = m.text.split(None, 2)[2]
    try:
        user_id, _, _ = await extract_user(c, m)
    except Exception:
        return
    if not user_id:
        return await m.reply_text("Cannot find user!")
    if user_id == Nikki.id:
        return await m.reply_text("Huh, why ?")
    if not reason:
        return await m.reply_text("Read /help please!")
    from_user = await c.get_users(user_id)
    title = reason
    try:
        await c.set_administrator_title(m.chat.id, from_user.id, title)
    except Exception as e:
        return await m.reply_text(f"Error: {e}")
    return await m.reply_text(
        f"Successfully Changed {from_user.mention}'s Admin Title To {title}",
    )

@Nikki.on_cmd("delgpic", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_change_info", is_both=True)
async def delgpic(c: Nikki, m: Message):
    chat_id = m.chat.id
    try:
        chat_info = await c.get_chat(chat_id)
        if chat_info.photo:
            await c.delete_chat_photo(chat_id)
            await c.send_message(chat_id, "Group profile picture has been deleted.")
        else:
            await c.send_message(chat_id, "The group does not have a profile picture.")
    except PeerIdInvalid:
        await c.send_message(chat_id, "Invalid chat ID.")

@Nikki.on_cmd("setgpic", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_change_info", is_both=True)
async def set_chat_photo(_, ctx: Message):
    reply = ctx.reply_to_message
    if not reply:
        return await ctx.reply_text("Reply to a photo to set it as chat_photo")
    file = reply.document or reply.photo
    if not file:
        return await ctx.reply_text(
            "Reply to a photo or document to set it as chat_photo"
        )
    if file.file_size > 5000000:
        return await ctx.reply("File size too large.")
    photo = await reply.download()
    try:
        await ctx.chat.set_photo(photo=photo)
        await ctx.reply_text("Successfully Changed Group Photo")
    except Exception as err:
        await ctx.reply(f"Failed changed group photo. ERROR: {err}")
    os.remove(photo)


@Nikki.on_cmd("setsticker", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_change_info", is_both=True)
async def set_sticker(client, message):
    replied = message.reply_to_message
    admin = message.from_user.mention if message.from_user else "Anon"
    chat = message.chat
    if replied:
        if not replied.sticker:
            await message.reply("ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ʀᴇᴘʟʏ ᴛᴏ ꜱᴏᴍᴇ ꜱᴛɪᴄᴋᴇʀ ᴛᴏ ꜱᴇᴛ ᴄʜᴀᴛ ꜱᴛɪᴄᴋᴇʀ ꜱᴇᴛ!")
            return
        stickers = message.reply_to_message.sticker.set_name
        try:
            await Nikki.invoke(
                SetStickers(
                    channel=await client.resolve_peer(chat.id),
                    stickerset=InputStickerSetShortName(short_name=stickers),
                )
            )
            await message.reply_text("ꜱᴜᴄᴄᴇꜱꜱꜰᴜʟʟʏ ꜱᴇᴛ ɴᴇᴡ ɢʀᴏᴜᴘ ꜱᴛɪᴄᴋᴇʀꜱ ɪɴ **{}**!".format(chat.title))
            return "#𝗖𝗛𝗔𝗡𝗚𝗘𝗗𝗚𝗥𝗢𝗨𝗣𝗦𝗧𝗜𝗖𝗞𝗘𝗥𝗦\n\n» **ꜱᴛɪᴄᴋᴇʀ ꜱᴇᴛ**: https://t.me/addstickers/{}\n» **ᴀᴅᴍɪɴ** : {}".format(stickers, admin)
        except errors.BadRequest as ee:
            if ee.MESSAGE == "PARTICIPANTS_TOO_FEW":
                await message.reply_text("ꜱᴏʀʀʏ, ᴅᴜᴇ ᴛᴏ ᴛᴇʟᴇɢʀᴀᴍ ʀᴇꜱᴛʀɪᴄᴛɪᴏɴꜱ ᴄʜᴀᴛ ɴᴇᴇᴅꜱ ᴛᴏ ʜᴀᴠᴇ ᴍɪɴɪᴍᴜᴍ 100 ᴍᴇᴍʙᴇʀꜱ ʙᴇꜰᴏʀᴇ ᴛʜᴇʏ ᴄᴀɴ ʜᴀᴠᴇ ɢʀᴏᴜᴘ ꜱᴛɪᴄᴋᴇʀꜱ!")
                return
    else:
        await message.reply("ʏᴏᴜ ɴᴇᴇᴅ ᴛᴏ ʀᴇᴘʟʏ ᴛᴏ ꜱᴏᴍᴇ ꜱᴛɪᴄᴋᴇʀ ᴛᴏ ꜱᴇᴛ ᴄʜᴀᴛ ꜱᴛɪᴄᴋᴇʀ ꜱᴇᴛ.")
        return


__PLUGIN__ = "Aᴅᴍɪɴs"
__alt_name__ = [
    "admins",
    "promote",
    "demote",
    "adminlist",
    "setgpic",
    "title",
    "setgtitle",
    "fullpromote",
    "invitelink",
    "setgdes",
    "zombies",
]

__HELP__ = """
**Dᴇsᴄʀɪᴘᴛɪᴏɴ :**
Tʜᴇ Cᴏᴍᴍᴀɴᴅs Aᴅᴍɪɴs Cᴀɴ Usᴇ Fᴏʀ Mᴀɴᴀɢᴇ A Gʀᴏᴜᴘ
────────────────────────

**Usᴇʀ Cᴏᴍᴍᴀɴᴅs :**
๏ /adminlist: ʟɪsᴛ ᴀʟʟ ᴛʜᴇ ᴀᴅᴍɪɴs ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ.

**Tʜᴇ Fᴏʟʟᴏᴡɪɴɢ Cᴏᴍᴍᴀɴᴅs Aʀᴇ Aᴅᴍɪɴ Oɴʟʏ :**
๏ /invitelink: ɢᴇᴛs ᴄʜᴀᴛ ɪɴᴠɪᴛᴇʟɪɴᴋ.
๏ /promote: ᴘʀᴏᴍᴏᴛᴇs ᴛʜᴇ ᴜsᴇʀ ʀᴇᴘʟɪᴇᴅ ᴛᴏ ᴏʀ ᴛᴀɢɢᴇᴅ (sᴜᴘᴘᴏʀᴛs ᴡɪᴛʜ ᴛɪᴛʟᴇ).
๏ /fullpromote: ғᴜʟʟʏ ᴘʀᴏᴍᴏᴛᴇs ᴛʜᴇ ᴜsᴇʀ ʀᴇᴘʟɪᴇᴅ ᴛᴏ ᴏʀ ᴛᴀɢɢᴇᴅ (sᴜᴘᴘᴏʀᴛs ᴡɪᴛʜ ᴛɪᴛʟᴇ).
๏ /demote: ᴅᴇᴍᴏᴛᴇs ᴛʜᴇ ᴜsᴇʀ ʀᴇᴘʟɪᴇᴅ ᴛᴏ ᴏʀ ᴛᴀɢɢᴇᴅ. (ɪғ ᴘʀᴏᴍᴏᴛᴇᴅ ʙʏ ᴍᴇ)
๏ /admincache: ʀᴇʟᴏᴀᴅs ᴛʜᴇ ʟɪsᴛ ᴏғ ᴀʟʟ ᴛʜᴇ ᴀᴅᴍɪɴs ɪɴ ᴛʜᴇ ɢʀᴏᴜᴘ.
๏ /zombies: ʙᴀɴs ᴀʟʟ ᴛʜᴇ ᴅᴇʟᴇᴛᴇᴅ ᴀᴄᴄᴏᴜɴᴛs. 
๏ /title: sᴇᴛs ᴀ ᴄᴜsᴛᴏᴍ ᴛɪᴛʟᴇ ғᴏʀ ᴀɴ ᴀᴅᴍɪɴ ᴛʜᴀᴛ ᴛʜᴇ ʙᴏᴛ ᴘʀᴏᴍᴏᴛᴇᴅ.
๏ /setgtitle : sᴇᴛs ɴᴇᴡ ᴄʜᴀᴛ ᴛɪᴛʟᴇ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ.
๏ /setgpic: ᴀs ᴀ ʀᴇᴘʟʏ ᴛᴏ ғɪʟᴇ ᴏʀ ᴘʜᴏᴛᴏ ᴛᴏ sᴇᴛ ɢʀᴏᴜᴘ ᴘʀᴏғɪʟᴇ ᴘɪᴄ.
๏ /delgpic: sᴀᴍᴇ ᴀs ᴀʙᴏᴠᴇ ʙᴜᴛ ᴛᴏ ʀᴇᴍᴏᴠᴇ ɢʀᴏᴜᴘ ᴘʀᴏғɪʟᴇ ᴘɪᴄ.
๏ /setdescription : sᴇᴛs ɴᴇᴡ ᴄʜᴀᴛ ᴅᴇsᴄʀɪᴘᴛɪᴏɴ ɪɴ ɢʀᴏᴜᴘ."""
