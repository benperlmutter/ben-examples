import pymongo
import json
from datetime import datetime

# ---------- functions start here ---------- #
def createPartsDocs(num):
	i = 0
	while i < num:
		i += 1
		doc = {
		"partNumber": "P1234",
		"description": "Engine piston",
		"category": "Mechanical",
		"datePutIntoService": datetime(2023, 1, 1),
		"datePulledFromService": None,
		"productsUsedIn": [
		{
		"productId": "PROD123",
		"quantity": 2
		},{
		"productId": "PROD456",
		"quantity": 1
		}
		],
		"updatedAt": datetime(2024, 8, 28),
		}
		return doc

def createBOMDocs(num):
	i = 0
	while i < num:
		i += 1
		doc = {
		"bomName": "Product A BOM",
		"productReleaseDate": datetime(2023, 12, 15),
		"parts": [
		{
		"partId": "P1234", # Reference to the part from the parts master
		"quantity": 2,
		"dateUsed": datetime(2023, 11, 1),
		"dateReleased": datetime(2023, 11, 15),
		},{
		"partId": "P5678",
		"quantity": 1,
		"dateUsed": datetime(2023, 12, 1),
		"dateReleased": datetime(2023, 12, 15)
		}],
		"personas": [
		"Manufacturing Engineer",
		"Procurement Specialist",
		"Quality Assurance"
		],
		"updatedAt": datetime(2024, 8, 28)
		}
		return doc


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

# generate documents
w = parts_col.insert_one(createPartsDocs(1))
y = current_version_boms_col.insert_one(createBOMDocs(1))

# for doc in orders_col.with_options(read_preference=pymongo.ReadPreference.SECONDARY_PREFERRED).find({}):
# 	# w = orders_demo_col.insert_one(readAndProcessDocument(doc))
# 	# print(w.inserted_id)
# 	# new_doc = readAndProcessDocument(doc)
# 	# print(new_doc)
# 	# basket_vector = model.encode(new_doc["basket"]).tolist()

# 	# result_doc['sentence'] = doc
# 	# new_doc['vector_embedding'] = basket_vector
# 	print(doc["created_at"])
# 	# w = orders_original_col.insert_one(doc)
# 	# print(w.inserted_id)
# 	# print(orders_demo_col.find_one({"_id":w.inserted_id}))

