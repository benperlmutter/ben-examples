#!/usr/bin/env python3
"""
RAG-based Email Response Generator for BSRI Team

This script identifies unanswered guest emails and generates appropriate responses
using retrieval augmented generation (RAG) with MongoDB vector search and Azure OpenAI.

Features:
- Finds threads where the latest message is from a Guest (needs response)
- Uses the email_embeddings collection for semantic similarity search
- Generates contextual responses based on similar past conversations
- Provides detailed logging and response tracking
"""

import pymongo
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sentence_transformers import SentenceTransformer
from openai import AzureOpenAI

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EmailResponseGenerator:
    def __init__(self):
        self.setup_database()
        self.setup_azure_openai()
        self.setup_model()
    
    def setup_database(self):
        """Initialize MongoDB connection"""
        try:
            with open('../../../atlas-creds/atlas-creds.json', 'r') as f:
                creds_data = json.load(f)
            
            mdb_string = creds_data["mdb-connection-string"]
            self.mdb_client = pymongo.MongoClient(mdb_string)
            
            # Use email_chatbot database
            self.email_chatbot_db = self.mdb_client.email_chatbot
            self.original_emails_col = self.email_chatbot_db.original_emails
            self.email_embeddings_col = self.email_chatbot_db.email_embeddings
            
            logger.info("Database connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup database: {e}")
            raise
    
    def setup_azure_openai(self):
        """Initialize Azure OpenAI client"""
        try:
            with open('../../../azure-gpt-creds/azure-gpt-creds.json', 'r') as f:
                azure_creds = json.load(f)

            # Initialize Azure OpenAI client with only the required parameters
            # Removed any deprecated parameters like 'proxies'
            self.azure_client = AzureOpenAI(
                api_version=azure_creds["azure-api-version"],
                azure_endpoint=azure_creds["azure-endpoint"],
                api_key=azure_creds["azure-api-key"]
            )

            # Store deployment name separately for use in completions
            self.azure_deployment = azure_creds["azure-deployment-name"]

            logger.info("Azure OpenAI client initialized successfully")

        except Exception as e:
            logger.error(f"Failed to setup Azure OpenAI: {e}")
            logger.error(f"Error details: {str(e)}")
            raise
    
    def setup_model(self):
        """Initialize the SentenceTransformer model"""
        try:
            logger.info("Loading SentenceTransformer model...")
            self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            logger.info("SentenceTransformer model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer model: {e}")
            raise
    
    def find_unanswered_guest_emails(self, days_back: int = 30, limit: int = 10) -> List[Dict]:
        """Find threads where the latest message is from a Guest (needs BSRI Team response)"""
        try:
            logger.info(f"Finding unanswered guest emails from the last {days_back} days...")
            
            # Get recent guest messages
            since_date = datetime.now() - timedelta(days=days_back)
            
            # Find all recent guest messages
            recent_guest_messages = list(
                self.original_emails_col.find({
                    "sender": "Guest",
                    "date": {"$gte": since_date}
                }).sort("date", -1)
            )
            
            unanswered_threads = []
            processed_threads = set()
            
            for guest_message in recent_guest_messages:
                thread_id = guest_message["thread_id"]
                
                # Skip if we've already processed this thread
                if thread_id in processed_threads:
                    continue
                
                processed_threads.add(thread_id)
                
                # Get the latest message in this thread
                latest_message = self.original_emails_col.find({
                    "thread_id": thread_id
                }).sort("date", -1).limit(1)
                
                for latest in latest_message:
                    # If the latest message is from a Guest, it needs a response
                    if latest["sender"] == "Guest":
                        unanswered_threads.append(latest)
                        logger.info(f"Found unanswered thread: {thread_id} - {latest['subject'][:50]}...")
                        
                        if len(unanswered_threads) >= limit:
                            break
                
                if len(unanswered_threads) >= limit:
                    break
            
            logger.info(f"Found {len(unanswered_threads)} unanswered guest emails")
            return unanswered_threads
            
        except Exception as e:
            logger.error(f"Error finding unanswered guest emails: {e}")
            return []
    
    def find_similar_conversations(self, guest_message: str, k: int = 5) -> List[Dict]:
        """Use vector search to find similar conversations in the embeddings collection"""
        try:
            # Generate embedding for the guest message
            message_vector = self.model.encode(guest_message).tolist()
            
            # MongoDB vector search pipeline
            pipeline = [
                {
                    "$search": {
                        "knnBeta": {
                            "vector": message_vector,
                            "path": "message_embeddings",
                            "k": k * 3  # Get more results to filter
                        }
                    }
                },
                {
                    "$limit": k * 3
                },
                {
                    "$project": {
                        "message_embeddings": 0,  # Exclude large embedding field
                        "_id": 0,
                        "score": {
                            "$meta": "searchScore"
                        }
                    }
                }
            ]
            
            # Execute search
            search_results = list(self.email_embeddings_col.aggregate(pipeline))
            
            # Filter to get diverse thread examples (avoid multiple messages from same thread)
            seen_threads = set()
            filtered_results = []
            
            for result in search_results:
                thread_id = result.get("thread_id")
                if thread_id not in seen_threads:
                    seen_threads.add(thread_id)
                    filtered_results.append(result)
                    
                    if len(filtered_results) >= k:
                        break
            
            logger.info(f"Found {len(filtered_results)} similar conversations for RAG context")
            return filtered_results
            
        except Exception as e:
            logger.error(f"Error finding similar conversations: {e}")
            return []
    
    def get_thread_conversation(self, thread_id: str) -> List[Dict]:
        """Get the full conversation for a thread, sorted by date"""
        try:
            conversation = list(
                self.original_emails_col.find({
                    "thread_id": thread_id
                }).sort("date", 1)
            )
            return conversation

        except Exception as e:
            logger.error(f"Error getting thread conversation: {e}")
            return []

    def build_rag_context(self, guest_message: str, similar_conversations: List[Dict]) -> str:
        """Build context for RAG using similar conversations"""
        try:
            context = f"""You are responding as the BSRI Team (Big Sur River Inn Events Team) to a guest inquiry about weddings or events.

GUEST'S CURRENT MESSAGE:
{guest_message}

SIMILAR PAST CONVERSATIONS FOR REFERENCE:
Use these examples to understand our communication style and how we typically respond to similar inquiries:

"""

            for i, similar_msg in enumerate(similar_conversations, 1):
                thread_id = similar_msg.get("thread_id")
                score = similar_msg.get("score", 0)

                # Get the full conversation for this thread
                thread_conversation = self.get_thread_conversation(thread_id)

                if thread_conversation:
                    context += f"\n--- EXAMPLE CONVERSATION {i} (Similarity: {score:.3f}) ---\n"

                    for msg in thread_conversation:
                        sender = msg.get("sender", "Unknown")
                        message_text = msg.get("thread_message", "")
                        date = msg.get("date", "")

                        # Clean and truncate message for context
                        clean_message = message_text[:300] + "..." if len(message_text) > 300 else message_text

                        context += f"{sender}: {clean_message}\n"

                    context += "\n"

            context += """
INSTRUCTIONS:
1. Respond as the BSRI Team in a warm, professional, and helpful manner
2. Use the communication style and tone from the example conversations above
3. Address the guest's specific questions or requests
4. Provide relevant information about Big Sur River Inn's event services
5. Include appropriate contact information or next steps
6. Keep the response concise but comprehensive
7. Match the level of formality used in similar past responses

Generate a response that would be appropriate for the BSRI Team to send:"""

            return context

        except Exception as e:
            logger.error(f"Error building RAG context: {e}")
            return ""

    def generate_response(self, guest_message: str, rag_context: str) -> Optional[str]:
        """Generate response using Azure OpenAI with RAG context"""
        try:
            logger.info("Generating response using Azure OpenAI...")

            completion = self.azure_client.chat.completions.create(
                model=self.azure_deployment,  # Use the deployment name from credentials
                messages=[
                    {
                        "role": "user",
                        "content": rag_context
                    }
                ],
                temperature=0.7,
                max_tokens=500
            )

            response = completion.choices[0].message.content
            logger.info("Response generated successfully")
            return response

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            logger.error(f"Error details: {str(e)}")
            return None

    def process_unanswered_emails(self, days_back: int = 7, limit: int = 5, k_similar: int = 3):
        """Main function to process unanswered emails and generate responses"""
        try:
            logger.info("=" * 60)
            logger.info("STARTING EMAIL RESPONSE GENERATION")
            logger.info("=" * 60)

            # Find unanswered guest emails
            unanswered_emails = self.find_unanswered_guest_emails(days_back=days_back, limit=limit)

            if not unanswered_emails:
                logger.info("No unanswered guest emails found!")
                return

            logger.info(f"Processing {len(unanswered_emails)} unanswered emails...")

            for i, email in enumerate(unanswered_emails, 1):
                try:
                    logger.info(f"\n{'='*40}")
                    logger.info(f"PROCESSING EMAIL {i}/{len(unanswered_emails)}")
                    logger.info(f"{'='*40}")

                    thread_id = email["thread_id"]
                    subject = email.get("subject", "No Subject")
                    guest_message = email["thread_message"]
                    date = email.get("date", "Unknown")

                    logger.info(f"Thread ID: {thread_id}")
                    logger.info(f"Subject: {subject}")
                    logger.info(f"Date: {date}")
                    logger.info(f"Guest Message Preview: {guest_message[:100]}...")

                    # Find similar conversations
                    similar_conversations = self.find_similar_conversations(guest_message, k=k_similar)

                    if not similar_conversations:
                        logger.warning("No similar conversations found - skipping this email")
                        continue

                    # Build RAG context
                    rag_context = self.build_rag_context(guest_message, similar_conversations)

                    # Generate response
                    response = self.generate_response(guest_message, rag_context)

                    if response:
                        logger.info("\n" + "🤖 GENERATED RESPONSE:")
                        logger.info("-" * 40)
                        logger.info(response)
                        logger.info("-" * 40)

                        # Log response details
                        self.log_response_details(email, response, similar_conversations)
                    else:
                        logger.error("Failed to generate response")

                except Exception as e:
                    logger.error(f"Error processing email {i}: {e}")
                    continue

            logger.info("\n" + "=" * 60)
            logger.info("EMAIL RESPONSE GENERATION COMPLETED")
            logger.info("=" * 60)

        except Exception as e:
            logger.error(f"Error in process_unanswered_emails: {e}")
            raise

    def log_response_details(self, email: Dict, response: str, similar_conversations: List[Dict]):
        """Log detailed information about the generated response"""
        try:
            logger.info("\n📊 RESPONSE GENERATION DETAILS:")
            logger.info(f"   Thread ID: {email['thread_id']}")
            logger.info(f"   Subject: {email.get('subject', 'No Subject')}")
            logger.info(f"   Guest Message Length: {len(email['thread_message'])} characters")
            logger.info(f"   Generated Response Length: {len(response)} characters")
            logger.info(f"   Similar Conversations Used: {len(similar_conversations)}")

            if similar_conversations:
                logger.info("   Similarity Scores:")
                for i, conv in enumerate(similar_conversations, 1):
                    score = conv.get("score", 0)
                    thread_id = conv.get("thread_id", "Unknown")
                    logger.info(f"     {i}. Thread {thread_id}: {score:.3f}")

        except Exception as e:
            logger.error(f"Error logging response details: {e}")

    def get_statistics(self):
        """Get and display statistics about the email collections"""
        try:
            logger.info("=== EMAIL COLLECTION STATISTICS ===")

            # Original emails stats
            total_original = self.original_emails_col.count_documents({})
            guest_count = self.original_emails_col.count_documents({"sender": "Guest"})
            bsri_count = self.original_emails_col.count_documents({"sender": "BSRI Team"})
            events_legacy = self.original_emails_col.count_documents({"sender": "Events Team"})

            # Embedded emails stats
            total_embedded = self.email_embeddings_col.count_documents({})
            embedded_guest = self.email_embeddings_col.count_documents({"sender": "Guest"})
            embedded_bsri = self.email_embeddings_col.count_documents({"sender": "BSRI Team"})
            embedded_events_legacy = self.email_embeddings_col.count_documents({"sender": "Events Team"})

            logger.info(f"Original Emails: {total_original} total")
            logger.info(f"  - Guest: {guest_count}")
            logger.info(f"  - BSRI Team: {bsri_count}")
            if events_legacy > 0:
                logger.info(f"  - Events Team (legacy): {events_legacy}")

            logger.info(f"Embedded Emails: {total_embedded} total")
            logger.info(f"  - Guest: {embedded_guest}")
            logger.info(f"  - BSRI Team: {embedded_bsri}")
            if embedded_events_legacy > 0:
                logger.info(f"  - Events Team (legacy): {embedded_events_legacy}")

            # Coverage
            coverage = (total_embedded / total_original * 100) if total_original > 0 else 0
            logger.info(f"Embedding Coverage: {coverage:.1f}%")

            # Recent activity
            recent_date = datetime.now() - timedelta(days=7)
            recent_guest = self.original_emails_col.count_documents({
                "sender": "Guest",
                "date": {"$gte": recent_date}
            })
            recent_bsri = self.original_emails_col.count_documents({
                "sender": "BSRI Team",
                "date": {"$gte": recent_date}
            })

            logger.info(f"Recent Activity (Last 7 days):")
            logger.info(f"  - Guest messages: {recent_guest}")
            logger.info(f"  - BSRI Team messages: {recent_bsri}")

        except Exception as e:
            logger.error(f"Error getting statistics: {e}")

def main():
    """Main function"""
    try:
        generator = EmailResponseGenerator()

        # Show current statistics
        generator.get_statistics()

        # Process unanswered emails
        # Adjust parameters as needed:
        # - days_back: How many days back to look for unanswered emails
        # - limit: Maximum number of emails to process
        # - k_similar: Number of similar conversations to use for context
        generator.process_unanswered_emails(
            days_back=7,    # Look back 7 days
            limit=3,        # Process up to 3 emails
            k_similar=3     # Use 3 similar conversations for context
        )

    except Exception as e:
        logger.error(f"Application error: {e}")
        raise

if __name__ == "__main__":
    main()
