import pymongo
import json

# ---------- functions start here ---------- #
def readAndProcess(db, col):
	cursor = col.find({}).limit(10)
	for document in cursor:
		print(document)



# ---------- script starts here ---------- #
f = open('../../atlas-creds/atlas-creds.json')
pData = json.load(f)

conn_string = pData["bsri-connection-string"]

client = pymongo.MongoClient(conn_string)
square_db = client.square
orders_col = square_db.orders

# db.orders_col.insert_one({"hello":"world"})

readAndProcess(square_db, orders_col)

