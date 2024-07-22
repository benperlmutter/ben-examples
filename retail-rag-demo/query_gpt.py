import json
import os
from openai import AzureOpenAI
    
# client = AzureOpenAI(
#     api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
#     api_version="2024-02-01",
#     azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
#     )

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

completion = deployment_client.chat.completions.create(
    model="gpt-35-turbo",
    messages=[
        {
            "role": "user",
            # "content": "How do I output all files in a directory using Python?",
            # "content": "What is the most likely thing I would purchase next if my current basket consists of stickers, water, and a burrito, and 3 similar baskets purchased previously have looked like basket 1 made up of Amys Black Bean & Corn Salsa with quantity of 1, Juice - Welch's Grape Juice 16oz with quantity of 1, Taco Works Tortilla Chip with quantity of 1, Stickers - Assorted with quantity of 3, and basket 2 made up of Taco Works Tortilla Chips with quantity of 1, Stickers - Assorted with quantity of 3, and basket 3 made up of Stickers - Assorted with quantity of 4, Morenita Salt And Lime Tortilla Chips with quantity of 1, Salsa Fresca 16oz with quantity of 1"
            "content": "Given my basket of stickers, water, and a burrito, What is the most common item not found in my basket from these 3 similar baskets that look like basket 1 made up of Amys Black Bean & Corn Salsa with quantity of 1, Juice - Welch's Grape Juice 16oz with quantity of 1, Taco Works Tortilla Chip with quantity of 1, Stickers - Assorted with quantity of 3, and basket 2 made up of Taco Works Tortilla Chips with quantity of 1, Stickers - Assorted with quantity of 3, and basket 3 made up of Stickers - Assorted with quantity of 4, Morenita Salt And Lime Tortilla Chips with quantity of 1, Salsa Fresca 16oz with quantity of 1"
        },
    ],
)
print(completion.to_json())