import pymongo
import json
from sentence_transformers import SentenceTransformer, util

import os
from openai import AzureOpenAI


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
# orders_demo_col = retail_demo_db.orders
orders_demo_col = retail_demo_db.orders_updated_baskets

f = open('../../azure-gpt-creds/azure-gpt-creds.json')
pData = json.load(f)

azure_api_key = pData["azure-api-key"]
azure_api_version = pData["azure-api-version"]
azure_endpoint = pData["azure-endpoint"]
azure_deployment_name = pData["azure-deployment-name"] 
    
deployment_client = AzureOpenAI(
    api_version=azure_api_version,
    # https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#create-a-resource
    azure_endpoint=azure_endpoint,
    # Navigate to the Azure OpenAI Studio to deploy a model.
    azure_deployment=azure_deployment_name,  # e.g. gpt-35-instant
    api_key=azure_api_key
)

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