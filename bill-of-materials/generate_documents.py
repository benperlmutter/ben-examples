import pymongo
import json
from datetime import datetime
import random

# ---------- functions start here ---------- #
def createPart(category, parent_part, part, lower_weight, higher_weight, num):
	datePulled = datetime(random.randint(2022, 2023), random.randint(1, 12), random.randint(1, 28))
	datePulledArray = [datePulled, None]
	doc = {
	"partNumber": parent_part.upper()+"_"+part.upper()+"_"+"100"+str(num),
	"description": parent_part+" "+part,
	"weight_kg":random.randint(lower_weight, higher_weight),
	"category": category,
	"datePutIntoService": datetime(random.randint(2010, 2021), random.randint(1, 12), random.randint(1, 28)),
	"datePulledFromService": datePulledArray[random.randint(0, 1)],
	"updatedAt": datetime(2024, random.randint(1, 8), random.randint(1, 28)),
	}
	return doc

def createBOMDoc(part_dict):
	bom_parts_matrix = []
	bom_array = []
	i = 0
	for array in part_matrix: #create array of just parts info for BOMs
		parts_array = []
		for part in array:
			bom_part = {
			"partNumber": part["partNumber"],
			"quantity": random.randint(1, 4),
			"datePutIntoService": part["datePutIntoService"],
			"datePulledFromService": part["datePulledFromService"]
			}
			parts_array.append(bom_part)
		bom_parts_matrix.append(parts_array)
	for bom_part_array in bom_parts_matrix:
		i += 1
		doc = {
		"bomName": "BOM"+"_"+str(i),
		"productReleaseDate": datetime(random.randint(2022, 2023), random.randint(1, 12), random.randint(1, 28)),
		"parts": bom_part_array,
		"personas":[],
		"updatedAt": datetime(2024, random.randint(1, 8), random.randint(1, 28))
		}
		bom_array.append(doc)
	return bom_array

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
part_docs = 2
i = 1
part_dict = {"piston":[],"crankshaft":[],"cylinderhead":[],"suspension":[],"rear_axle":[],"front_axle":[],"clutch":[],"gearbox":[],"doors":[],"windows":[],"roof":[]}
while i < part_docs+1:
	i+=1
	doc_array = []
	piston = createPart("Mechanical", "Engine", "Piston", 3, 9, i)
	part_dict["piston"].append(piston)

	crankshaft = createPart("Mechanical", "Engine", "Crankshaft", 6, 20, i)
	part_dict["crankshaft"].append(crankshaft)

	cylinderhead = createPart("Mechanical", "Engine", "Cylinderhead", 1, 5, i)
	part_dict["cylinderhead"].append(cylinderhead)

	suspension = createPart("Mechanical", "Chassis", "Suspension", 20, 30, i)
	part_dict["suspension"].append(suspension)

	rear_axle = createPart("Mechanical", "Chassis", "Rear_Axle", 20, 30, i)
	part_dict["rear_axle"].append(rear_axle)

	front_axle = createPart("Mechanical", "Chassis", "Front_Axle", 20, 30, i)
	part_dict["front_axle"].append(front_axle)

	clutch = createPart("Mechanical", "Transmission", "Clutch", 15, 25, i)
	part_dict["clutch"].append(clutch)

	gearbox = createPart("Mechanical", "Transmission", "Gearbox", 25, 45, i)
	part_dict["gearbox"].append(gearbox)

	doors = createPart("Exterior", "Body", "Doors", 20, 25, i)
	part_dict["doors"].append(doors)

	windows = createPart("Exterior", "Body", "Windows", 3, 9, i)
	part_dict["windows"].append(windows)

	roof = createPart("Exterior", "Body", "Roof", 40, 50, i)
	part_dict["roof"].append(roof)

	# w = parts_col.insert_many([piston, crankshaft, cylinderhead, suspension, rear_axle, front_axle, clutch, gearbox, doors, windows, roof])
# y = current_version_boms_col.insert_many(createBOMDoc(part_matrix))


# y = current_version_boms_col.insert_one(createBOMDocs(1))

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

