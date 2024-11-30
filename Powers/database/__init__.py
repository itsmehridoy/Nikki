from pymongo import MongoClient
from pymongo.errors import PyMongoError

from Powers import DB_NAME, DB_URI, LOGGER

try:
    Powers_db_client = MongoClient(DB_URI)
except PyMongoError as e:
    LOGGER.error(f"Error in Mongodb: {e}")
    exit(1)

Powers_main_db = Powers_db_client[DB_NAME]

class MongoDB:
    def __init__(self, collection):
        self.collection = Powers_main_db[collection]

    def insert_one(self, document):
        result = self.collection.insert_one(document)
        return str(result.inserted_id)

    def find_one(self, query):
        result = self.collection.find_one(query)
        return result if result else False

    def find_all(self, query=None):
        if query is None:
            query = {}
        return list(self.collection.find(query))

    def count(self, query=None):
        if query is None:
            query = {}
        return self.collection.count_documents(query)

    def delete_one(self, query):
        self.collection.delete_many(query)
        return self.collection.count_documents({})

    def replace(self, query, new_data):
        old = self.collection.find_one(query)
        _id = old["_id"]
        self.collection.replace_one({"_id": _id}, new_data)
        new = self.collection.find_one({"_id": _id})
        return old, new

    def update(self, query, update):
        result = self.collection.update_one(query, {"$set": update})
        new_document = self.collection.find_one(query)
        return result.modified_count, new_document

    @staticmethod
    def close():
        return Powers_db_client.close()

def connect_first():
    _ = MongoDB("test")
    LOGGER.info("Initialized Database!\n")

connect_first()

#For motor client database.
from Powers.database.tools import *
