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
transactions_db.create_collection('txns', timeseries={ 'timeField': 'timestamp', 'metaField': 'metadata' })

txn_coll = transactions_db.txns

item_list = ["box of cereal","sodapop","loaf of bread","chips","salsa","milk","eggs","whole chicken","salmon fillet"]
location_list = ["ocean beach","castro","marina","western addition","andronicos on clement"]

# generate documents
counter = 0
total_counter = 0
total_docs_number = 999999
doc_array = []

while total_counter < total_docs_number:
	counter += 1
	total_counter += 1
	item_number = random.randint(0, len(item_list)-1)
	location_number = random.randint(0, len(location_list)-1)
	item_price = round(random.uniform(1, 10), 2)
	doc = {
		"timestamp": datetime(random.randint(2010, 2021), random.randint(1, 12), random.randint(1, 28)),
		"metadata": {
		"item":item_list[item_number],
		"price": item_price,
		"location": location_list[location_number],
		"loyalty_number":random.randint(9999, 99999),
		"SKU": random.randint(9999999, 99999999)
		}
	}
	doc_array.append(doc)
	if len(doc_array) > 999:
		w = txn_coll.insert_many(doc_array)
		doc_array = []
		counter = 0
	elif total_counter == total_docs_number:
		w = txn_coll.insert_many(doc_array)

