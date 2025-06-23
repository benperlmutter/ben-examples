import pymongo
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Set
from sentence_transformers import SentenceTransformer, util
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IncrementalEmailEmbeddingGenerator:
    def __init__(self):
        self.setup_database()
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
            self.email_embeddings_col = self.email_chatbot_db.email_embeddings  # New collection name
            
            # Create indexes for the email embeddings collection
            self.create_embedding_indexes()
            
            logger.info("Database connection established successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup database: {e}")
            raise
    
    def create_embedding_indexes(self):
        """Create indexes for the email embeddings collection"""
        try:
            # Index on message_id for deduplication and fast lookups
            self.email_embeddings_col.create_index("message_id", unique=True)
            # Index on thread_id for thread queries
            self.email_embeddings_col.create_index("thread_id")
            # Index on date for chronological queries
            self.email_embeddings_col.create_index("date")
            # Index on sender for filtering
            self.email_embeddings_col.create_index("sender")
            # Compound index for thread queries by date
            self.email_embeddings_col.create_index([("thread_id", 1), ("date", 1)])
            # Index on embedded_at for tracking when embeddings were created
            self.email_embeddings_col.create_index("embedded_at")
            
            logger.info("Email embeddings collection indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Index creation warning (may already exist): {e}")
    
    def setup_model(self):
        """Initialize the SentenceTransformer model"""
        try:
            logger.info("Loading SentenceTransformer model...")
            self.model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
            logger.info("SentenceTransformer model loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer model: {e}")
            raise
    
    def get_existing_embedded_message_ids(self) -> Set[str]:
        """Get set of message IDs that already have embeddings"""
        try:
            logger.info("Fetching existing embedded message IDs...")
            existing_ids = set(self.email_embeddings_col.distinct("message_id"))
            logger.info(f"Found {len(existing_ids)} existing embedded messages")
            return existing_ids
            
        except Exception as e:
            logger.error(f"Error fetching existing embedded message IDs: {e}")
            return set()
    
    def get_emails_needing_embeddings(self, existing_embedded_ids: Set[str]) -> List[Dict]:
        """Get emails from original collection that don't have embeddings yet"""
        try:
            logger.info("Finding emails that need embeddings...")
            
            # Query for emails not in the embedded collection
            query = {"message_id": {"$nin": list(existing_embedded_ids)}} if existing_embedded_ids else {}
            
            emails_needing_embeddings = list(
                self.original_emails_col.find(query).sort("date", 1)
            )
            
            logger.info(f"Found {len(emails_needing_embeddings)} emails needing embeddings")
            return emails_needing_embeddings
            
        except Exception as e:
            logger.error(f"Error finding emails needing embeddings: {e}")
            return []
    
    def preprocess_text_for_embedding(self, text: str) -> str:
        """Preprocess text before generating embeddings"""
        if not text:
            return ""
        
        # Remove excessive whitespace
        text = " ".join(text.split())
        
        # Truncate very long messages (model has token limits)
        max_length = 500  # Adjust based on your needs
        if len(text) > max_length:
            text = text[:max_length] + "..."
            logger.debug(f"Text truncated to {max_length} characters")
        
        return text
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate vector embedding for given text"""
        try:
            if not text or not text.strip():
                logger.warning("Empty text provided for embedding")
                return []
            
            # Preprocess text
            processed_text = self.preprocess_text_for_embedding(text)
            
            # Generate embedding
            embedding = self.model.encode(processed_text)
            
            # Convert to list for MongoDB storage
            return embedding.tolist()
            
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return []
    
    def create_embedded_document(self, original_doc: Dict) -> Optional[Dict]:
        """Create embedded document from original email document"""
        try:
            # Generate embedding for the thread message
            message_embedding = self.generate_embedding(original_doc.get("thread_message", ""))
            
            if not message_embedding:
                logger.warning(f"Failed to generate embedding for message: {original_doc.get('message_id', 'unknown')}")
                return None
            
            # Create embedded document with all original fields plus embedding
            embedded_doc = {
                "message_id": original_doc.get("message_id", ""),
                "thread_id": original_doc.get("thread_id", ""),
                "date": original_doc.get("date", datetime.now()),
                "sender": original_doc.get("sender", ""),
                "subject": original_doc.get("subject", ""),
                "snippet": original_doc.get("snippet", ""),
                "thread_message": original_doc.get("thread_message", ""),
                "from_header": original_doc.get("from_header", ""),
                "message_embeddings": message_embedding,
                "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
                "embedding_dimension": len(message_embedding),
                "original_created_at": original_doc.get("created_at", datetime.now()),
                "original_updated_at": original_doc.get("updated_at", datetime.now()),
                "embedded_at": datetime.now()
            }
            
            return embedded_doc
            
        except Exception as e:
            logger.error(f"Error creating embedded document: {e}")
            return None
    
    def process_new_embeddings(self, batch_size: int = 50) -> int:
        """Process only emails that don't have embeddings yet"""
        try:
            logger.info("Starting incremental embedding generation...")
            
            # Get existing embedded message IDs
            existing_embedded_ids = self.get_existing_embedded_message_ids()
            
            # Get emails that need embeddings
            emails_needing_embeddings = self.get_emails_needing_embeddings(existing_embedded_ids)
            
            if not emails_needing_embeddings:
                logger.info("No new emails found that need embeddings")
                return 0
            
            logger.info(f"Processing {len(emails_needing_embeddings)} new emails for embedding generation")
            
            processed_count = 0
            successful_embeddings = 0
            failed_embeddings = 0
            batch_docs = []
            
            for i, email_doc in enumerate(emails_needing_embeddings):
                try:
                    # Create embedded document
                    embedded_doc = self.create_embedded_document(email_doc)
                    
                    if embedded_doc:
                        batch_docs.append(embedded_doc)
                        
                        # Process batch when it reaches batch_size
                        if len(batch_docs) >= batch_size:
                            batch_success, batch_failed = self.insert_batch(batch_docs)
                            successful_embeddings += batch_success
                            failed_embeddings += batch_failed
                            batch_docs = []
                            
                            logger.info(f"Progress: {i+1}/{len(emails_needing_embeddings)} processed, "
                                      f"{successful_embeddings} successful, {failed_embeddings} failed")
                    else:
                        failed_embeddings += 1
                    
                    processed_count += 1
                    
                except Exception as e:
                    logger.error(f"Error processing email {email_doc.get('message_id', 'unknown')}: {e}")
                    failed_embeddings += 1
                    processed_count += 1
                    continue
            
            # Process remaining batch
            if batch_docs:
                batch_success, batch_failed = self.insert_batch(batch_docs)
                successful_embeddings += batch_success
                failed_embeddings += batch_failed
            
            logger.info("=== Incremental Embedding Generation Complete ===")
            logger.info(f"Emails processed: {processed_count}")
            logger.info(f"Successful embeddings: {successful_embeddings}")
            logger.info(f"Failed embeddings: {failed_embeddings}")
            
            if successful_embeddings > 0:
                self.print_recent_embeddings(successful_embeddings)
            
            return successful_embeddings
            
        except Exception as e:
            logger.error(f"Error in process_new_embeddings: {e}")
            raise
    
    def insert_batch(self, batch_docs: List[Dict]) -> tuple[int, int]:
        """Insert a batch of embedded documents, return (successful, failed) counts"""
        successful = 0
        failed = 0
        
        for doc in batch_docs:
            try:
                # Insert only if doesn't exist (using message_id uniqueness)
                self.email_embeddings_col.insert_one(doc)
                successful += 1
                logger.debug(f"Successfully embedded: {doc.get('message_id', 'unknown')}")
                
            except pymongo.errors.DuplicateKeyError:
                # Document already exists (shouldn't happen with our pre-filtering, but just in case)
                logger.debug(f"Embedding already exists for: {doc.get('message_id', 'unknown')}")
                failed += 1
                
            except Exception as e:
                logger.error(f"Error inserting embedding for {doc.get('message_id', 'unknown')}: {e}")
                failed += 1
        
        return successful, failed
    
    def print_recent_embeddings(self, count: int):
        """Print information about recently created embeddings"""
        try:
            logger.info(f"=== Recently Created Embeddings (Last {count}) ===")
            
            recent_embeddings = self.email_embeddings_col.find().sort("embedded_at", -1).limit(count)
            
            for embedding in recent_embeddings:
                logger.info(f"📧 {embedding.get('date', 'unknown')} - "
                          f"{embedding.get('sender', 'unknown')}: "
                          f"{embedding.get('subject', 'No subject')[:50]}...")
            
        except Exception as e:
            logger.error(f"Error printing recent embeddings: {e}")
    
    def get_collection_stats(self):
        """Get and display statistics about both collections"""
        try:
            # Original emails stats
            total_original = self.original_emails_col.count_documents({})
            original_guest = self.original_emails_col.count_documents({"sender": "Guest"})
            original_bsri = self.original_emails_col.count_documents({"sender": "BSRI Team"})
            # Also check for legacy "Events Team" entries
            original_events_legacy = self.original_emails_col.count_documents({"sender": "Events Team"})

            # Embedded emails stats
            total_embedded = self.email_embeddings_col.count_documents({})
            embedded_guest = self.email_embeddings_col.count_documents({"sender": "Guest"})
            embedded_bsri = self.email_embeddings_col.count_documents({"sender": "BSRI Team"})
            # Also check for legacy "Events Team" entries
            embedded_events_legacy = self.email_embeddings_col.count_documents({"sender": "Events Team"})
            
            # Calculate coverage
            coverage_percentage = (total_embedded / total_original * 100) if total_original > 0 else 0
            
            logger.info("=== Collection Statistics ===")
            logger.info(f"Original Emails Collection:")
            logger.info(f"  Total: {total_original}")
            logger.info(f"  Guest: {original_guest}")
            logger.info(f"  BSRI Team: {original_bsri}")
            if original_events_legacy > 0:
                logger.info(f"  Events Team (legacy): {original_events_legacy}")
            logger.info(f"")
            logger.info(f"Email Embeddings Collection:")
            logger.info(f"  Total: {total_embedded}")
            logger.info(f"  Guest: {embedded_guest}")
            logger.info(f"  BSRI Team: {embedded_bsri}")
            if embedded_events_legacy > 0:
                logger.info(f"  Events Team (legacy): {embedded_events_legacy}")
            logger.info(f"")
            logger.info(f"Coverage: {coverage_percentage:.1f}% ({total_embedded}/{total_original})")
            
            # Emails needing embeddings
            emails_needing_embeddings = total_original - total_embedded
            if emails_needing_embeddings > 0:
                logger.info(f"⚠️  Emails needing embeddings: {emails_needing_embeddings}")
            else:
                logger.info("✅ All emails have embeddings!")
            
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
    
    def verify_embedding_integrity(self):
        """Verify that all embeddings are valid and complete"""
        try:
            logger.info("Verifying embedding integrity...")
            
            # Check for documents with missing or invalid embeddings
            invalid_embeddings = self.email_embeddings_col.count_documents({
                "$or": [
                    {"message_embeddings": {"$exists": False}},
                    {"message_embeddings": []},
                    {"message_embeddings": None}
                ]
            })
            
            if invalid_embeddings > 0:
                logger.warning(f"Found {invalid_embeddings} documents with invalid embeddings")
            else:
                logger.info("✅ All embeddings are valid")
            
            # Check embedding dimensions
            sample_doc = self.email_embeddings_col.find_one({"message_embeddings": {"$exists": True}})
            if sample_doc and "message_embeddings" in sample_doc:
                expected_dim = 384  # all-MiniLM-L6-v2 dimension
                actual_dim = len(sample_doc["message_embeddings"])
                
                if actual_dim == expected_dim:
                    logger.info(f"✅ Embedding dimensions correct: {actual_dim}")
                else:
                    logger.warning(f"⚠️  Unexpected embedding dimension: {actual_dim} (expected {expected_dim})")
            
        except Exception as e:
            logger.error(f"Error verifying embedding integrity: {e}")
    
    def cleanup_invalid_embeddings(self):
        """Remove documents with invalid embeddings"""
        try:
            logger.info("Cleaning up invalid embeddings...")
            
            result = self.email_embeddings_col.delete_many({
                "$or": [
                    {"message_embeddings": {"$exists": False}},
                    {"message_embeddings": []},
                    {"message_embeddings": None}
                ]
            })
            
            if result.deleted_count > 0:
                logger.info(f"Removed {result.deleted_count} invalid embedding documents")
            else:
                logger.info("No invalid embeddings found to clean up")
            
        except Exception as e:
            logger.error(f"Error cleaning up invalid embeddings: {e}")

def main():
    """Main function - designed to be run after new emails are added"""
    try:
        generator = IncrementalEmailEmbeddingGenerator()
        
        # Show current statistics
        logger.info("Checking current collection status...")
        generator.get_collection_stats()
        
        # Process only new emails that need embeddings
        new_embeddings_count = generator.process_new_embeddings(batch_size=50)
        
        if new_embeddings_count > 0:
            # Show updated statistics
            logger.info("Updated collection status:")
            generator.get_collection_stats()
            
            # Verify integrity of new embeddings
            generator.verify_embedding_integrity()
        
        logger.info("Incremental embedding generation completed successfully!")
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise

if __name__ == "__main__":
    main()