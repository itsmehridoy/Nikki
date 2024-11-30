import asyncio
import os
import re
import shutil
import tempfile

from PIL import Image
from pyrogram import Client, emoji, enums
from pyrogram.errors import BadRequest, PeerIdInvalid, StickersetInvalid
from pyrogram.file_id import FileId
from pyrogram.raw.functions.messages import GetStickerSet, SendMedia
from pyrogram.raw.functions.stickers import (
    AddStickerToSet,
    CreateStickerSet,
    RemoveStickerFromSet,
)
from pyrogram.raw.types import (
    DocumentAttributeFilename,
    InputDocument,
    InputMediaUploadedDocument,
    InputStickerSetItem,
    InputStickerSetShortName,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from Powers import MESSAGE_DUMP
from Powers.bot_class import Nikki

def get_emoji_regex():
    e_list = [
        getattr(emoji, e).encode("unicode-escape").decode("ASCII")
        for e in dir(emoji)
        if not e.startswith("_")
    ]
    e_sort = sorted([x for x in e_list if not x.startswith("*")], reverse=True)
    pattern_ = f"({'|'.join(e_sort)})"
    return re.compile(pattern_)

EMOJI_PATTERN = get_emoji_regex()
SUPPORTED_TYPES = ["jpeg", "png", "webp"]

@Nikki.on_cmd("getsticker")
async def getsticker_(self: Client, ctx: Message):
    if not ctx.reply_to_message:
        return await ctx.reply_msg("Please reply to a sticker for me to upload its PNG.")
    sticker = ctx.reply_to_message.sticker
    if not sticker:
        return await ctx.reply_msg("Only support sticker..")
    if sticker.is_animated:
        return await ctx.reply_msg("Animated stickers are not supported.")
    with tempfile.TemporaryDirectory() as tempdir:
        path = os.path.join(tempdir, "getsticker")
        sticker_file = await self.download_media(
            message=ctx.reply_to_message,
            file_name=f"{path}/{sticker.set_name}.png",
        )
        await ctx.reply_to_message.reply_document(
            document=sticker_file,
            caption=f"<b>Emoji:</b> {sticker.emoji}\n"
            f"<b>Sticker ID:</b> <code>{sticker.file_id}</code>\n\n"
            f"<b>Send by:</b> @{self.me.username}",
        )
    shutil.rmtree(tempdir, ignore_errors=True)

@Nikki.on_cmd("stickerid")
async def getstickerid(_, ctx: Message):
    if ctx.reply_to_message and ctx.reply_to_message.sticker:
        await ctx.reply_msg(
            "The ID of this sticker is: <code>{stickerid}</code>".format(
                stickerid=ctx.reply_to_message.sticker.file_id
            )
        )
    else:
        await ctx.reply_text("Please reply to a sticker to get its ID.")

@Nikki.on_cmd(["unkang", "delsticker"])
async def unkangs(self: Client, ctx: Message):
    if not ctx.from_user:
        return await ctx.reply("You're anonymous; un-kang in my PM.")

    if ctx.reply_to_message and ctx.reply_to_message.sticker:
        sticker = ctx.reply_to_message.sticker
        if str(ctx.from_user.id) not in sticker.set_name:
            return await ctx.reply("This sticker is not from your pack; please don't un-kang it.")
        
        pp = await ctx.reply("Unkanging the sticker...")
        try:
            decoded = FileId.decode(sticker.file_id)
            sticker = InputDocument(
                id=decoded.media_id,
                access_hash=decoded.access_hash,
                file_reference=decoded.file_reference,
            )
            await Nikki.invoke(RemoveStickerFromSet(sticker=sticker))
            await pp.edit("Unkanging successful.")
        except Exception as e:
            await pp.edit(f"Unkanging error: {e}")
    else:
        await ctx.reply("Please reply to a sticker from your sticker pack.")

@Nikki.on_cmd(["curi", "kang"])
async def kang_sticker(self, ctx: Message):
    if not ctx.from_user:
        return await ctx.reply("You need to use this command in a chat.", delete_in=6)

    prog_msg = await ctx.reply("Kanging the sticker...")

    sticker_emoji = "🤔"
    packnum = 0
    packname_found = False
    resize = False
    animated = False
    videos = False
    convert = False

    reply = ctx.reply_to_message
    user = await self.resolve_peer(ctx.from_user.username or ctx.from_user.id)

    if reply and reply.media:
        if reply.photo:
            resize = True
        elif reply.animation:
            videos = True
            convert = True
        elif reply.video:
            convert = True
            videos = True
        elif reply.document:
            if "image" in reply.document.mime_type:
                resize = True
            elif reply.document.mime_type in ("video", "animation"):
                videos = True
                convert = True
            elif "tgsticker" in reply.document.mime_type:
                animated = True
        elif reply.sticker:
            if not reply.sticker.file_name:
                return await prog_msg.edit("The sticker has no name.")
            if reply.sticker.emoji:
                sticker_emoji = reply.sticker.emoji
            animated = reply.sticker.is_animated
            videos = reply.sticker.is_video
            if videos:
                convert = False
            elif not reply.sticker.file_name.endswith(".tgs"):
                resize = True
        else:
            return await prog_msg.edit("Unsupported media type.")

        pack_prefix = "anim" if animated else "vid" if videos else "a"
        packname = f"{pack_prefix}_{ctx.from_user.id}_by_{self.me.username}"

        if len(ctx.command) > 1 and ctx.command[1].isdigit() and int(ctx.command[1]) > 0:
            packnum = ctx.command.pop(1)
            packname = f"{pack_prefix}{packnum}_{ctx.from_user.id}_by_{self.me.username}"

        if len(ctx.command) > 1:
            sticker_emoji = "".join(set(EMOJI_PATTERN.findall("".join(ctx.command[1:]))) or sticker_emoji)

        filename = await self.download_media(ctx.reply_to_message)
        if not filename:
            await prog_msg.delete()
            return
    else:
        return await prog_msg.edit("You need to reply to a sticker or provide a valid image URL.")

    try:
        if resize:
            filename = resize_image(filename)
        elif convert:
            filename = await convert_video(filename)
            if filename is False:
                return await prog_msg.edit("Error", delete_in=6)

        max_stickers = 50 if animated else 120

        while not packname_found:
            try:
                stickerset = await self.invoke(
                    GetStickerSet(
                        stickerset=InputStickerSetShortName(short_name=packname),
                        hash=0,
                    )
                )
                if stickerset.set.count >= max_stickers:
                    packnum += 1
                    packname = f"{pack_prefix}_{packnum}_{ctx.from_user.id}_by_{self.me.username}"
                else:
                    packname_found = True
            except StickersetInvalid:
                break

        file = await self.save_file(filename)
        media = await self.invoke(
            SendMedia(
                peer=(await self.resolve_peer(MESSAGE_DUMP)),
                media=InputMediaUploadedDocument(
                    file=file,
                    mime_type=self.guess_mime_type(filename),
                    attributes=[DocumentAttributeFilename(file_name=filename)],
                ),
                message=f"#Sticker kang by UserID -> {ctx.from_user.id}",
                random_id=self.rnd_id(),
            ),
        )

        msg_ = media.updates[-1].message
        stkr_file = msg_.media.document

        if packname_found:
            await prog_msg.edit("Using existing sticker pack...")
            await self.invoke(
                AddStickerToSet(
                    stickerset=InputStickerSetShortName(short_name=packname),
                    sticker=InputStickerSetItem(
                        document=InputDocument(
                            id=stkr_file.id,
                            access_hash=stkr_file.access_hash,
                            file_reference=stkr_file.file_reference,
                        ),
                        emoji=sticker_emoji,
                    ),
                )
            )
        else:
            await prog_msg.edit("Creating a new pack and adding the sticker...")
            stkr_title = f"{ctx.from_user.first_name}'s"
            if animated:
                stkr_title += "AnimPack"
            elif videos:
                stkr_title += "VidPack"
            if packnum != 0:
                stkr_title += f" v{packnum}"

            try:
                await self.invoke(
                    CreateStickerSet(
                        user_id=user,
                        title=stkr_title,
                        short_name=packname,
                        stickers=[
                            InputStickerSetItem(
                                document=InputDocument(
                                    id=stkr_file.id,
                                    access_hash=stkr_file.access_hash,
                                    file_reference=stkr_file.file_reference,
                                ),
                                emoji=sticker_emoji,
                            )
                        ],
                        animated=animated,
                        videos=videos,
                    )
                )
            except PeerIdInvalid:
                return await prog_msg.edit(
                    "To use this feature, please start a private chat with me.",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "Start Chat",
                                    url=f"https://t.me/{self.me.username}?start",
                                )
                            ]
                        ]
                    ),
                )

    except BadRequest:
        return await prog_msg.edit("Your Sticker Pack is full if your pack is not in v1 Type /kang 1, if it is not in v2 Type /kang 2 and so on.")
    except Exception as all_e:
        await prog_msg.edit(f"{all_e.__class__.__name__} : {all_e}")
    else:
        markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "View Pack",
                        url=f"https://t.me/addstickers/{packname}",
                    )
                ]
            ]
        )
        await prog_msg.edit(f"Sticker added successfully. {sticker_emoji}", reply_markup=markup)
        await self.delete_messages(
            chat_id=MESSAGE_DUMP, message_ids=msg_.id, revoke=True
        )
        try:
            os.remove(filename)
        except OSError:
            pass

def resize_image(filename: str) -> str:
    im = Image.open(filename)
    maxsize = 512
    scale = maxsize / max(im.width, im.height)
    sizenew = (int(im.width * scale), int(im.height * scale))
    im = im.resize(sizenew, Image.NEAREST)
    downpath, f_name = os.path.split(filename)
    # not hardcoding png_image as "sticker.png"
    png_image = os.path.join(downpath, f"{f_name.split('.', 1)[0]}.png")
    im.save(png_image, "PNG")
    if png_image != filename:
        os.remove(filename)
    return png_image


async def convert_video(filename: str) -> str:
    downpath, f_name = os.path.split(filename)
    webm_video = os.path.join(downpath, f"{f_name.split('.', 1)[0]}.webm")
    cmd = [
        "ffmpeg",
        "-loglevel",
        "quiet",
        "-i",
        filename,
        "-t",
        "00:00:03",
        "-vf",
        "fps=30",
        "-c:v",
        "vp9",
        "-b:v:",
        "500k",
        "-preset",
        "ultrafast",
        "-s",
        "512x512",
        "-y",
        "-an",
        webm_video,
    ]

    proc = await asyncio.create_subprocess_exec(*cmd)
    await proc.communicate()

    if webm_video != filename:
        os.remove(filename)
    return webm_video

__PLUGIN__ = "Sᴛɪᴄᴋᴇʀ"
__HELP__ = """
**Dᴇsᴄʀɪᴘᴛɪᴏɴ :**
ʜᴇʀᴇ sᴏᴍᴇ ᴇxᴛʀᴀ ᴄᴏᴍᴍᴀɴᴅ ғᴏʀ ᴛʜɪs ʙᴏᴛ.

**Cᴏᴍᴍᴀɴᴅs :**
• /stickerid : ʀᴇᴘʟʏ ᴛᴏ ᴀ ꜱᴛɪᴄᴋᴇʀ ᴛᴏ ᴍᴇ ᴛᴏ ᴛᴇʟʟ ʏᴏᴜ ɪᴛꜱ ғɪʟᴇ ɪᴅ.
• /getsticker : ʀᴇᴘʟʏ ᴛᴏ ᴀ ꜱᴛɪᴄᴋᴇʀ ᴛᴏ ᴍᴇ ᴛᴏ ᴜᴘʟᴏᴀᴅ ɪᴛꜱ ʀᴀᴡ ᴘɴɢ ғɪʟᴇ.
• /kang : ʀᴇᴘʟʏ ᴛᴏ ᴀ ꜱᴛɪᴄᴋᴇʀ ᴛᴏ ᴀᴅᴅ ɪᴛ ᴛᴏ ʏᴏᴜʀ ᴘᴀᴄᴋ.  ɪᴍɢ, ɢɪғ, ᴘʜᴏᴛᴏ
• /delsticker : ʀᴇᴘʟʏ ᴛᴏ ʏᴏᴜʀ ᴀɴɪᴍᴇ ᴇxɪꜱᴛ ꜱᴛɪᴄᴋᴇʀ ᴛᴏ ʏᴏᴜʀ ᴘᴀᴄᴋ ᴛᴏ ᴅᴇʟᴇᴛᴇ ɪᴛ.
• /stickers : ғɪɴᴅ ꜱᴛɪᴄᴋᴇʀꜱ ғᴏʀ ɢɪᴠᴇɴ ᴛᴇʀᴍ ᴏɴ ᴄᴏᴍʙᴏᴛ ꜱᴛɪᴄᴋᴇʀ ᴄᴀᴛᴀʟᴏɢᴜᴇ."""
