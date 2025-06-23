#!/usr/bin/env python3
"""
Migration script to update existing email documents with the new sender logic
This script will:
1. Find all emails with sender "Events Team"
2. Re-evaluate their sender based on the from_header using the new logic
3. Update the sender field to "BSRI Team" if they have @bigsurriverinn.com domain
"""
import pymongo
import json
import logging
import re
from typing import Dict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SenderDataMigrator:
    def __init__(self):
        self.setup_database()
    
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
    
    def determine_sender(self, from_header: str) -> str:
        """Determine sender based on email domain (same logic as updated files)"""
        if not from_header:
            return "Guest"
        
        # Extract email address from header (handles formats like "Name <email@domain.com>")
        email_match = re.search(r'<([^>]+)>|([^\s<>]+@[^\s<>]+)', from_header)
        if email_match:
            email_address = email_match.group(1) or email_match.group(2)
            if email_address and "@bigsurriverinn.com" in email_address.lower():
                return "BSRI Team"
        
        return "Guest"
    
    def analyze_existing_data(self):
        """Analyze existing data to see what needs migration"""
        try:
            logger.info("Analyzing existing data...")
            
            # Count current sender distribution in original emails
            total_count = self.original_emails_col.count_documents({})
            guest_count = self.original_emails_col.count_documents({"sender": "Guest"})
            events_team_count = self.original_emails_col.count_documents({"sender": "Events Team"})
            bsri_team_count = self.original_emails_col.count_documents({"sender": "BSRI Team"})
            
            logger.info("=== Original Emails Collection Analysis ===")
            logger.info(f"Total documents: {total_count}")
            logger.info(f"Guest: {guest_count}")
            logger.info(f"Events Team (old): {events_team_count}")
            logger.info(f"BSRI Team (new): {bsri_team_count}")
            
            # Count current sender distribution in embeddings
            total_embedded = self.email_embeddings_col.count_documents({})
            embedded_guest = self.email_embeddings_col.count_documents({"sender": "Guest"})
            embedded_events = self.email_embeddings_col.count_documents({"sender": "Events Team"})
            embedded_bsri = self.email_embeddings_col.count_documents({"sender": "BSRI Team"})
            
            logger.info("=== Email Embeddings Collection Analysis ===")
            logger.info(f"Total documents: {total_embedded}")
            logger.info(f"Guest: {embedded_guest}")
            logger.info(f"Events Team (old): {embedded_events}")
            logger.info(f"BSRI Team (new): {embedded_bsri}")
            
            return events_team_count, embedded_events
            
        except Exception as e:
            logger.error(f"Error analyzing existing data: {e}")
            return 0, 0
    
    def migrate_original_emails(self, dry_run: bool = True):
        """Migrate sender field in original emails collection"""
        try:
            logger.info(f"{'DRY RUN: ' if dry_run else ''}Migrating original emails...")
            
            # Find all documents with "Events Team" sender
            events_team_docs = list(self.original_emails_col.find({"sender": "Events Team"}))
            
            if not events_team_docs:
                logger.info("No 'Events Team' documents found to migrate")
                return 0
            
            logger.info(f"Found {len(events_team_docs)} documents to evaluate")
            
            updated_count = 0
            unchanged_count = 0
            
            for doc in events_team_docs:
                from_header = doc.get("from_header", "")
                current_sender = doc.get("sender", "")
                new_sender = self.determine_sender(from_header)
                
                if new_sender != current_sender:
                    logger.info(f"Will update: {from_header} -> {new_sender}")
                    
                    if not dry_run:
                        # Update the document
                        result = self.original_emails_col.update_one(
                            {"_id": doc["_id"]},
                            {"$set": {"sender": new_sender}}
                        )
                        if result.modified_count > 0:
                            updated_count += 1
                    else:
                        updated_count += 1
                else:
                    unchanged_count += 1
            
            logger.info(f"{'DRY RUN: ' if dry_run else ''}Migration complete!")
            logger.info(f"Documents that would be updated: {updated_count}")
            logger.info(f"Documents that would remain unchanged: {unchanged_count}")
            
            return updated_count
            
        except Exception as e:
            logger.error(f"Error migrating original emails: {e}")
            return 0
    
    def migrate_email_embeddings(self, dry_run: bool = True):
        """Migrate sender field in email embeddings collection"""
        try:
            logger.info(f"{'DRY RUN: ' if dry_run else ''}Migrating email embeddings...")
            
            # Find all documents with "Events Team" sender
            events_team_docs = list(self.email_embeddings_col.find({"sender": "Events Team"}))
            
            if not events_team_docs:
                logger.info("No 'Events Team' documents found in embeddings to migrate")
                return 0
            
            logger.info(f"Found {len(events_team_docs)} embedding documents to evaluate")
            
            updated_count = 0
            unchanged_count = 0
            
            for doc in events_team_docs:
                from_header = doc.get("from_header", "")
                current_sender = doc.get("sender", "")
                new_sender = self.determine_sender(from_header)
                
                if new_sender != current_sender:
                    logger.info(f"Will update embedding: {from_header} -> {new_sender}")
                    
                    if not dry_run:
                        # Update the document
                        result = self.email_embeddings_col.update_one(
                            {"_id": doc["_id"]},
                            {"$set": {"sender": new_sender}}
                        )
                        if result.modified_count > 0:
                            updated_count += 1
                    else:
                        updated_count += 1
                else:
                    unchanged_count += 1
            
            logger.info(f"{'DRY RUN: ' if dry_run else ''}Embedding migration complete!")
            logger.info(f"Documents that would be updated: {updated_count}")
            logger.info(f"Documents that would remain unchanged: {unchanged_count}")
            
            return updated_count
            
        except Exception as e:
            logger.error(f"Error migrating email embeddings: {e}")
            return 0
    
    def run_migration(self, dry_run: bool = True):
        """Run the complete migration process"""
        try:
            logger.info("=" * 60)
            logger.info(f"STARTING SENDER DATA MIGRATION ({'DRY RUN' if dry_run else 'LIVE RUN'})")
            logger.info("=" * 60)
            
            # Analyze current state
            original_events_count, embedded_events_count = self.analyze_existing_data()
            
            if original_events_count == 0 and embedded_events_count == 0:
                logger.info("No migration needed - no 'Events Team' documents found")
                return
            
            # Migrate original emails
            if original_events_count > 0:
                logger.info("\n" + "=" * 40)
                updated_original = self.migrate_original_emails(dry_run=dry_run)
            
            # Migrate embeddings
            if embedded_events_count > 0:
                logger.info("\n" + "=" * 40)
                updated_embeddings = self.migrate_email_embeddings(dry_run=dry_run)
            
            # Final summary
            logger.info("\n" + "=" * 60)
            logger.info("MIGRATION SUMMARY")
            logger.info("=" * 60)
            if original_events_count > 0:
                logger.info(f"Original emails: {updated_original} documents {'would be ' if dry_run else ''}updated")
            if embedded_events_count > 0:
                logger.info(f"Email embeddings: {updated_embeddings} documents {'would be ' if dry_run else ''}updated")
            
            if dry_run:
                logger.info("\n🔍 This was a DRY RUN - no actual changes were made")
                logger.info("To perform the actual migration, run with dry_run=False")
            else:
                logger.info("\n✅ Migration completed successfully!")
                
                # Show updated statistics
                logger.info("\nUpdated statistics:")
                self.analyze_existing_data()
            
        except Exception as e:
            logger.error(f"Error in migration process: {e}")
            raise

def main():
    """Main function"""
    try:
        migrator = SenderDataMigrator()
        
        # First run as dry run to see what would be changed
        migrator.run_migration(dry_run=True)
        
        # Uncomment the line below to perform the actual migration
        # migrator.run_migration(dry_run=False)
        
    except Exception as e:
        logger.error(f"Application error: {e}")
        raise

if __name__ == "__main__":
    main()
