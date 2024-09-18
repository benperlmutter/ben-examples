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
part_docs = 4
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

	w = parts_col.insert_many([piston, crankshaft, cylinderhead, suspension, rear_axle, front_axle, clutch, gearbox, doors, windows, roof])
