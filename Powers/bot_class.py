from platform import python_version
from threading import RLock
from pyrogram import Client, __version__
from pyrogram.raw.all import layer
from Powers import (LOGGER, MESSAGE_DUMP, NO_LOAD, load_cmds)
from Powers.database import MongoDB
from Powers.plugins import all_plugins
from Config import Config

from Abg import patch

INITIAL_LOCK = RLock()

class Anony(Client):
    def __init__(self):
        super().__init__(
            "Nikki",
            bot_token=Config.BOT_TOKEN,
            plugins=dict(root="Powers.plugins", exclude=NO_LOAD),
            api_id=Config.API_ID,
            api_hash=Config.API_HASH,
            workers=Config.WORKERS,
        )

    async def start(self):
        await super().start()
        self.id = self.me.id
        self.name = self.me.first_name + " " + (self.me.last_name or "")
        self.username = self.me.username
        self.mention = self.me.mention

        startmsg = await self.send_message(MESSAGE_DUMP, "<i>Starting Bot...</i>")
        LOGGER.info(f"Pyrogram v{__version__} (Layer - {layer}) started on {self.username}")
        cmd_list = await load_cmds(await all_plugins())
        LOGGER.info(f"Plugins Loaded: {cmd_list}")
        await startmsg.edit_text(
            f"<b><i>@{self.username} started on Pyrogram v{__version__} (Layer - {layer})</i></b>\n"
            f"\n<b>Python:</b> <u>{python_version()}</u>\n"
            f"\n<b>Loaded Plugins:</b>\n<i>{cmd_list}</i>\n"
        )
        LOGGER.info("Bot Started Successfully!\n")
    async def stop(self):
        await super().stop()
        MongoDB.close()
        LOGGER.info("Bot Stopped.")

Nikki = Anony()
