import pytz
import logging
from Config import Config
from time import time
from importlib import import_module as imp_mod

from telethon import TelegramClient
from telethon.sessions import MemorySession

logging.basicConfig(
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("telethon").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)

TIME_ZONE = pytz.timezone(Config.TIME_ZONE)
MESSAGE_DUMP = Config.MESSAGE_DUMP
SUPPORT_GROUP = Config.SUPPORT_GROUP
SUPPORT_CHANNEL = Config.SUPPORT_CHANNEL
OWNER_ID = Config.OWNER_ID
DEV_USERS = Config.DEV_USERS
SUDO_USERS = Config.SUDO_USERS
WHITELIST_USERS = Config.WHITELIST_USERS
DB_URI = Config.DB_URI
DB_NAME = Config.DB_NAME
NO_LOAD = Config.NO_LOAD
HELP_COMMANDS = {}
UPTIME = time()
SUPPORT_USERS = {"Owner": [Config.OWNER_ID], "Dev": set(Config.DEV_USERS), "Sudo": set(Config.SUDO_USERS), "White": set(Config.WHITELIST_USERS)}










async def load_cmds(all_plugins):
    """Loads all the plugins in bot."""
    for single in all_plugins:
        if single.lower() in [i.lower() for i in Config.NO_LOAD]:
            LOGGER.warning(f"Not loading '{single}' as it's added in NO_LOAD list")
            continue

        imported_module = imp_mod(f"Powers.plugins.{single}")
        if not hasattr(imported_module, "__PLUGIN__"):
            continue

        plugin_name = imported_module.__PLUGIN__.lower()
        plugin_dict_name = f"plugins.{plugin_name}"
        plugin_help = imported_module.__HELP__

        if plugin_dict_name in HELP_COMMANDS:
            raise Exception(
                (
                    "Can't have two plugins with the same name! Please change one\n"
                    f"Error while importing '{imported_module.__name__}'"
                ),
            )

        HELP_COMMANDS[plugin_dict_name] = {
            "buttons": [],
            "disablable": [],
            "alt_cmds": [],
            "help_msg": plugin_help,
        }

        if hasattr(imported_module, "__buttons__"):
            HELP_COMMANDS[plugin_dict_name]["buttons"] = imported_module.__buttons__
        if hasattr(imported_module, "_DISABLE_CMDS_"):
            HELP_COMMANDS[plugin_dict_name][
                "disablable"
            ] = imported_module._DISABLE_CMDS_
        if hasattr(imported_module, "__alt_name__"):
            HELP_COMMANDS[plugin_dict_name]["alt_cmds"] = imported_module.__alt_name__

        (HELP_COMMANDS[plugin_dict_name]["alt_cmds"]).append(plugin_name)

    if NO_LOAD:
        LOGGER.warning(f"Not loading Plugins - {NO_LOAD}")

    return (
        ", ".join((i.split(".")[1]).capitalize() for i in list(HELP_COMMANDS.keys()))
        + "\n"
    )
