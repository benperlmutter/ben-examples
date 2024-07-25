import pymongo
import json


# ---------- functions start here ---------- #
def readAndProcess(db, col):
	cursor = col.find({})
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
	
	if "line_items" in document:
		for li in document["line_items"]:
			new_string += json.dumps(li)

	new_doc["basket"] = new_string
	return new_doc


# ---------- script starts here ---------- #
f = open('../../atlas-creds/atlas-creds.json')
pData = json.load(f)

mdb_conn_string = pData["mdb-connection-string"]

# mdb_client = pymongo.MongoClient(mdb_conn_string, readPreference='secondaryPreferred')
mdb_client = pymongo.MongoClient(mdb_conn_string)
retail_demo_db = mdb_client.retail
orders_col = retail_demo_db.orders

for doc in orders_col.with_options(read_preference=pymongo.ReadPreference.SECONDARY_PREFERRED).find({}):
	# w = orders_demo_col.insert_one(readAndProcessDocument(doc))
	# print(w.inserted_id)
	# new_doc = readAndProcessDocument(doc)
	# print(new_doc)
	# basket_vector = model.encode(new_doc["basket"]).tolist()

	# result_doc['sentence'] = doc
	# new_doc['vector_embedding'] = basket_vector
	print(doc["created_at"])
	# w = orders_original_col.insert_one(doc)
	# print(w.inserted_id)
	# print(orders_demo_col.find_one({"_id":w.inserted_id}))

