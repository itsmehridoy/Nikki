from Powers import LOGGER
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_DB_URI = "mongodb+srv://Mrs:Nikki@cluster0.nlh0bzz.mongodb.net/?retryWrites=true&w=majority"

LOGGER.info("Connecting to your second Mongo Database...")
try:
    _mongo_async_ = AsyncIOMotorClient(MONGO_DB_URI)
    db = _mongo_async_.Anony
    LOGGER.info("Connected to your second Mongo Database.")
except:
    LOGGER.error("Failed to connect to your second Mongo Database.")
    exit()
