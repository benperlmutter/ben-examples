import pymongo
import json
from sentence_transformers import SentenceTransformer, util


query = "stickers, water, burrito"
# query = "B - chicken"
# query = "ice cream, chips, B - chicken"
# query = "chips, Chicken Burrito"
# query = "ice cream"
# query = '{"name": "Cigarettes - Am Sq Turqse B", "quantity": "2"}'
# query = "salad, sandwich, coca cola"
# query = "W-"
#query = "Studying hard, the students prepped for their exams."
#query = "A delicious meal was cooked by the chef."
#query = "Tyson's boxing style was feared for its power and aggression."


# ---------- functions start here ---------- #


# ---------- script starts here ---------- #
f = open('../../atlas-creds/atlas-creds.json')
pData = json.load(f)

bsri_string = pData["bsri-connection-string"]
mdb_string = pData["mdb-connection-string"]


bsri_client = pymongo.MongoClient(bsri_string)
square_db = bsri_client.square
orders_col = square_db.orders

mdb_client = pymongo.MongoClient(mdb_string)
retail_demo_db = mdb_client.retail
orders_demo_col = retail_demo_db.orders

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

vector_query = model.encode(query).tolist()

# print(vector_query)

pipeline = [
    {
        "$search": {
            "knnBeta": {
                "vector": vector_query,
                "path": "vector_embedding",
                "k": 3
            }
        }
    },
    {
    	"$limit": 3
    },
    {
        "$project": {
            "vector_embedding": 0,
            "_id": 0,
            'score': {
                '$meta': 'searchScore'
            }
        }
    }
]

# print('hello world')

results = orders_demo_col.aggregate(pipeline)
# results = orders_demo_col.find({})
# print(results)
for result in results:
	# print(result)
	print("\n")
	print("*************Vector Search Result*****************")
	print(result['basket'])
	print("**************************************************")