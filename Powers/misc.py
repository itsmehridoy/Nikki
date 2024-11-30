import socket
import heroku3

from pyrogram.filters import user

from Config import Config
from Powers import (LOGGER, DEV_USERS, WHITELIST_USERS,
                    OWNER_ID, SUDO_USERS)
from Powers.database.support_db import SUPPORTS

SUDOERS = user(OWNER_ID)

HAPP = None

async def load_support_users():
    support = SUPPORTS()
    for i in DEV_USERS:
        support.insert_support_user(int(i),"dev")
    for i in SUDO_USERS:
        support.insert_support_user(int(i),"sudo")
    for i in WHITELIST_USERS:
        support.insert_support_user(int(i),"whitelist")
    return

def get_support_staff(want = "all"):
    """
    dev, sudo, whitelist, dev_level, sudo_level, all
    """
    support = SUPPORTS()
    devs = support.get_particular_support("dev")
    sudo = support.get_particular_support("sudo")
    whitelist = support.get_particular_support("whitelist")

    if want in ["dev","dev_level"]:
        wanted = devs
    elif want == "sudo":
        wanted = sudo
    elif want == "whitelist":
        wanted = whitelist
    elif want == "sudo_level":
        wanted = sudo + devs
    else:
        wanted = list(set([int(OWNER_ID)] + devs + sudo + whitelist))

    return wanted


def is_heroku():
    return "heroku" in socket.getfqdn()


XCB = [
    "/",
    "@",
    ".",
    "com",
    ":",
    "git",
    "heroku",
    "push",
    str(Config.HEROKU_API_KEY),
    "https",
    str(Config.HEROKU_APP_NAME),
    "HEAD",
    "master",
]

def heroku():
    global HAPP
    if is_heroku:
        if Config.HEROKU_API_KEY and Config.HEROKU_APP_NAME:
            try:
                Heroku = heroku3.from_key(Config.HEROKU_API_KEY)
                HAPP = Heroku.app(Config.HEROKU_APP_NAME)
                LOGGER.info(f"Heroku App Configured")
            except BaseException:
                LOGGER.warning(
                    f"Please make sure your Heroku API Key and Your App name are configured correctly in the heroku."
                )
