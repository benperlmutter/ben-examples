import pymongo
import json

f = open('../../atlas-creds/atlas-creds.json')
pData = json.load(f)

conn_string = pData["bsri-connection-string"]

client = pymongo.MongoClient(conn_string)
db = client.test_db

db.test_collection.insert_one({"hello":"world"})

