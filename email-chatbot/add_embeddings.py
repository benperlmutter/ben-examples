import pymongo
import json
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
	"date": document["date"],
	"thread_id": document["thread_id"],
	"sender": document["sender"],
	"thread_message": document["thread_message"],
	"message_embeddings":""}
	
	return new_doc


# ---------- script starts here ---------- #
f = open('../../atlas-creds/atlas-creds.json')
pData = json.load(f)

mdb_string = pData["mdb-connection-string"]

mdb_client = pymongo.MongoClient(mdb_string)
event_emails_db = mdb_client.event_emails
og_emails_col = event_emails_db.og_emails
embedded_emails_col = event_emails_db.embedded_emails

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

for doc in og_emails_col.find({}):
	# w = orders_demo_col.insert_one(readAndProcessDocument(doc))
	# print(w.inserted_id)
	new_doc = readAndProcessDocument(doc)
	# print(new_doc)
	message_vector = model.encode(new_doc["thread_message"]).tolist()

	# result_doc['sentence'] = doc
	new_doc['message_embeddings'] = message_vector

	# print(new_doc)

	w = embedded_emails_col.insert_one(new_doc)
	# print(w.inserted_id)
	# print(orders_demo_col.find_one({"_id":w.inserted_id}))

