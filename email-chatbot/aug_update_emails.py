import os.path
import base64
import datetime
import dateutil
import pymongo
import json
import logging
import time
from typing import Dict, List, Optional

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from bs4 import BeautifulSoup

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Gmail API scopes
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

class EmailUpdater:
    def __init__(self):
        self.setup_database()
        self.setup_gmail_service()
    
    def setup_database(self):
        """Initialize MongoDB connection"""
        try:
            with open('../../../atlas-creds/atlas-creds.json', 'r') as f:
                creds_data = json.load(f)
            
            mdb_string = creds_data["mdb-connection-string"]
            self.mdb_client = pymongo.MongoClient(mdb_string)
            
            # Use new database structure
            self.email_chatbot_db = self.mdb_client.email_chatbot
            self.original_emails_col = self.email_chatbot_db.original_emails
            
            logger.info("Database connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup database: {e}")
            raise
    
    def setup_gmail_service(self):
        """Initialize Gmail API service"""
        try:
            creds = None
            
            if os.path.exists("../../../email-chatbot-creds/token.json"):
                creds = Credentials.from_authorized_user_file(
                    "../../../email-chatbot-creds/token.json", SCOPES
                )
            
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        "../../../email-chatbot-creds/credentials.json", SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                
                with open("../../../email-chatbot-creds/token.json", "w") as token:
                    token.write(creds.to_json())
            
            self.gmail_service = build("gmail", "v1", credentials=creds)
            logger.info("Gmail service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup Gmail service: {e}")
            raise
    
    def get_last_update_time(self) -> datetime.datetime:
        """Get the timestamp of the last processed email"""
        try:
            # Find the most recent email in our database
            latest_email = self.original_emails_col.find().sort("date", -1).limit(1)
            
            for email in latest_email:
                logger.info(f"Last processed email date: {email['date']}")
                return email['date']
            
            # If no emails found, start from 30 days ago
            default_date = datetime.datetime.now() - datetime.timedelta(days=30)
            logger.info(f"No emails found, starting from: {default_date}")
            return default_date
            
        except Exception as e:
            logger.error(f"Error getting last update time: {e}")
            return datetime.datetime.now() - datetime.timedelta(days=30)
    
    def clean_email_content(self, content: str) -> str:
        """Clean and process email content"""
        if not content:
            return ""
        
        # Remove quoted text (email chains)
        days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
        for day in days:
            content = content.split(f"On {day},")[0]
        
        # Clean up formatting
        content = content.replace("\r\n", " ").replace("\n", " ").replace("\r", " ")
        content = " ".join(content.split())  # Remove extra whitespace
        
        return content.strip()
    
    def extract_message_content(self, payload: Dict) -> str:
        """Recursively extract text content from email payload"""
        content_parts = []
        
        # Check direct body data
        if "body" in payload and "data" in payload["body"]:
            try:
                decoded = base64.urlsafe_b64decode(payload["body"]["data"]).decode("utf-8")
                if decoded.strip().startswith("<"):
                    # HTML content - extract text
                    soup = BeautifulSoup(decoded, "html.parser")
                    text = soup.get_text()
                    if text.strip():
                        content_parts.append(text.strip())
                else:
                    # Plain text content
                    if decoded.strip():
                        content_parts.append(decoded.strip())
            except Exception as e:
                logger.warning(f"Error decoding message body: {e}")
        
        # Check parts recursively
        if "parts" in payload:
            for part in payload["parts"]:
                part_content = self.extract_message_content(part)
                if part_content:
                    content_parts.append(part_content)
        
        return "\n".join(content_parts)
    
    def extract_message_data(self, message: Dict, thread_id: str) -> Optional[Dict]:
        """Extract relevant data from a Gmail message"""
        try:
            # Extract headers
            headers = {}
            if "headers" in message.get("payload", {}):
                for header in message["payload"]["headers"]:
                    headers[header["name"]] = header["value"]
            
            # Extract basic info
            message_id = headers.get("Message-ID", "")
            date_str = headers.get("Date", "")
            from_header = headers.get("From", "")
            subject = headers.get("Subject", "")
            snippet = message.get("snippet", "")
            
            # Parse date
            try:
                date_parsed = dateutil.parser.parse(date_str) if date_str else datetime.datetime.now()
            except:
                date_parsed = datetime.datetime.now()
            
            # Determine sender
            sender = "Events Team" if from_header.startswith("Events") else "Guest"
            
            # Extract message content
            thread_message = self.extract_message_content(message["payload"])
            
            if not thread_message:
                return None
            
            # Clean content
            thread_message = self.clean_email_content(thread_message)
            
            if not thread_message:
                return None
            
            return {
                "message_id": message_id,
                "thread_id": thread_id,
                "date": date_parsed,
                "sender": sender,
                "subject": subject,
                "snippet": snippet,
                "thread_message": thread_message,
                "from_header": from_header,
                "created_at": datetime.datetime.now(),
                "updated_at": datetime.datetime.now()
            }
            
        except Exception as e:
            logger.error(f"Error extracting message data: {e}")
            return None
    
    def check_for_new_emails(self, since_date: datetime.datetime = None):
        """Check for new emails since the last update"""
        try:
            if since_date is None:
                since_date = self.get_last_update_time()
            
            logger.info(f"Checking for new emails since: {since_date}")
            
            # Get recent threads
            results = self.gmail_service.users().threads().list(userId="me").execute()
            threads = results.get("threads", [])
            
            if not threads:
                logger.info("No threads found")
                return
            
            new_messages_count = 0
            updated_threads_count = 0
            
            # Process threads to find new messages
            for i, thread in enumerate(threads):
                try:
                    thread_id = thread["id"]
                    
                    # Get thread details
                    thread_details = self.gmail_service.users().threads().get(
                        userId="me", id=thread_id, format="full"
                    ).execute()
                    
                    if "messages" not in thread_details:
                        continue
                    
                    thread_has_new_messages = False
                    
                    # Check each message in the thread
                    for message in thread_details["messages"]:
                        message_data = self.extract_message_data(message, thread_id)
                        
                        if not message_data:
                            continue
                        
                        # Check if this is a new message
                        existing_message = self.original_emails_col.find_one({
                            "message_id": message_data["message_id"]
                        })
                        
                        if not existing_message:
                            # This is a new message
                            try:
                                self.original_emails_col.insert_one(message_data)
                                new_messages_count += 1
                                thread_has_new_messages = True
                                
                                logger.info(f"New message added: {message_data['sender']} - {message_data['subject'][:50]}...")
                                
                                # Special handling for guest messages
                                if message_data['sender'] == 'Guest':
                                    logger.info("🔔 NEW GUEST MESSAGE DETECTED - May need response!")
                                    self.log_guest_message(message_data)
                                
                            except Exception as e:
                                logger.error(f"Error inserting new message: {e}")
                    
                    if thread_has_new_messages:
                        updated_threads_count += 1
                    
                    # Progress update every 50 threads
                    if (i + 1) % 50 == 0:
                        logger.info(f"Processed {i+1} threads, found {new_messages_count} new messages")
                
                except Exception as e:
                    logger.error(f"Error processing thread {thread_id}: {e}")
                    continue
            
            logger.info(f"Update complete! Found {new_messages_count} new messages in {updated_threads_count} threads")
            
            if new_messages_count > 0:
                self.print_recent_activity()
            
        except Exception as e:
            logger.error(f"Error checking for new emails: {e}")
            raise
    
    def log_guest_message(self, message_data: Dict):
        """Log details of new guest messages that may need responses"""
        logger.info("=" * 60)
        logger.info("NEW GUEST MESSAGE DETAILS:")
        logger.info(f"Date: {message_data['date']}")
        logger.info(f"Subject: {message_data['subject']}")
        logger.info(f"Thread ID: {message_data['thread_id']}")
        logger.info(f"Message Preview: {message_data['thread_message'][:200]}...")
        logger.info("=" * 60)
    
    def print_recent_activity(self):
        """Print summary of recent email activity"""
        try:
            # Get recent messages (last 24 hours)
            since_yesterday = datetime.datetime.now() - datetime.timedelta(days=1)
            
            recent_messages = self.original_emails_col.find({
                "date": {"$gte": since_yesterday}
            }).sort("date", -1)
            
            logger.info("=== Recent Activity (Last 24 Hours) ===")
            
            for message in recent_messages:
                logger.info(f"{message['date']} - {message['sender']}: {message['subject'][:50]}...")
            
            # Count by sender
            guest_count = self.original_emails_col.count_documents({
                "sender": "Guest",
                "date": {"$gte": since_yesterday}
            })
            
            events_count = self.original_emails_col.count_documents({
                "sender": "Events Team",
                "date": {"$gte": since_yesterday}
            })
            
            logger.info(f"Recent Guest messages: {guest_count}")
            logger.info(f"Recent Events Team messages: {events_count}")
            
        except Exception as e:
            logger.error(f"Error generating recent activity summary: {e}")
    
    def monitor_continuously(self, check_interval_minutes: int = 15):
        """Continuously monitor for new emails"""
        logger.info(f"Starting continuous monitoring (checking every {check_interval_minutes} minutes)")
        
        while True:
            try:
                logger.info("Checking for new emails...")
                self.check_for_new_emails()
                
                logger.info(f"Waiting {check_interval_minutes} minutes until next check...")
                time.sleep(check_interval_minutes * 60)
                
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                logger.info("Waiting 5 minutes before retrying...")
                time.sleep(300)  # Wait 5 minutes before retrying

def main():
    """Main function"""
    try:
        updater = EmailUpdater()
        
        # Choose mode:
        # 1. One-time check for new emails
        updater.check_for_new_emails()
        
        # 2. Continuous monitoring (uncomment to use)
        # updater.monitor_continuously(check_interval_minutes=15)
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise

if __name__ == "__main__":
    main()