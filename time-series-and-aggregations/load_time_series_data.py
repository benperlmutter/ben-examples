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
transactions_db.create_collection('txns', timeseries={ 'timeField': 'timestamp', 'metaField': 'metadata' })
txn_coll = transactions_db.txns

# generate documents

doc = {
	"timestamp": datetime(random.randint(2010, 2021), random.randint(1, 12), random.randint(1, 28)),
	"metadata": {
	"item":"box of cereal",
	"location": "pleasanton",
	"loyalty_number":1234,
	"SKU": 4234239845
	}
}

w = txn_coll.insert_one(doc)
