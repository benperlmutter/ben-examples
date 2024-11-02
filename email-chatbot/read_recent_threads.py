import os.path
import base64
import datetime
import dateutil
import pymongo
import json

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

  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("../../email-chatbot-creds/token.json"):
    creds = Credentials.from_authorized_user_file("../../email-chatbot-creds/token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "../../email-chatbot-creds/credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("../../email-chatbot-creds/token.json", "w") as token:
      token.write(creds.to_json())

  try:
    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)
    results = service.users().threads().list(userId="me").execute()
    threads = results.get("threads", [])

    i = 0

    w = og_emails_col.find().sort({"date":-1}).limit(10)
    for doc in w:
      print(doc)

  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()