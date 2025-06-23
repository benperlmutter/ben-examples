import os.path
import base64
import datetime
import dateutil
import pymongo
import json
import logging
import re
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

class EmailCollector:
    def __init__(self):
        self.setup_database()
        self.setup_gmail_service()

    def determine_sender(self, from_header: str) -> str:
        """Determine sender based on email domain"""
        if not from_header:
            return "Guest"

        # Extract email address from header (handles formats like "Name <email@domain.com>")
        email_match = re.search(r'<([^>]+)>|([^\s<>]+@[^\s<>]+)', from_header)
        if email_match:
            email_address = email_match.group(1) or email_match.group(2)
            if email_address and "@bigsurriverinn.com" in email_address.lower():
                return "BSRI Team"

        return "Guest"
    
    def setup_database(self):
        """Initialize MongoDB connection with new database structure"""
        try:
            with open('../../../atlas-creds/atlas-creds.json', 'r') as f:
                creds_data = json.load(f)
            
            mdb_string = creds_data["mdb-connection-string"]
            self.mdb_client = pymongo.MongoClient(mdb_string)
            
            # New database and collection structure
            self.email_chatbot_db = self.mdb_client.email_chatbot
            self.original_emails_col = self.email_chatbot_db.original_emails
            
            # Create indexes for better performance
            self.create_indexes()
            
            logger.info("Database connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup database: {e}")
            raise
    
    def create_indexes(self):
        """Create database indexes for efficient querying"""
        try:
            # Index on message_id for deduplication
            self.original_emails_col.create_index("message_id", unique=True)
            # Index on thread_id for thread queries
            self.original_emails_col.create_index("thread_id")
            # Index on date for chronological queries
            self.original_emails_col.create_index("date")
            # Index on sender for filtering
            self.original_emails_col.create_index("sender")
            # Compound index for thread queries by date
            self.original_emails_col.create_index([("thread_id", 1), ("date", 1)])
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Index creation warning (may already exist): {e}")
    
    def setup_gmail_service(self):
        """Initialize Gmail API service"""
        try:
            creds = None
            
            # Load existing credentials
            if os.path.exists("../../../email-chatbot-creds/token.json"):
                creds = Credentials.from_authorized_user_file(
                    "../../../email-chatbot-creds/token.json", SCOPES
                )
            
            # Refresh or get new credentials
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        "../../../email-chatbot-creds/credentials.json", SCOPES
                    )
                    creds = flow.run_local_server(port=0)
                
                # Save credentials for next run
                with open("../../../email-chatbot-creds/token.json", "w") as token:
                    token.write(creds.to_json())
            
            self.gmail_service = build("gmail", "v1", credentials=creds)
            logger.info("Gmail service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup Gmail service: {e}")
            raise
    
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
            
            # Determine sender based on email domain
            sender = self.determine_sender(from_header)
            
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
    
    def collect_all_emails(self, max_threads: int = None):
        """Collect all emails from Gmail and store in MongoDB"""
        try:
            logger.info("Starting email collection process...")
            
            # Get all threads
            results = self.gmail_service.users().threads().list(userId="me").execute()
            threads = results.get("threads", [])
            
            if not threads:
                logger.info("No threads found")
                return
            
            total_threads = len(threads)
            if max_threads:
                threads = threads[:max_threads]
                logger.info(f"Processing {len(threads)} of {total_threads} threads")
            else:
                logger.info(f"Processing all {total_threads} threads")
            
            processed_count = 0
            new_messages_count = 0
            
            for i, thread in enumerate(threads):
                try:
                    thread_id = thread["id"]
                    logger.info(f"Processing thread {i+1}/{len(threads)}: {thread_id}")
                    
                    # Get full thread details
                    thread_details = self.gmail_service.users().threads().get(
                        userId="me", id=thread_id, format="full"
                    ).execute()
                    
                    if "messages" not in thread_details:
                        continue
                    
                    # Process each message in the thread
                    for message in thread_details["messages"]:
                        message_data = self.extract_message_data(message, thread_id)
                        
                        if message_data:
                            try:
                                # Insert with upsert to avoid duplicates
                                result = self.original_emails_col.replace_one(
                                    {"message_id": message_data["message_id"]},
                                    message_data,
                                    upsert=True
                                )
                                
                                if result.upserted_id:
                                    new_messages_count += 1
                                    logger.debug(f"New message stored: {message_data['message_id']}")
                                
                            except pymongo.errors.DuplicateKeyError:
                                logger.debug(f"Message already exists: {message_data['message_id']}")
                            except Exception as e:
                                logger.error(f"Error storing message: {e}")
                    
                    processed_count += 1
                    
                    # Progress update every 10 threads
                    if (i + 1) % 10 == 0:
                        logger.info(f"Processed {i+1} threads, {new_messages_count} new messages")
                
                except Exception as e:
                    logger.error(f"Error processing thread {thread_id}: {e}")
                    continue
            
            logger.info(f"Collection complete! Processed {processed_count} threads, {new_messages_count} new messages")
            
            # Print summary statistics
            self.print_collection_summary()
            
        except Exception as e:
            logger.error(f"Error in collect_all_emails: {e}")
            raise
    
    def print_collection_summary(self):
        """Print summary of collected emails"""
        try:
            total_count = self.original_emails_col.count_documents({})
            guest_count = self.original_emails_col.count_documents({"sender": "Guest"})
            bsri_count = self.original_emails_col.count_documents({"sender": "BSRI Team"})
            thread_count = len(self.original_emails_col.distinct("thread_id"))

            logger.info("=== Collection Summary ===")
            logger.info(f"Total messages: {total_count}")
            logger.info(f"Guest messages: {guest_count}")
            logger.info(f"BSRI Team messages: {bsri_count}")
            logger.info(f"Unique threads: {thread_count}")
            
            # Get date range
            oldest = self.original_emails_col.find().sort("date", 1).limit(1)
            newest = self.original_emails_col.find().sort("date", -1).limit(1)
            
            for old in oldest:
                logger.info(f"Oldest message: {old['date']}")
                break
            
            for new in newest:
                logger.info(f"Newest message: {new['date']}")
                break
            
        except Exception as e:
            logger.error(f"Error generating summary: {e}")

def main():
    """Main function to run email collection"""
    try:
        collector = EmailCollector()
        
        # Collect all emails (remove max_threads parameter to collect all)
        collector.collect_all_emails(max_threads=100)  # Limit for testing
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise

if __name__ == "__main__":
    main()