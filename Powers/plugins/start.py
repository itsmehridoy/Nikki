from pyrogram.enums import ChatType, ParseMode, ChatMemberStatus as CMS
from pyrogram.errors import MessageNotModified, QueryIdInvalid, UserIsBlocked
from pyrogram.types import (CallbackQuery, InlineKeyboardButton,
                            InlineKeyboardMarkup, Message)

from Powers import HELP_COMMANDS, LOGGER, OWNER_ID
from Powers.bot_class import Nikki
from Powers.utils.kbhelpers import ikb
from Powers.database import add_served_chat, add_served_user
from Powers.utils.start_utils import (gen_cmds_kb, gen_start_kb, get_help_msg,
                                      get_private_note, get_private_rules)

@Nikki.on_cb("close_admin")
async def close_admin_callback(_, q: CallbackQuery):
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
    await q.answer("Closed!", show_alert=True)
    return


@Nikki.on_cmd("start")
async def start(c: Nikki, m: Message):
    if m.chat.type == ChatType.PRIVATE:
        if len(m.text.strip().split()) > 1:
            help_option = (m.text.split(None, 1)[1]).lower()

            if help_option.startswith("note") and (
                help_option not in ("note", "notes")
            ):
                await get_private_note(c, m, help_option)
                return
    
            if help_option.startswith("rules"):
                await get_private_rules(c, m, help_option)
                return

            help_msg, help_kb = await get_help_msg(m, help_option)

            if not help_msg:
                return
            elif help_msg:
                await c.send_message(
                    m.chat.id,
                    help_msg,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=help_kb,
                    disable_web_page_preview=True,
                )
                return
            if len(help_option.split("_",1)) == 2:
                if help_option.split("_")[1] == "help":
                    await c.send_message(
                        m.chat.id,
                        help_msg,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=help_kb,
                    )
                    return
        try:
            cpt = f"""
ʜᴇʏ {m.from_user.mention} 🥀

๏ ᴛʜɪs ɪs {Nikki.mention} !
➻ ᴛʜᴇ ᴍᴏsᴛ ᴩᴏᴡᴇʀғᴜʟ ᴛᴇʟᴇɢʀᴀᴍ ɢʀᴏᴜᴩ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴏᴛ ᴡɪᴛʜ sᴏᴍᴇ ᴀᴡᴇsᴏᴍᴇ ᴀɴᴅ ᴜsᴇғᴜʟ ғᴇᴀᴛᴜʀᴇs.

──────────────────
**๏ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʜᴇʟᴩ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴍʏ ᴍᴏᴅᴜʟᴇs ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅs.**"""

            await c.send_message(
                m.chat.id,
                cpt,
                reply_markup=(await gen_start_kb(m)),
                disable_web_page_preview=True,
            )
            await add_served_user(m.from_user.id)
        except UserIsBlocked:
            LOGGER.warning(f"Bot blocked by {m.from_user.id}")
    else:
      kb = InlineKeyboardMarkup(
        [
          [
            InlineKeyboardButton(
              "Connect me to pm", 
              url=f"https://t.me/{Nikki.username}?start",
            ),
          ],
        ],
      )
        
      await m.reply_text(
        text="Heya :) PM me if you have any questions on how to use me!",
        reply_markup=kb,
        quote=True,
      )
    return await add_served_chat(m.chat.id)

@Nikki.on_cb("start_back")
async def start_back(_, q: CallbackQuery):
    try:
        cpt = f"""
ʜᴇʏ {q.from_user.mention} 🥀

๏ ᴛʜɪs ɪs {Nikki.mention} !
➻ ᴛʜᴇ ᴍᴏsᴛ ᴩᴏᴡᴇʀғᴜʟ ᴛᴇʟᴇɢʀᴀᴍ ɢʀᴏᴜᴩ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ʙᴏᴛ ᴡɪᴛʜ sᴏᴍᴇ ᴀᴡᴇsᴏᴍᴇ ᴀɴᴅ ᴜsᴇғᴜʟ ғᴇᴀᴛᴜʀᴇs.

──────────────────
**๏ ᴄʟɪᴄᴋ ᴏɴ ᴛʜᴇ ʜᴇʟᴩ ʙᴜᴛᴛᴏɴ ᴛᴏ ɢᴇᴛ ɪɴғᴏʀᴍᴀᴛɪᴏɴ ᴀʙᴏᴜᴛ ᴍʏ ᴍᴏᴅᴜʟᴇs ᴀɴᴅ ᴄᴏᴍᴍᴀɴᴅs.**"""

        await q.message.edit_text(
            cpt,
            reply_markup=(await gen_start_kb(q.message)),
        )
    except MessageNotModified:
        pass
    await q.answer()
    return


@Nikki.on_cb("commands")
async def commands_menu(_, q: CallbackQuery):
    ou = await gen_cmds_kb(q.message)
    keyboard = ikb(ou, True)
    try:
        cpt = f"""
➻ Hᴇʏ {q.from_user.mention},

🥀 Cʟɪᴄᴋ Oɴ Bᴇʟᴏᴡ Bᴜᴛᴛᴏɴs Tᴏ Oᴘᴇɴ
Fᴜʟʟ Iɴғᴏʀᴍᴀᴛɪᴏɴ Mᴇɴᴜ ✨..."""

        await q.message.edit_text(
            cpt,
            reply_markup=keyboard,
        )
    except MessageNotModified:
        pass
    except QueryIdInvalid:
        await q.message.edit_text(
            cpt,
            reply_markup=keyboard,
        )

    await q.answer()
    return


@Nikki.on_cmd("help")
async def help_menu(c: Nikki, m: Message):
    if len(m.text.split()) >= 2:
        textt = m.text.replace(" ","_",).replace("_"," ",1)
        help_option = (textt.split(None)[1]).lower()
        help_msg, help_kb = await get_help_msg(m, help_option)

        if not help_msg:
            LOGGER.error(f"No help_msg found for help_option - {help_option}!!")
            return
        if m.chat.type == ChatType.PRIVATE:
            if len(help_msg) >= 1026:
                await c.send_message(
                    m.chat.id,
                    help_msg,
                    parse_mode=ParseMode.MARKDOWN,
                )
            await c.send_message(
                m.chat.id,
                help_msg,
                reply_markup=help_kb,
                parse_mode=ParseMode.MARKDOWN,
            )
        else:
            r_id = m.reply_to_message.id if m.reply_to_message else m.id
            await m.reply_text(
                reply_to_message_id=r_id,
                text=f"Contact me in PM for help on <code>{help_option}</code>!",
                reply_markup=InlineKeyboardMarkup(
                  [
                    [
                      InlineKeyboardButton(
                        "Click me for help!",
                        url=f"t.me/{Nikki.username}?start={help_option}",
                        ),
                    ],
                  ],
                ),
            )
    else:

        if m.chat.type == ChatType.PRIVATE:
            ou = await gen_cmds_kb(m)
            keyboard = ikb(ou, True)
            msg = f"""
➻ Hᴇʏ {m.from_user.mention},

🥀 Cʟɪᴄᴋ Oɴ Bᴇʟᴏᴡ Bᴜᴛᴛᴏɴs Tᴏ Oᴘᴇɴ
Fᴜʟʟ Iɴғᴏʀᴍᴀᴛɪᴏɴ Mᴇɴᴜ ✨..."""
        else:
            keyboard = InlineKeyboardMarkup(
              [
                [
                  InlineKeyboardButton(
                    "Help", 
                    url=f"t.me/{Nikki.username}?start=start_help",
                  ),
                ],
              ],
            )
            msg = "Contact me in PM to get the list of possible commands."

        await c.send_message(
            chat_id=m.chat.id,
            text=msg,
            reply_markup=keyboard,
            protect_content=True,
        )

    return await add_served_chat(m.chat.id)

@Nikki.on_cb("plugins.")
async def get_module_info(c: Nikki, q: CallbackQuery):
    module = q.data.split(".", 1)[1]
    help_msg = HELP_COMMANDS[f"plugins.{module}"]["help_msg"]
    help_kb = HELP_COMMANDS[f"plugins.{module}"]["buttons"]
    await q.message.edit_text(
        help_msg,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=ikb(help_kb,
        True,
        todo="commands"),
    )
    await q.answer()
    return
