import pymongo
import json
from sentence_transformers import SentenceTransformer, util


query = "The cook prepared a meal of poultry and veggies."
#query = "The pupils worked hard for their test."
#query = "Studying hard, the students prepped for their exams."
#query = "A delicious meal was cooked by the chef."
#query = "Tyson's boxing style was feared for its power and aggression."


results = db.vectors_demo_1.aggregate(pipeline)
for result in results:
    print("\n")
    print("*************Vector Search Result*****************")
    print(result['sentence'])
    print("**************************************************")


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

# model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

# for doc in orders_col.find({}).limit(10):
# 	# w = orders_demo_col.insert_one(readAndProcessDocument(doc))
# 	# print(w.inserted_id)
# 	new_doc = readAndProcessDocument(doc)
# 	# print(new_doc)
# 	basket_vector = model.encode(new_doc["basket"]).tolist()

# 	# result_doc['sentence'] = doc
# 	new_doc['vector_embedding'] = basket_vector

# 	result = orders_demo_col.insert_one(new_doc)
# 	print(result.inserted_id)
# 	print(orders_demo_col.find_one({"_id":result.inserted_id}))

vector_query = model.encode(query).tolist()

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
        "$limit": 1
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

results = vector_test_db.orders_demo_col.aggregate(pipeline)
for result in results:
    print("\n")
    print("*************Vector Search Result*****************")
    print(result['basket'])
    print("**************************************************")