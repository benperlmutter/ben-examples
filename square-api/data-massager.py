import pymongo
import json


# ---------- functions start here ---------- #
def readAndProcess(db, col):
	cursor = col.find({}).limit(10)
	for document in cursor:
		new_doc = {
		"order_id": document["order_id"],
		"created_at": document["created_at"],
		"updated_at": document["updated_at"],
		"basket":""}

		new_string = ""
		
		for li in document["line_items"]:
			new_string += json.dumps(li)

		new_doc["basket"] = new_string
		print(new_doc)

def readAndProcessDocument(document):
	new_doc = {
	"order_id": document["order_id"],
	"created_at": document["created_at"],
	"updated_at": document["updated_at"],
	"basket":""}

	new_string = ""
	
	for li in document["line_items"]:
		new_string += json.dumps(li)

	new_doc["basket"] = new_string
	return new_doc



# order_id
# "xwwvVncf4QO9EHvhazGOJ89eV"
# version
# 1
# location_id
# "D4V4SR5CVWE6E"
# created_at
# "2023-01-01T23:59:30Z"
# updated_at
# "2023-01-01T23:59:36Z"



# ---------- script starts here ---------- #
f = open('../../atlas-creds/atlas-creds.json')
pData = json.load(f)

bsri_string = pData["bsri-connection-string"]
mdb_string = pData["mdb-connection-string"]


bsri_client = pymongo.MongoClient(bsri_string)
square_db = bsri_client.square
orders_col = square_db.orders

mdb_client = pymongo.MongoClient(mdb_string)
vector_test_db = mdb_client.vector_tests
orders_demo_col = vector_test_db.orders_demo

for doc in orders_col.find({}).limit(10):
	# w = orders_demo_col.insert_one(readAndProcessDocument(doc))
	# print(w.inserted_id)
	new_doc = readAndProcessDocument(doc)
	# print(new_doc)
	w = orders_demo_col.insert_one(new_doc)
	print(w.inserted_id)
	print(orders_demo_col.find_one({"_id":w.inserted_id}))





# db.orders_col.insert_one({"hello":"world"})

# readAndProcess(square_db, orders_col)

# for doc in readAndProcess(square_db, orders_col):
# 	print(doc)

