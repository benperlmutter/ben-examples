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

  results = og_emails_col.aggregate([{"$sort":{"date":1}}])
  print(list(results))


if __name__ == "__main__":
  main()