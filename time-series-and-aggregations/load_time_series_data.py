import pymongo
import json
from datetime import datetime
import random

# ---------- functions start here ---------- #


# ---------- script starts here ---------- #
f = open('../../atlas-creds/atlas-creds.json')
pData = json.load(f)

mdb_conn_string = pData["mdb-connection-string"]

# mdb_client = pymongo.MongoClient(mdb_conn_string, readPreference='secondaryPreferred')
mdb_client = pymongo.MongoClient(mdb_conn_string)
transactions_db = mdb_client.transactions

# create time series collection if necessary
# transactions_db.create_collection('txns', timeseries={ 'timeField': 'timestamp', 'metaField': 'metadata' })

txn_coll = transactions_db.txns

# generate documents
counter = 0
total_counter = 0
total_docs_number = 9999
doc_array = []

while total_counter < total_docs_number:
	counter += 1
	total_counter += 1
	doc = {
		"timestamp": datetime(random.randint(2010, 2021), random.randint(1, 12), random.randint(1, 28)),
		"metadata": {
		"item":"box of cereal",
		"location": "pleasanton",
		"loyalty_number":1234,
		"SKU": 4234239845
		}
	}
	doc_array.append(doc)
	if len(doc_array) > 999:
		w = txn_coll.insert_many(doc_array)
		doc_array = []
		counter = 0
	elif total_counter == total_docs_number:
		w = txn_coll.insert_many(doc_array)

