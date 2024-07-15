import json
import pymongo
from datetime import datetime

from square.http.auth.o_auth_2 import BearerAuthCredentials
from square.client import Client
import os

from sentence_transformers import SentenceTransformer, util

# ---------- functions start here ---------- #
def getOrders(startDate, endDate, locationID, cursor):
	result = client.orders.search_orders(
		body = {
	    "location_ids": [
	      locationID
	    ],
	    "query": {
	      "filter": {
	        "state_filter": {
	          "states": [
	            "COMPLETED"
	          ]
	        },
	        "date_time_filter": {
	          "closed_at": {
	            "start_at": startDate,
	            "end_at": endDate
	          }
	        }
	      },
	      "sort": {
	        "sort_field": "CLOSED_AT",
	        "sort_order": "DESC"
	      }
	    },
	    # "limit": 3,
	    "cursor": cursor,
	    "return_entries": True
	  }
	)

	return result

def readAndProcess(db, col):
	cursor = col.find({})
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
	
	if "line_items" in document:
		for li in document["line_items"]:
			new_string += json.dumps(li)

	new_doc["basket"] = new_string
	return new_doc


# ---------- script starts here ---------- #
dateFrom = datetime(2024, 7, 3)
# dateTo = datetime.today()
dateTo = datetime(2024, 7, 15)

dateFromString = dateFrom.strftime("%Y-%m-%dT%H:%M:%S")
dateToString = dateTo.strftime("%Y-%m-%dT%H:%M:%S")

f = open('../../atlas-creds/atlas-creds.json')
pData = json.load(f)

myclient = pymongo.MongoClient(pData["mongodump2-connection-string"])
mydb = myclient["retail"]
mycol = mydb["orders"]

f = open('../../square_creds/square_creds.json')
pData = json.load(f)

access_token = pData["access_token"]

model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

client = Client(bearer_auth_credentials=BearerAuthCredentials(access_token=access_token),environment='production')

result = getOrders(dateFromString, dateToString, "D4V4SR5CVWE6E", "")

if result.is_success():
	for o in result.body["order_entries"]:
		o["created_at"] = datetime.strptime(o["created_at"][:19], "%Y-%m-%dT%H:%M:%S")
		o["updated_at"] = datetime.strptime(o["updated_at"][:19], "%Y-%m-%dT%H:%M:%S")
		o["closed_at"] = datetime.strptime(o["closed_at"][:19], "%Y-%m-%dT%H:%M:%S")
		new_doc = readAndProcessDocument(o)
		# x = mycol.insert_one(o)
		basket_vector = model.encode(new_doc["basket"]).tolist()
		new_doc['vector_embedding'] = basket_vector
		x = mycol.insert_one(new_doc)
		print(new_doc["created_at"])
	if "cursor" in result.body:
		while "cursor" in result.body:
			result = getOrders(dateFromString, dateToString, "D4V4SR5CVWE6E", result.body["cursor"])
			for o in result.body["order_entries"]:
				o["created_at"] = datetime.strptime(o["created_at"][:19], "%Y-%m-%dT%H:%M:%S")
				o["updated_at"] = datetime.strptime(o["updated_at"][:19], "%Y-%m-%dT%H:%M:%S")
				o["closed_at"] = datetime.strptime(o["closed_at"][:19], "%Y-%m-%dT%H:%M:%S")
				new_doc = readAndProcessDocument(o)
				# x = mycol.insert_one(o)
				basket_vector = model.encode(new_doc["basket"]).tolist()
				new_doc['vector_embedding'] = basket_vector
				x = mycol.insert_one(new_doc)
				print(new_doc["created_at"])
elif result.is_error():
	print(result.errors)


