import pymongo
client = pymongo.MongoClient("")
db = client.test_db

db.test_collection.insert_one({"hello":"world"})