import pymongo
import json
from datetime import datetime
import random
import itertools
import array

# ---------- functions start here ---------- #
def createRunDoc(num):

	doc = {
	"sensor":"sensor_"+str(random.randint(99, 999)),
	"metric": random.randint(99999, 999999999),
	"meta" :{
	"run_name":num
	}
	}

	return doc

# ---------- script starts here ---------- #
f = open('../../atlas-creds/atlas-creds.json')
pData = json.load(f)

mdb_conn_string = pData["mdb-refine-connection-string"]

# mdb_client = pymongo.MongoClient(mdb_conn_string, readPreference='secondaryPreferred')
mdb_client = pymongo.MongoClient(mdb_conn_string)
shard_test_db = mdb_client.shard_test
shard_col = shard_test_db.shard_test_coll

total_doc_to_write = 9999999

bulk_array = []

num = 0
bulk_counter = 0
total_counter = 0

while total_counter < total_doc_to_write+1:
	num += 1
	doc = createRunDoc(random.randint(1, 999))
	if bulk_counter < 1000:
		bulk_array.append(doc)
		bulk_counter += 1
		total_counter += 1
	else:
		bulk_array.append(doc)
		y = shard_col.insert_many(bulk_array)
		bulk_array = []
		bulk_counter = 0
		total_counter += 1
	if total_counter == total_doc_to_write:
		y = shard_col.insert_many(bulk_array)

