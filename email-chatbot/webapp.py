#!/usr/bin/env python3
"""
Email Chatbot Web Application

A Flask web application that combines all four "aug" scripts into a unified interface:
1. Update with new emails and generate embeddings
2. View unanswered guest emails
3. Generate responses to specific guest emails

Features:
- Real-time email processing
- Interactive email management
- Response generation with RAG
- System statistics and monitoring
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
import logging
import json
import os
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
import time

# Import our aug modules
from aug_update_emails import EmailUpdater
from aug_generate_embeddings import IncrementalEmailEmbeddingGenerator
from aug_generate_responses import EmailResponseGenerator
from config import WebConfig, DatabaseConfig, AIConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = WebConfig.SECRET_KEY

class EmailChatbotService:
    """Service class that integrates all aug components"""
    
    def __init__(self):
        self.email_updater = None
        self.embedding_generator = None
        self.response_generator = None
        self.last_update_time = None
        self.is_processing = False
        
    def initialize_components(self):
        """Initialize all components (lazy loading)"""
        try:
            if not self.email_updater:
                logger.info("Initializing EmailUpdater...")
                self.email_updater = EmailUpdater()
                
            if not self.embedding_generator:
                logger.info("Initializing EmbeddingGenerator...")
                self.embedding_generator = IncrementalEmailEmbeddingGenerator()
                
            if not self.response_generator:
                logger.info("Initializing ResponseGenerator...")
                self.response_generator = EmailResponseGenerator()
                
            logger.info("All components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            return False
    
    def get_system_statistics(self) -> Dict:
        """Get comprehensive system statistics"""
        try:
            if not self.initialize_components():
                return {"error": "Failed to initialize components"}
            
            # Get statistics from embedding generator (has comprehensive stats)
            stats = {}
            
            # Original emails stats
            total_original = self.embedding_generator.original_emails_col.count_documents({})
            guest_count = self.embedding_generator.original_emails_col.count_documents({"sender": "Guest"})
            bsri_count = self.embedding_generator.original_emails_col.count_documents({"sender": "BSRI Team"})
            events_legacy = self.embedding_generator.original_emails_col.count_documents({"sender": "Events Team"})
            
            # Embedded emails stats
            total_embedded = self.embedding_generator.email_embeddings_col.count_documents({})
            embedded_guest = self.embedding_generator.email_embeddings_col.count_documents({"sender": "Guest"})
            embedded_bsri = self.embedding_generator.email_embeddings_col.count_documents({"sender": "BSRI Team"})
            embedded_events_legacy = self.embedding_generator.email_embeddings_col.count_documents({"sender": "Events Team"})
            
            # Recent activity (last 7 days)
            recent_date = datetime.now() - timedelta(days=7)
            recent_guest = self.embedding_generator.original_emails_col.count_documents({
                "sender": "Guest",
                "date": {"$gte": recent_date}
            })
            recent_bsri = self.embedding_generator.original_emails_col.count_documents({
                "sender": "BSRI Team", 
                "date": {"$gte": recent_date}
            })
            
            # Calculate coverage
            coverage = (total_embedded / total_original * 100) if total_original > 0 else 0
            emails_needing_embeddings = total_original - total_embedded
            
            stats = {
                "original_emails": {
                    "total": total_original,
                    "guest": guest_count,
                    "bsri_team": bsri_count,
                    "events_legacy": events_legacy
                },
                "embedded_emails": {
                    "total": total_embedded,
                    "guest": embedded_guest,
                    "bsri_team": embedded_bsri,
                    "events_legacy": embedded_events_legacy
                },
                "coverage": {
                    "percentage": round(coverage, 1),
                    "emails_needing_embeddings": emails_needing_embeddings
                },
                "recent_activity": {
                    "guest_messages": recent_guest,
                    "bsri_messages": recent_bsri
                },
                "last_update": self.last_update_time.isoformat() if self.last_update_time else None,
                "is_processing": self.is_processing
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting system statistics: {e}")
            return {"error": str(e)}
    
    def update_emails_and_embeddings(self) -> Dict:
        """Update with new emails and generate embeddings"""
        try:
            if self.is_processing:
                return {"error": "System is already processing. Please wait."}
            
            self.is_processing = True
            result = {"success": False, "new_emails": 0, "new_embeddings": 0, "messages": []}
            
            if not self.initialize_components():
                result["error"] = "Failed to initialize components"
                return result
            
            # Step 1: Check for new emails
            result["messages"].append("Checking for new emails...")
            logger.info("Starting email update process...")
            
            # Get count before update
            emails_before = self.email_updater.original_emails_col.count_documents({})
            
            # Update emails
            self.email_updater.check_for_new_emails()
            
            # Get count after update
            emails_after = self.email_updater.original_emails_col.count_documents({})
            new_emails_count = emails_after - emails_before
            
            result["new_emails"] = new_emails_count
            result["messages"].append(f"Found {new_emails_count} new emails")
            
            # Step 2: Generate embeddings for new emails
            if new_emails_count > 0:
                result["messages"].append("Generating embeddings for new emails...")
                logger.info("Generating embeddings for new emails...")
                
                new_embeddings_count = self.embedding_generator.process_new_embeddings(batch_size=50)
                result["new_embeddings"] = new_embeddings_count
                result["messages"].append(f"Generated {new_embeddings_count} new embeddings")
            else:
                result["messages"].append("No new emails found, checking for missing embeddings...")
                # Still check for any emails that might need embeddings
                new_embeddings_count = self.embedding_generator.process_new_embeddings(batch_size=50)
                result["new_embeddings"] = new_embeddings_count
                if new_embeddings_count > 0:
                    result["messages"].append(f"Generated {new_embeddings_count} missing embeddings")
            
            self.last_update_time = datetime.now()
            result["success"] = True
            result["messages"].append("Update completed successfully!")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in update_emails_and_embeddings: {e}")
            return {"error": str(e), "success": False}
        finally:
            self.is_processing = False
    
    def get_unanswered_emails(self, days_back: int = 30, limit: int = 20) -> List[Dict]:
        """Get list of unanswered guest emails"""
        try:
            if not self.initialize_components():
                return []
            
            unanswered_emails = self.response_generator.find_unanswered_guest_emails(
                days_back=days_back, 
                limit=limit
            )
            
            # Format for web display
            formatted_emails = []
            for email in unanswered_emails:
                formatted_email = {
                    "thread_id": email.get("thread_id", ""),
                    "message_id": email.get("message_id", ""),
                    "subject": email.get("subject", "No Subject"),
                    "date": email.get("date", datetime.now()).isoformat(),
                    "from_header": email.get("from_header", ""),
                    "snippet": email.get("snippet", ""),
                    "thread_message": email.get("thread_message", ""),
                    "thread_message_preview": email.get("thread_message", "")[:200] + "..." if len(email.get("thread_message", "")) > 200 else email.get("thread_message", "")
                }
                formatted_emails.append(formatted_email)
            
            return formatted_emails
            
        except Exception as e:
            logger.error(f"Error getting unanswered emails: {e}")
            return []
    
    def generate_response_for_email(self, thread_id: str, message_id: str) -> Dict:
        """Generate a response for a specific email"""
        try:
            if not self.initialize_components():
                return {"error": "Failed to initialize components"}
            
            # Find the specific email
            email = self.response_generator.original_emails_col.find_one({
                "thread_id": thread_id,
                "message_id": message_id
            })
            
            if not email:
                return {"error": "Email not found"}
            
            guest_message = email.get("thread_message", "")
            if not guest_message:
                return {"error": "No message content found"}
            
            # Find similar conversations
            similar_conversations = self.response_generator.find_similar_conversations(
                guest_message, k=3
            )
            
            if not similar_conversations:
                return {"error": "No similar conversations found for context"}
            
            # Build RAG context
            rag_context = self.response_generator.build_rag_context(
                guest_message, similar_conversations
            )
            
            # Generate response
            response = self.response_generator.generate_response(guest_message, rag_context)
            
            if not response:
                return {"error": "Failed to generate response"}
            
            return {
                "success": True,
                "response": response,
                "similar_conversations_count": len(similar_conversations),
                "similarity_scores": [conv.get("score", 0) for conv in similar_conversations]
            }
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {"error": str(e)}

# Global service instance
email_service = EmailChatbotService()

# Routes
@app.route('/')
def index():
    """Main dashboard"""
    try:
        stats = email_service.get_system_statistics()
        return render_template('index.html', stats=stats)
    except Exception as e:
        logger.error(f"Error in index route: {e}")
        flash(f"Error loading dashboard: {str(e)}", "error")
        return render_template('index.html', stats={"error": str(e)})

@app.route('/api/stats')
def api_stats():
    """API endpoint for system statistics"""
    return jsonify(email_service.get_system_statistics())

@app.route('/api/update', methods=['POST'])
def api_update():
    """API endpoint to update emails and embeddings"""
    result = email_service.update_emails_and_embeddings()
    return jsonify(result)

@app.route('/unanswered')
def unanswered_emails():
    """View unanswered guest emails"""
    try:
        days_back = request.args.get('days_back', 30, type=int)
        limit = request.args.get('limit', 20, type=int)
        
        emails = email_service.get_unanswered_emails(days_back=days_back, limit=limit)
        return render_template('unanswered.html', emails=emails, days_back=days_back, limit=limit)
    except Exception as e:
        logger.error(f"Error in unanswered_emails route: {e}")
        flash(f"Error loading unanswered emails: {str(e)}", "error")
        return render_template('unanswered.html', emails=[], days_back=30, limit=20)

@app.route('/api/unanswered')
def api_unanswered():
    """API endpoint for unanswered emails"""
    days_back = request.args.get('days_back', 30, type=int)
    limit = request.args.get('limit', 20, type=int)
    emails = email_service.get_unanswered_emails(days_back=days_back, limit=limit)
    return jsonify(emails)

@app.route('/api/generate_response', methods=['POST'])
def api_generate_response():
    """API endpoint to generate response for specific email"""
    data = request.get_json()
    thread_id = data.get('thread_id')
    message_id = data.get('message_id')
    
    if not thread_id or not message_id:
        return jsonify({"error": "Missing thread_id or message_id"}), 400
    
    result = email_service.generate_response_for_email(thread_id, message_id)
    return jsonify(result)

if __name__ == '__main__':
    # Use configuration from config.py
    print(f"Starting Email Chatbot Web Application on {WebConfig.HOST}:{WebConfig.PORT}")
    print(f"Debug mode: {WebConfig.DEBUG}")
    print(f"Access the application at: http://localhost:{WebConfig.PORT}")

    app.run(debug=WebConfig.DEBUG, host=WebConfig.HOST, port=WebConfig.PORT)
