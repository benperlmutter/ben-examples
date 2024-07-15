import pymongo
import json
from datetime import datetime

# ---------- functions start here ---------- #


# ---------- script starts here ---------- #
f = open('../../atlas-creds/atlas-creds.json')
pData = json.load(f)

mdb_string = pData["mdb-connection-string"]
mdb_string = pData["mongodump2-connection-string"]


mdb_client = pymongo.MongoClient(mdb_string)
retail_demo_db = mdb_client.retail
orders_demo_col = retail_demo_db.orders

dateFrom = datetime(2024, 7, 3)

# results = orders_demo_col.delete_many({"created_at": {"$lt": dateFrom}})
results = orders_demo_col.delete_many({"created_at": {"$gt": dateFrom}})
# results = orders_demo_col.delete_many({"created_at":{"$type": "string"}})
# results = orders_demo_col.find({})
# print(results)
print(results)