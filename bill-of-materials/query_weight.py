import pymongo
import json
from datetime import datetime
import random
import sys
import time

# ---------- functions start here ---------- #

# ---------- script starts here ---------- #
f = open('../../atlas-creds/atlas-creds.json')
pData = json.load(f)

mdb_conn_string = pData["mdb-connection-string"]

# mdb_client = pymongo.MongoClient(mdb_conn_string, readPreference='secondaryPreferred')
mdb_client = pymongo.MongoClient(mdb_conn_string)
bom_demo_db = mdb_client.bom
parts_col = bom_demo_db.parts
current_version_boms_col = bom_demo_db.current_version_boms
persona_boms_col = bom_demo_db.persona_boms
bomName = ""

if len(sys.argv) > 1:
	bomName = sys.argv[1]

# agg pipeline
pipeline_with_match = [
{
        '$match': {
            'bomName': bomName
        }
    }, {
        '$unwind': {
            'path': '$parts'
        }
    }, {
        '$project': {
            'bomName': 1, 
            'parts': 1, 
            'parts_weight': {
                '$multiply': [
                    '$parts.quanity', '$parts.weight_kg'
                ]
            }
        }
    }, {
        '$group': {
            '_id': '$bomName', 
            'bomWeight': {
                '$sum': '$parts_weight'
            }
        }
    }
  ]

pipeline = [
    {
        '$unwind': {
            'path': '$parts'
        }
    }, {
        '$project': {
            'bomName': 1, 
            'parts_weight': {
                '$multiply': [
                    '$parts.quanity', '$parts.weight_kg'
                ]
            }
        }
    }, {
        '$group': {
            '_id': '$bomName', 
            'bomWeight': {
                '$sum': '$parts_weight'
            }
        }
    }
]

# run query
start_time = time.perf_counter()

if len(sys.argv) > 1:
	print(list(current_version_boms_col.aggregate(pipeline_with_match)))
else:
	print(list(current_version_boms_col.aggregate(pipeline)))

print("--- %s seconds ---" % (time.perf_counter() - start_time))
