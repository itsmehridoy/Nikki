from asyncio import gather
from httpx import AsyncClient, Timeout
from pyrogram.filters import user

from Powers import OWNER_ID, SUPPORT_USERS
from Powers.database.support_db import SUPPORTS

SUDOERS = user(OWNER_ID)

async def load_support_users():
    support = SUPPORTS()
    for i in SUPPORT_USERS["Dev"]:
        support.insert_support_user(int(i), "dev")
    for i in SUPPORT_USERS["Sudo"]:
        support.insert_support_user(int(i), "sudo")
    for i in SUPPORT_USERS["White"]:
        support.insert_support_user(int(i), "whitelist")
    return


def get_support_staff(want="all"):
    """
    dev, sudo, whitelist, dev_level, sudo_level, all
    """
    support = SUPPORTS()
    if want in ["dev", "dev_level"]:
        devs = SUPPORT_USERS["Dev"] or support.get_particular_support("dev")
        wanted = list(devs) 
        if want == "dev_level":
            wanted.append(OWNER_ID)
    elif want == "sudo":
        sudo = SUPPORT_USERS["Sudo"] or support.get_particular_support("sudo")
        wanted = list(sudo)
    elif want == "whitelist":
        whitelist = SUPPORT_USERS["White"] or support.get_particular_support("whitelist")
        wanted = list(whitelist)
    elif want == "sudo_level":
        devs = SUPPORT_USERS["Dev"] or support.get_particular_support("dev")
        sudo = SUPPORT_USERS["Sudo"] or support.get_particular_support("sudo")
        wanted = list(sudo) + list(devs) + [OWNER_ID]
    else:
        devs = SUPPORT_USERS["Dev"] or support.get_particular_support("dev")
        sudo = SUPPORT_USERS["Sudo"] or support.get_particular_support("sudo")
        whitelist = SUPPORT_USERS["White"] or support.get_particular_support("whitelist")
        wanted = list(set([int(OWNER_ID)] + list(devs) + list(sudo) + list(whitelist)))

    return wanted or []


async def cache_support():
    support = SUPPORTS()
    dev = support.get_particular_support("dev")
    devs = set(dev)
    sudo = set(support.get_particular_support("sudo"))
    SUPPORT_USERS["Dev"] = SUPPORT_USERS["Dev"].union(devs)
    SUPPORT_USERS["Sudo"] = SUPPORT_USERS["Sudo"].union(sudo)
    return

# HTTPx Async Client
fetch = AsyncClient(
    verify=False,
    headers={
        "Accept-Language": "en-US,en;q=0.9,id-ID;q=0.8,id;q=0.7",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 Edge/107.0.1418.42",
    },
    timeout=Timeout(20),
)
