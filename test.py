import pymongo
client = pymongo.MongoClient("mongodb+srv://main_user:123pass@ben-demo.hgk7x.mongodb.net/?retryWrites=true&w=majority")
db = client.test_db

db.test_collection.insert_one({"hello":"world"})