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


    if not threads:
      print("No labels found.")
      return
    # print("Threads:")
    for thread in threads:
      print("")
      thread_id = thread["id"]
      print("new thread with id: "+thread_id)
      if i < 1000:
        i += 1
        email = service.users().threads().get(userId="me", id=thread["id"], format="full").execute()
        print("..............................NEW EMAIL..............................")
        print(email)
        if "messages" in email:
          for m in email["messages"]: #high level messages array
            snippet = m["snippet"]
            # print("snippet is "+snippet)
            sender = "Guest"
            date_var = datetime.date.today()
            if "headers" in m["payload"]:
              for h in m["payload"]["headers"]:
                if h["name"] == "Date":
                  date_var = dateutil.parser.parse(h["value"])
                if h["name"] == "From":
                  if h["value"].split(" ")[0] == "Events":
                    sender = "Events Team"
            if "data" in m["payload"]["body"]:
              thread_message = base64.urlsafe_b64decode(m["payload"]["body"]["data"]).decode("utf-8")
              print(sender+" said..............................NEW PART..............................")
              # print(thread_message)
              thread_message = thread_message.replace("\r\n"," ")
              date_var = date_var+datetime.timedelta(milliseconds=10)
              doc = {"_id": date_var, "thread_id": thread_id, "sender": sender, "thread_message": thread_message}
              print(doc)
              w = og_emails_col.insert_one(doc)
            if "parts" in m["payload"]: #first level payload w/ parts
              for p in m["payload"]["parts"]:
                if "body" in p and "data" in p["body"]:
                  thread_message = base64.urlsafe_b64decode(p["body"]["data"]).decode("utf-8")
                  if thread_message[0] != "<":
                    print(sender+" said..............................NEW PART..............................")
                    thread_message = thread_message.split("On Sun,")[0]
                    thread_message = thread_message.split("On Mon,")[0]
                    thread_message = thread_message.split("On Tue,")[0]
                    thread_message = thread_message.split("On Wed,")[0]
                    thread_message = thread_message.split("On Thu,")[0]
                    thread_message = thread_message.split("On Fri,")[0]
                    thread_message = thread_message.split("On Sat,")[0]
                    # print(thread_message)
                    thread_message = thread_message.replace("\r\n"," ")
                    date_var = date_var+datetime.timedelta(milliseconds=100)
                    doc = {"_id": date_var, "thread_id": thread_id, "sender": sender, "thread_message": thread_message}
                    print(doc)
                    w = og_emails_col.insert_one(doc)
                if "parts" in p: #second level parts in parts array
                  # print("parts in p")
                  for sub_part in p["parts"]:
                    if "body" in sub_part and "data" in sub_part["body"]:
                      # print("body and data in sub_part")
                      thread_message = base64.urlsafe_b64decode(sub_part["body"]["data"]).decode("utf-8")
                      if thread_message[0] != "<":
                        print(sender+" said..............................NEW PART..............................")
                        thread_message = thread_message.split("On Sun,")[0]
                        thread_message = thread_message.split("On Mon,")[0]
                        thread_message = thread_message.split("On Tue,")[0]
                        thread_message = thread_message.split("On Wed,")[0]
                        thread_message = thread_message.split("On Thu,")[0]
                        thread_message = thread_message.split("On Fri,")[0]
                        thread_message = thread_message.split("On Sat,")[0]
                        # print(thread_message)
                        thread_message = thread_message.replace("\r\n"," ")
                        date_var = date_var+datetime.timedelta(milliseconds=1000)
                        doc = {"_id": date_var, "thread_id": thread_id, "sender": sender, "thread_message": thread_message}
                        print(doc)
                        w = og_emails_col.insert_one(doc)

        # for m in email["messages"]:
        #   if "parts" in m["payload"]:
        #     for p in m["payload"]["parts"]:
        #       if "data" in p["body"]:
        #         thread_message = base64.urlsafe_b64decode(p["body"]["data"]).decode("utf-8")
        #         if thread_message[0] != "<":
        #           print("..............................NEW PART..............................")
        #           print(thread_message)
        #         # thread_message = thread_message.replace("b", "")
        #         # thread_message = thread_message.replace("n", "")
        #         # thread_message = thread_message.replace("\\r\n", "")

  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()