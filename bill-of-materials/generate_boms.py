import pymongo
import json
from datetime import datetime
import random
import itertools
import array

# ---------- functions start here ---------- #
def createPartsDoc(part):
	quantity = 1
	if part["description"] == "Engine Piston":
		quantity = random.randint(3, 12)
	elif part["description"] == "Engine Crankshaft":
		quantity = random.randint(1, 2)
	elif part["description"] == "Engine Cylinderhead":
		quantity = random.randint(3, 12)
	elif part["description"] == "Chassis Suspension":
		quantity = 4 
	elif part["description"] == "Chassis Rear_Axle":
		quantity = 2
	elif part["description"] == "Chassis Front_Axle":
		quantity = 2
	elif part["description"] == "Body Doors":
		quantity = random.randint(2, 5)
	elif part["description"] == "Body Windows":
		quantity = random.randint(2, 5)

	doc = {
	"partNumber":part["partNumber"],
	"quanity": quantity,
	"datePutIntoService": part["datePutIntoService"],
	"datePulledFromService": part["datePulledFromService"]
	}

	return doc


# def createBOMDoc(num, piston, crankshaft, cylinderhead, suspension, rear_axle, front_axle, clutch, transmission, door, window, roof):
def createBOMDoc(num, parts_array):
	doc = {
	"bomName": "BOM"+"_"+str(num),
	"productReleaseDate": datetime(random.randint(2022, 2023), random.randint(1, 12), random.randint(1, 28)),
	"parts": parts_array,
	"personas":[],
	"updatedAt": datetime(2024, random.randint(1, 8), random.randint(1, 28))
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

# get parts from MDB
pistons = parts_col.find({"description":"Engine Piston"})
crankshafts = parts_col.find({"description":"Engine Crankshaft"})
cylinderheads = parts_col.find({"description":"Engine Cylinderhead"})
suspensions = parts_col.find({"description":"Chassis Suspension"})
rear_axles = parts_col.find({"description":"Chassis Rear_Axle"})
front_axles = parts_col.find({"description":"Chassis Front_Axle"})
clutchs = parts_col.find({"description":"Transmission Clutch"})
transmissions = parts_col.find({"description":"Transmission Gearbox"})
doors = parts_col.find({"description":"Body Doors"})
windows = parts_col.find({"description":"Body Windows"})
roofs = parts_col.find({"description":"Body Roof"})

num = 0

pistons_parts = []
for piston in pistons:
	pistons_parts.append(createPartsDoc(piston))

crankshafts_parts = []
for crankshaft in crankshafts:
	crankshafts_parts.append(createPartsDoc(crankshaft))

cylinderheads_parts = []
for cylinderhead in cylinderheads:
	cylinderheads_parts.append(createPartsDoc(cylinderhead))

suspensions_parts = []
for suspension in suspensions:
	suspensions_parts.append(createPartsDoc(suspension))

rear_axles_parts = []
for rear_axle in rear_axles:
	rear_axles_parts.append(createPartsDoc(rear_axle))

front_axles_parts = []
for front_axle in front_axles:
	front_axles_parts.append(createPartsDoc(front_axle))

clutchs_parts = []
for clutch in clutchs:
	clutchs_parts.append(createPartsDoc(clutch))

transmissions_parts = []
for transmission in transmissions:
	transmissions_parts.append(createPartsDoc(transmission))

doors_parts = []
for door in doors:
	doors_parts.append(createPartsDoc(door))

windows_parts = []
for window in windows:
	windows_parts.append(createPartsDoc(window))

roofs_parts = []
for roof in roofs:
	roofs_parts.append(createPartsDoc(roof))


parts_matrix = itertools.product(pistons_parts, crankshafts_parts, cylinderheads_parts, suspensions_parts, rear_axles_parts, front_axles_parts, clutchs_parts, transmissions_parts, doors_parts, windows_parts, roofs_parts)
# print(len(list(x)))
bulk_array = []
bulk_counter = 0
total_counter = 0
for parts_array in parts_matrix:
	num += 1
	# print(list(parts_array))
	bom = createBOMDoc(num, list(parts_array))
	if bulk_counter < 1000:
		bulk_array.append(bom)
		bulk_counter += 1
		total_counter += 1
	else:
		y = current_version_boms_col.insert_many(bulk_array)
		bulk_array = []
		bulk_counter = 0
		total_counter += 1
	if total_counter == len(parts_matrix)-1:
		y = current_version_boms_col.insert_many(bulk_array)

# for a, b, c, d, e, f, g, h, i, j, k in zip(pistons, crankshafts, cylinderheads, suspensions, rear_axles, front_axles, clutchs, transmissions, doors, windows, roofs):
# 	num += 1
# 	parts_array = []

# 	parts_array.append(createPartsDoc(a))
# 	parts_array.append(createPartsDoc(b))
# 	parts_array.append(createPartsDoc(c))
# 	parts_array.append(createPartsDoc(d))
# 	parts_array.append(createPartsDoc(e))
# 	parts_array.append(createPartsDoc(f))
# 	parts_array.append(createPartsDoc(g))
# 	parts_array.append(createPartsDoc(h))
# 	parts_array.append(createPartsDoc(i))
# 	parts_array.append(createPartsDoc(j))
# 	parts_array.append(createPartsDoc(k))

# 	bom = createBOMDoc(num, parts_array)
# 	y = current_version_boms_col.insert_one(bom)


# for piston in pistons:
# 	for crankshaft in crankshafts:
# 		for cylinderhead in cylinderheads:
# 			for suspension in suspensions:
# 				for rear_axle in rear_axles:
# 					for front_axle in front_axles:
# 						for clutch in clutchs:
# 							for transmission in transmissions:
# 								for door in doors:
# 									for window in windows:
# 										print(window)
# 										for roof in roofs:
# 											num += 1
											# parts_array = []

											# parts_array.append(createPartsDoc(piston))
											# parts_array.append(createPartsDoc(crankshaft))
											# parts_array.append(createPartsDoc(cylinderhead))
											# parts_array.append(createPartsDoc(suspension))
											# parts_array.append(createPartsDoc(rear_axle))
											# parts_array.append(createPartsDoc(front_axle))
											# parts_array.append(createPartsDoc(clutch))
											# parts_array.append(createPartsDoc(transmission))
											# parts_array.append(createPartsDoc(door))
											# parts_array.append(createPartsDoc(window))
											# parts_array.append(createPartsDoc(roof))
# 											bom = createBOMDoc(num, parts_array)
# 											print('here_'+str(num))
# 											# y = current_version_boms_col.insert_one(bom)
