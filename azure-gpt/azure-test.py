import os
from openai import AzureOpenAI
    
# client = AzureOpenAI(
#     api_key=os.getenv("AZURE_OPENAI_API_KEY"),  
#     api_version="2024-02-01",
#     azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
#     )

client = AzureOpenAI(
    api_key="36d786792d78459d88dc4782e716f618",  
    api_version="2024-02-01",
    azure_endpoint = "https://ben-demo.openai.azure.com/"
    )

api_version = "2024-02-01"
    
deployment_name='retail-demo' #This will correspond to the custom name you chose for your deployment when you deployed a model. Use a gpt-35-turbo-instruct deployment. 
    
deployment_client = AzureOpenAI(
    api_version=api_version,
    # https://learn.microsoft.com/en-us/azure/cognitive-services/openai/how-to/create-resource?pivots=web-portal#create-a-resource
    azure_endpoint="https://ben-demo.openai.azure.com/",
    # Navigate to the Azure OpenAI Studio to deploy a model.
    azure_deployment=deployment_name,  # e.g. gpt-35-instant
    api_key="36d786792d78459d88dc4782e716f618"
)

completion = deployment_client.chat.completions.create(
    model="gpt-35-turbo",
    messages=[
        {
            "role": "user",
            "content": "How do I output all files in a directory using Python?",
        },
    ],
)
print(completion.to_json())