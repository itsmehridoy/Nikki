from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telethon import *
from telethon.tl.types import ChatBannedRights

from Powers import LOGGER, OWNER_ID, telethn
from Powers.events import register
from Powers.database.sql.night_mode_sql import (
    add_nightmode,
    get_all_chat_id,
    is_nightmode_indb,
    rmnightmode,
)

hehes = ChatBannedRights(
    until_date=None,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    send_polls=True,
    invite_users=True,
    pin_messages=True,
    change_info=True,
)

openhehe = ChatBannedRights(
    until_date=None,
    send_messages=False,
    send_media=False,
    send_stickers=False,
    send_gifs=False,
    send_games=False,
    send_inline=False,
    send_polls=False,
    invite_users=True,
    pin_messages=True,
    change_info=True,
)


async def is_register_admin(chat, user):
    if isinstance(chat, (types.InputPeerChannel, types.InputChannel)):
        return isinstance(
            (
                await telethn(functions.channels.GetParticipantRequest(chat, user))
            ).participant,
            (types.ChannelParticipantAdmin, types.ChannelParticipantCreator),
        )
    if isinstance(chat, types.InputPeerUser):
        return True


async def can_change_info(message):
    result = await telethn(
        functions.channels.GetParticipantRequest(
            channel=message.chat_id,
            user_id=message.sender_id,
        )
    )
    p = result.participant
    return isinstance(p, types.ChannelParticipantCreator) or (
            isinstance(p, types.ChannelParticipantAdmin) and p.admin_rights.change_info
    )


@register(pattern="^/(nightmode|Nightmode|NightMode|Nmode|night|closechat) ?(.*)")
async def profanity(event):
    if event.fwd_from:
        return
    if event.is_private:
        return
    input = event.pattern_match.group(2)
    if event.sender_id != OWNER_ID:
        if not await is_register_admin(event.input_chat, event.sender_id):
            await event.reply("ᴏɴʟʏ ᴀᴅᴍɪɴs ᴄᴀɴ ᴇxᴇᴄᴜᴛᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ!")
            return
        if not await can_change_info(message=event):
            await event.reply(
                "ʏᴏᴜ ᴀʀᴇ ᴍɪssɪɴɢ ᴛʜᴇ ғᴏʟʟᴏᴡɪɴɢ ʀɪɢʜᴛs ᴛᴏ ᴜsᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ : CanChangeinfo"
            )
            return
    if not input:
        if is_nightmode_indb(str(event.chat_id)):
            await event.reply("ᴄᴜʀʀᴇɴᴛʟʏ ɴɪɢʜᴛᴍᴏᴅᴇ ɪs ᴇɴᴀʙʟᴇᴅ ғᴏʀ ᴛʜɪs ᴄʜᴀᴛ")
            return
        await event.reply("ᴄᴜʀʀᴇɴᴛʟʏ ɴɪɢʜᴛᴍᴏᴅᴇ ɪs ᴅɪsᴀʙʟᴇᴅ ғᴏʀ ᴛʜɪs ᴄʜᴀᴛ")
        return
    if "on" in input and event.is_group:
        if is_nightmode_indb(str(event.chat_id)):
            await event.reply("ɴɪɢʜᴛ ᴍᴏᴅᴇ ɪs ᴀʟʀᴇᴀᴅʏ ᴛᴜʀɴᴇᴅ ᴏɴ ғᴏʀ ᴛʜɪs ᴄʜᴀᴛ")
            return
        add_nightmode(str(event.chat_id))
        await event.reply("ɴɪɢʜᴛᴍᴏᴅᴇ ᴛᴜʀɴᴇᴅ ᴏɴ ғᴏʀ ᴛʜɪs ᴄʜᴀᴛ.")
    if "off" in input:
        if event.is_group and not is_nightmode_indb(str(event.chat_id)):
            await event.reply("ɴɪɢʜᴛ ᴍᴏᴅᴇ ɪs ᴀʟʀᴇᴀᴅʏ ᴏғғ ғᴏʀ ᴛʜɪs ᴄʜᴀᴛ")
            return
        rmnightmode(str(event.chat_id))
        await event.reply("ɴɪɢʜᴛᴍᴏᴅᴇ ᴅɪsᴀʙʟᴇᴅ!")
    if "off" not in input and "on" not in input:
        await event.reply("ᴘʟᴇᴀsᴇ sᴘᴇᴄɪғʏ ᴏɴ ᴏʀ ᴏғғ!")
        return


async def job_close():
    chats = get_all_chat_id()
    if len(chats) == 0:
        return
    for pro in chats:
        try:
            await telethn.send_message(
                int(pro.chat_id),
                "🌗 ɴɪɢʜᴛ ᴍᴏᴅᴇ sᴛᴀʀᴛɪɴɢ: <code>ᴄʟᴏsɪɴɢ sᴛɪᴄᴋᴇʀs ᴀɴᴅ ᴍᴇᴅɪᴀ sᴇɴᴅ ᴘᴇʀᴍɪssɪᴏɴs ᴜɴᴛɪʟ 06:00ᴀᴍ</code>\n\n",
                parse_mode=ParseMode.HTML,
            )
            await telethn(
                functions.messages.EditChatDefaultBannedRightsRequest(
                    peer=int(pro.chat_id), banned_rights=hehes
                )
            )
        except Exception as e:
            LOGGER.info(f"ᴜɴᴀʙʟᴇ ᴛᴏ ᴄʟᴏsᴇ ɢʀᴏᴜᴘ {chat} - {e}")


# Run everyday at 12am
scheduler = AsyncIOScheduler(timezone="Asia/Dhaka")
scheduler.add_job(job_close, trigger="cron", hour=23, minute=59)
scheduler.start()


async def job_open():
    chats = get_all_chat_id()
    if len(chats) == 0:
        return
    for pro in chats:
        try:
            await telethn.send_message(
                int(pro.chat_id),
                "🌗 ɴɪɢʜᴛ ᴍᴏᴅᴇ ᴇɴᴅᴇᴅ: <code>ᴄʜᴀᴛ ᴏᴘᴇɴɪɴɢ</code>\n\nᴇᴠᴇʀʏᴏɴᴇ sʜᴏᴜʟᴅ ʙᴇ ᴀʙʟᴇ ᴛᴏ sᴇɴᴅ ᴍᴇssᴀɢᴇs",
                parse_mode=ParseMode.HTML,
            )
            await telethn(
                functions.messages.EditChatDefaultBannedRightsRequest(
                    peer=int(pro.chat_id), banned_rights=openhehe
                )
            )
        except Exception as e:
            logger.info(f"ᴜɴᴀʙʟᴇ ᴛᴏ ᴏᴘᴇɴ ɢʀᴏᴜᴘ {pro.chat_id} - {e}")


# Run everyday at 06
scheduler = AsyncIOScheduler(timezone="Asia/Dhaka")
scheduler.add_job(job_open, trigger="cron", hour=6, minute=59)
scheduler.start()
