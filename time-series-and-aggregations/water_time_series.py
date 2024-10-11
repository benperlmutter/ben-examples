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
water_data_db = mdb_client.water_data

# create time series collection if necessary
water_data_db.create_collection('water_metrics', timeseries={ 'timeField': 'timestamp', 'metaField': 'metadata' })

water_data_coll = water_data_db.water_metrics

data_point_type = ["flow_meter", "pressure_sensor", "temp_sensor", "leak_sensor", "maintenance_event"]
metric_type = ["flow_rate_liters_per_minute", "pressure_psi", "temperature_celsius", "duration_minutes", "leak_volume_liters"]
location_list = ["Main Pipeline Section A", "Main Pipeline Section B", "Resevoir Inlet", "Treatment Plant", "Pump Station", "Distribution Line A"]
geo_points = [{ "type": "Point", "coordinates": [ random.randint(-180, 180), random.randint(-90, 90) ] }, { "type": "Point", "coordinates": [ random.randint(-180, 180), random.randint(-90, 90) ] }, { "type": "Point", "coordinates": [ random.randint(-180, 180), random.randint(-90, 90) ] }, { "type": "Point", "coordinates": [ random.randint(-180, 180), random.randint(-90, 90) ] }, { "type": "Point", "coordinates": [ random.randint(-180, 180), random.randint(-90, 90) ] }, { "type": "Point", "coordinates": [ random.randint(-180, 180), random.randint(-90, 90) ] }, { "type": "Point", "coordinates": [ random.randint(-180, 180), random.randint(-90, 90) ] }, { "type": "Point", "coordinates": [ random.randint(-180, 180), random.randint(-90, 90) ] }, { "type": "Point", "coordinates": [ random.randint(-180, 180), random.randint(-90, 90) ] }, { "type": "Point", "coordinates": [ random.randint(-180, 180), random.randint(-90, 90) ] }]

# generate documents
counter = 0
total_counter = 0
total_docs_number = 999999
doc_array = []

while total_counter < total_docs_number:
	counter += 1
	total_counter += 1
	data_point_number = random.randint(0, len(data_point_type)-1)
	location_number = random.randint(0, len(location_list)-1)
	doc = {
		"timestamp": datetime(random.randint(2010, 2021), random.randint(1, 12), random.randint(1, 28), hour=random.randint(1, 23), minute=random.randint(1, 59), second=random.randint(1, 59), microsecond=random.randint(1, 999999)),
		"metadata": {
		"sensor_id":data_point_type[data_point_number]+"_"+str(total_counter%20),
		"geo_location": geo_points[(total_counter%10)-1],
		"metric": metric_type[data_point_number],
		"metric_value": random.randint(1, 100),
		"location": location_list[location_number],
		}
	}
	# print(doc["metadata"]["geo_location"])
	doc_array.append(doc)
	if len(doc_array) > 999:
		w = water_data_coll.insert_many(doc_array)
		doc_array = []
		counter = 0
		print(total_counter)
	elif total_counter == total_docs_number:
		w = water_data_coll.insert_many(doc_array)

