import os.path
import base64
import datetime
import dateutil
import pymongo
import json
from sentence_transformers import SentenceTransformer, util

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def main():
  #connect to the MDB client
  f = open('../../atlas-creds/atlas-creds.json')
  pData = json.load(f)

  mdb_string = pData["mdb-connection-string"]

  mdb_client = pymongo.MongoClient(mdb_string)
  event_emails_db = mdb_client.event_emails
  og_emails_col = event_emails_db.og_emails
  embedded_guest_emails_col = event_emails_db.embedded_guest_emails

  model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

  w = og_emails_col.find({"sender":"Guest"}).sort({"date":-1}).limit(10)

  for doc in w:
    thread_message = doc["thread_message"]

    conversation_text = "We have received an email from a prospective guest that is interested in a wedding or event at our business, the Big Sur River Inn. They have sent us this email message: \n"+thread_message
    conversation_text += "\n\nPlease help us generate a response to this inquiry using the same language and communication style as these prior conversations between a guest and the Events Team as follows: \n"

    message_vector = model.encode(thread_message).tolist()

    pipeline = [
        {
            "$search": {
                "knnBeta": {
                    "vector": message_vector,
                    "path": "message_embeddings",
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

    
    results = embedded_guest_emails_col.aggregate(pipeline)
    convo_num = 1
    for result in results:
      conversation_text += "Conversation "+str(convo_num)+" made up of \n"
      convo_num += 1
      thread_id = result["thread_id"]
      # print(result)
      relevant_threads = og_emails_col.find({"thread_id":thread_id}).sort({"date":1})
      # rt_size = len(list(relevant_threads))
      # rt_size = len(list(relevant_threads.clone()))
      # print(rt_size)
      # print("rt size above")

      message_num = 1
      for rt in relevant_threads:
        # print('this is rt')
        # print(rt)
        conversation_text += "Message "+ str(message_num)+ " from the "+rt["sender"]
        conversation_text += " saying "+rt["thread_message"] + "\n"
        message_num += 1
        # if message_num < rt_size:
        #   conversation_text += 
      # if message_num < rt_size:
      #   conversation_text +=

    print(conversation_text) 


if __name__ == "__main__":
  main()