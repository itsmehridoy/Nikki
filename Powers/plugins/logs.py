from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from Powers import MESSAGE_DUMP
from Powers.bot_class import Nikki
from Powers.database import add_served_chat

async def new_message(chat_id: int, message: str, reply_markup=None):
    await Nikki.send_message(chat_id=chat_id, text=message, reply_markup=reply_markup)

@Nikki.on_message(filters.new_chat_members)
async def on_new_chat_members(c: Nikki, message: Message):
    await add_served_chat(message.chat.id)
    if (await c.get_me()).id in [user.id for user in message.new_chat_members]:
        added_by = message.from_user.mention if message.from_user else "ᴜɴᴋɴᴏᴡɴ ᴜsᴇʀ"
        title = message.chat.title
        username = f"@{message.chat.username}"
        chat_id = message.chat.id
        Anony = f"**✫** <b><u>ɴᴇᴡ ɢʀᴏᴜᴘ</u></b> **:**\n\n**ᴄʜᴀᴛ ɪᴅ :** {chat_id}\n**ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ :** {username}\n**ᴄʜᴀᴛ ᴛɪᴛʟᴇ :** {title}\n\n**ᴀᴅᴅᴇᴅ ʙʏ :** {added_by}"
        reply_markup = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    message.from_user.first_name,
                    user_id=message.from_user.id
                )
            ]
        ])
        text = f"""ᴛʜᴀɴᴋs ғᴏʀ ᴀᴅᴅɪɴɢ ᴍᴇ ᴛᴏ **{message.chat.title}**

ᴘʀᴏᴍᴏᴛᴇ ᴍᴇ ᴀs ᴀᴅᴍɪɴɪsᴛʀᴀᴛᴏʀ ɪɴ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴏᴛʜᴇʀᴡɪsᴇ ɪ ᴡɪʟʟ ɴᴏᴛ ғᴜɴᴄᴛɪᴏɴ ᴘʀᴏᴘᴇʀʟʏ."""

        buttons = [
            [
                InlineKeyboardButton(text="sᴜᴘᴘᴏʀᴛ ᴄʜᴀᴛ", url="https://t.me/NikkiSupportChat"),
            ],
            [
                InlineKeyboardButton(text="ᴜᴘᴅᴀᴛᴇs ᴄʜᴀɴɴᴇʟ", url="https://t.me/NikkiAssociation"),
            ],
        ]

        await new_message(MESSAGE_DUMP, Anony, reply_markup)
        await new_message(message.chat.id, text, reply_markup=InlineKeyboardMarkup(buttons))

@Nikki.on_message(filters.left_chat_member)
async def on_left_chat_member(c: Nikki, message: Message):
    if (await c.get_me()).id == message.left_chat_member.id:
        remove_by = message.from_user.mention if message.from_user else "ᴜɴᴋɴᴏᴡɴ ᴜsᴇʀ"
        title = message.chat.title
        username = f"@{message.chat.username}"
        chat_id = message.chat.id
        goodbye = f"**✫** <b><u>ʟᴇғᴛ ɢʀᴏᴜᴘ</u></b> **:**\n\n**ᴄʜᴀᴛ ɪᴅ :** {chat_id}\n**ᴄʜᴀᴛ ᴜsᴇʀɴᴀᴍᴇ** : {username}\n**ᴄʜᴀᴛ ᴛɪᴛʟᴇ :** {title}\n\n**ʀᴇᴍᴏᴠᴇᴅ ʙʏ :** {remove_by}"
        reply_markup = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            message.from_user.first_name,
            user_id=message.from_user.id
        )
    ]
])

        await new_message(MESSAGE_DUMP, goodbye, reply_markup)
