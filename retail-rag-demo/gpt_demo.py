import pymongo
import json
from sentence_transformers import SentenceTransformer, util

import os
from openai import AzureOpenAI


# ---------- define the query here ---------- #

query = "stickers, water, burrito"
# query = "chips, Chicken Burrito"
query = "ice cream, red wine, and popcorn"
# query = '{"name": "Cigarettes - Am Sq Turqse B", "quantity": "2"}'
# query = "salad, sandwich, coca cola"
# query = "W-"
#query = "Studying hard, the students prepped for their exams."
#query = "A delicious meal was cooked by the chef."
#query = "Tyson's boxing style was feared for its power and aggression."


# ---------- gather credentials here ---------- #

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


# ---------- establish parameters here ---------- #

os.environ["TOKENIZERS_PARALLELISM"] = "false"

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
        "$limit": 10
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

basket_counter = 0


# ---------- functions start here ---------- #

def process_query_result(basket):
    basket_string = ""
    for item in json.loads("["+basket.replace("}{","},{")+"]"):
        basket_string += " "
        basket_string += item["name"]+" with quantity of "+str(item["quantity"])+","

    return basket_string

def query_gpt(message_content, client):
    completion = client.chat.completions.create(
        model="gpt-35-turbo",
        messages=[
        {
        "role": "user",
        "content": message_content
        }])
    return completion.to_json()


# ---------- script starts here ---------- #

message_content = "Given my basket of "+query+", what is the most common item these similar baskets have that is not currently in my basket, with these other baskets looking like "
results = orders_demo_col.aggregate(pipeline)
for result in results:
    basket_counter += 1
    basket_string = ""
    if basket_counter > 1:
        basket_string += " and "
    basket_string += "basket "+str(basket_counter)+" made up of"+process_query_result(result["basket"])
    message_content += basket_string

response = query_gpt(message_content[:-1], deployment_client)
print(json.loads(response)["choices"][0]["message"]["content"])

