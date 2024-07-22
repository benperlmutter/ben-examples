import pymongo
import json
import re
from sentence_transformers import SentenceTransformer, util


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

def readAndProcessBasket(document):
	basket = document["basket"]
	txt = ""
	txt = re.search("B - ", basket)
	new_txt = ""
	if txt != None:
		new_txt = basket.replace("B - ", "Burrito ")
		# print(new_txt)
	if new_txt != "":
		document["basket"] = new_txt

	return document


# ---------- script starts here ---------- #
f = open('../../atlas-creds/atlas-creds.json')
pData = json.load(f)

# bsri_string = pData["bsri-connection-string"]
mdb_string = pData["mdb-connection-string"]


# bsri_client = pymongo.MongoClient(bsri_string)
# square_db = bsri_client.square
# orders_col = square_db.orders

mdb_client = pymongo.MongoClient(mdb_string)
retail_demo_db = mdb_client.retail
orders_demo_col = retail_demo_db.orders_updated_baskets

other_col = retail_demo_db.another_copy5

# model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

doc_array = []
counter = 0
total_count = 0

# print(orders_demo_col.find({}).explain()["executionStats"]["nReturned"])

num_docs = orders_demo_col.find({}).explain()["executionStats"]["nReturned"]

for doc in orders_demo_col.find({}):
	# w = orders_demo_col.insert_one(readAndProcessDocument(doc))
	# print(w.inserted_id)
	# new_doc = readAndProcessBasket(doc)
	doc_array.append(doc)
	counter += 1
	total_count += 1

	if counter > 999 or total_count > (num_docs-3):
		w = other_col.insert_many(doc_array)
		print(w)
		doc_array = []
		counter = 0
	# print(new_doc)
	# basket_vector = model.encode(new_doc["basket"]).tolist()

	# result_doc['sentence'] = doc
	# new_doc['vector_embedding'] = basket_vector
	# print(new_doc)
	# w = orders_burrito_col.insert_one(new_doc)
	# print(w.inserted_id)
	# print(orders_demo_col.find_one({"_id":w.inserted_id}))

