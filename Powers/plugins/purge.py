import codecs
from asyncio import sleep

from pyrogram import enums
from pyrogram.enums import ChatType
from pyrogram.errors import MessageDeleteForbidden, RPCError
from pyrogram.types import Message

from Powers import SUPPORT_GROUP
from Powers.bot_class import Nikki

@Nikki.on_cmd("purge", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_delete_messages", is_both=True)
async def purge(c: Nikki, m: Message):

    if m.reply_to_message:
        message_ids = list(range(m.reply_to_message.id, m.id))

        def divide_chunks(l: list, n: int = 100):
            for i in range(0, len(l), n):
                yield l[i : i + n]

        # Dielete messages in chunks of 100 messages
        m_list = list(divide_chunks(message_ids))

        try:
            for plist in m_list:
                await c.delete_messages(
                    chat_id=m.chat.id,
                    message_ids=plist,
                    revoke=True,
                )
            await m.delete()
        except MessageDeleteForbidden:
            await m.reply_text(
                text="Cannot delete all messages. The messages may be too old, I might not have delete rights, or this might not be a supergroup."
            )
            return
        except RPCError as ef:
            await m.reply_text(
                text=f"""Some error occured, report to @{SUPPORT_GROUP}

      <b>Error:</b> <code>{ef}</code>"""
            )

        count_del_msg = len(message_ids)

        z = await m.reply_text(text=f"ᴅᴇʟᴇᴛᴇᴅ {count_del_msg} ᴍᴇssᴀɢᴇs!")
        await sleep(3)
        await z.delete()
        return
    await m.reply_text("Reply to a message to start purge !")
    return


@Nikki.on_cmd("spurge", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_delete_messages", is_both=True)
async def spurge(c: Nikki, m: Message):

    if m.reply_to_message:
        message_ids = list(range(m.reply_to_message.id, m.id))

        def divide_chunks(l: list, n: int = 100):
            for i in range(0, len(l), n):
                yield l[i : i + n]

        # Dielete messages in chunks of 100 messages
        m_list = list(divide_chunks(message_ids))

        try:
            for plist in m_list:
                await c.delete_messages(
                    chat_id=m.chat.id,
                    message_ids=plist,
                    revoke=True,
                )
            await m.delete()
        except MessageDeleteForbidden:
            await m.reply_text(
                text="Cannot delete all messages. The messages may be too old, I might not have delete rights, or this might not be a supergroup."
            )
            return
        except RPCError as ef:
            await m.reply_text(
                text=f"""Some error occured, report to @{SUPPORT_GROUP}

      <b>Error:</b> <code>{ef}</code>"""
            )
        return
    await m.reply_text("Reply to a message to start spurge !")
    return


@Nikki.on_cmd("del", group_only=True, self_admin=True)
@Nikki.adminsOnly(permissions="can_delete_messages", is_both=True)
async def del_msg(c: Nikki, m: Message):
    if m.reply_to_message:
        await m.delete()
        await c.delete_messages(
            chat_id=m.chat.id,
            message_ids=m.reply_to_message.id,
        )
    else:
        await m.reply_text("Reply to a message to let me know what to delete.")
    return

@Nikki.on_cmd("stat", group_only=True)
async def stat_chat(_, m: Message):
    __stats_format = f"**ᴛᴏᴛᴀʟ ᴍᴇssᴀɢᴇs ɪɴ {m.chat.title}:** `{m.id}`"
    await m.reply_text(__stats_format)

@Nikki.on_cmd("encode")
async def encode_text(_, message: Message):
    if len(message.command) > 1:
        text_to_encode = message.text.split("/encode ", 1)[1]
        encoded_text = ''.join([f'\\x{ord(char):02x}' for char in text_to_encode])
        await message.reply(f"Here is your encoded text: `{encoded_text}`")
    else:
        await message.reply("Please provide text to encode.")

@Nikki.on_cmd(["unencode", "decode"])
async def unencode_text(_, message: Message):
    if len(message.command) > 1:
        encoded_text = message.text.split("/unencode ", 1)[1]
        try:
            decoded_text = codecs.decode(encoded_text, 'unicode_escape')
            await message.reply(f"Here is your decoded text: `{decoded_text}`")
        except UnicodeDecodeError:
            await message.reply("Unable to decode the provided text.")
    else:
        await message.reply("Please provide text to decode using /unencode.")

__alt_name__ = ["purge", "del", "spurge"]
__PLUGIN__ = "Pᴜʀɢᴇ"

__HELP__ = """
**Dᴇsᴄʀɪᴘᴛɪᴏɴ :**
ɴᴇᴇᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ʟᴏᴛs ᴏғ ᴍᴇssᴀɢᴇs? ᴛʜᴀᴛ's ᴡʜᴀᴛ ᴘᴜʀɢᴇs ᴀʀᴇ ғᴏʀ!
────────────────────────

**Tʜᴇ Fᴏʟʟᴏᴡɪɴɢ Cᴏᴍᴍᴀɴᴅs Aʀᴇ Aᴅᴍɪɴ Oɴʟʏ :**
๏ /purge: ᴅᴇʟᴇᴛᴇs ᴍᴇssᴀɢᴇs ᴜᴘᴛᴏ ʀᴇᴘʟɪᴇᴅ ᴍᴇssᴀɢᴇ.
๏ /spurge: ᴅᴇʟᴇᴛᴇs ᴍᴇssᴀɢᴇs ᴜᴘᴛᴏ ʀᴇᴘʟɪᴇᴅ ᴍᴇssᴀɢᴇ ᴡɪᴛʜᴏᴜᴛ ᴀ sᴜᴄᴄᴇss ᴍᴇssᴀɢᴇ.
๏ /del: ᴅᴇʟᴇᴛᴇs ᴀ sɪɴɢʟᴇ ᴍᴇssᴀɢᴇ, ᴜsᴇᴅ ᴀs ᴀ ʀᴇᴘʟʏ ᴛᴏ ᴍᴇssᴀɢᴇ."""
