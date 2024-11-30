import os

class Config:
    LOGGER = True
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "8109009407:AAHDoEJW4G5ZY1O0-Tf2gs2h6l5GvEZYyys")
    API_ID = int(os.environ.get("API_ID", 28412950))
    API_HASH = os.environ.get("API_HASH", "0bfda840b5f2ea2f4053ba6d8813d351")
    OWNER_ID = int(os.environ.get("OWNER_ID", 6213690669))
    MESSAGE_DUMP = int(os.environ.get("MESSAGE_DUMP", -1001804048226))
    DEV_USERS = os.environ.get("DEV_USERS", "6213690669")
    SUDO_USERS = os.environ.get("SUDO_USERS", "6213690669")
    WHITELIST_USERS = os.environ.get("WHITELIST_USERS", "6213690669")
    SQLURL = os.environ.get("postgres://uckq345i07jr56:p147f8181671593c1966dd721ccb185f9e419fcd06a8a96eb185eaa593a033f8d@cbtilg6vevjp8e.cluster-czz5s0kz4scl.eu-west-1.rds.amazonaws.com:5432/dfhmfrq4iji2m4")
    DB_URI = os.environ.get("DB_URI", "mongodb+srv://GroupSentry:jT6MpjXATacUb2aU@cluster0.4nzkt.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
    DB_NAME = os.environ.get("DB_NAME", "NikkiDB")
    NO_LOAD = os.environ.get("NO_LOAD", "")
    PREFIX_HANDLER = os.environ.get("PREFIX_HANDLER", "/ !")
    SUPPORT_GROUP = os.environ.get("SUPPORT_GROUP", "NikkiSupportChat")
    SUPPORT_CHANNEL = os.environ.get("SUPPORT_CHANNEL", "NikkiAssociation")
    VERSION = os.environ.get("VERSION", "v2")
    TIME_ZONE = os.environ.get("TIME_ZONE", "Asia/Dhaka")
    WORKERS = int(os.environ.get("WORKERS", 8))
