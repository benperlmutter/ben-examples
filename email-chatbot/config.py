#!/usr/bin/env python3
"""
Configuration file for the Email Chatbot Web Application

This file contains all configurable settings for the web application.
You can modify these values or override them with environment variables.
"""

import os

# Web Server Configuration
class WebConfig:
    """Web server configuration settings"""
    
    # Server settings
    HOST = os.environ.get('HOST', '0.0.0.0')  # Listen on all interfaces
    PORT = int(os.environ.get('PORT', 8080))  # Default port 8080 (change this!)
    DEBUG = os.environ.get('DEBUG', 'True').lower() == 'true'
    
    # Flask settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')
    
    # Application settings
    AUTO_REFRESH_INTERVAL = int(os.environ.get('AUTO_REFRESH_INTERVAL', 30))  # seconds
    DEFAULT_DAYS_BACK = int(os.environ.get('DEFAULT_DAYS_BACK', 30))
    DEFAULT_EMAIL_LIMIT = int(os.environ.get('DEFAULT_EMAIL_LIMIT', 20))
    
    # Processing settings
    BATCH_SIZE = int(os.environ.get('BATCH_SIZE', 50))
    MAX_SIMILAR_CONVERSATIONS = int(os.environ.get('MAX_SIMILAR_CONVERSATIONS', 3))

# Database Configuration
class DatabaseConfig:
    """Database configuration settings"""
    
    # MongoDB settings
    DATABASE_NAME = os.environ.get('DATABASE_NAME', 'email_chatbot')
    ORIGINAL_EMAILS_COLLECTION = os.environ.get('ORIGINAL_EMAILS_COLLECTION', 'original_emails')
    EMAIL_EMBEDDINGS_COLLECTION = os.environ.get('EMAIL_EMBEDDINGS_COLLECTION', 'email_embeddings')

# AI/ML Configuration
class AIConfig:
    """AI and ML configuration settings"""
    
    # Embedding model settings
    EMBEDDING_MODEL = os.environ.get('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
    EMBEDDING_DIMENSION = int(os.environ.get('EMBEDDING_DIMENSION', 384))
    
    # OpenAI settings
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-35-turbo')
    OPENAI_TEMPERATURE = float(os.environ.get('OPENAI_TEMPERATURE', 0.7))
    OPENAI_MAX_TOKENS = int(os.environ.get('OPENAI_MAX_TOKENS', 500))

# Logging Configuration
class LoggingConfig:
    """Logging configuration settings"""
    
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
    LOG_FILE = os.environ.get('LOG_FILE', 'webapp.log')
    LOG_FORMAT = os.environ.get('LOG_FORMAT', '%(asctime)s - %(levelname)s - %(message)s')

# Quick port configuration options
# Uncomment one of these or set the PORT environment variable

# Common development ports
# WebConfig.PORT = 3000  # React/Node.js style
# WebConfig.PORT = 5000  # Flask default
# WebConfig.PORT = 8000  # Django style
# WebConfig.PORT = 8080  # Common alternative (current default)
# WebConfig.PORT = 9000  # High port

# Custom port examples
# WebConfig.PORT = 7777  # Custom port
# WebConfig.PORT = 4200  # Angular style

def get_config_summary():
    """Get a summary of current configuration"""
    return {
        'web': {
            'host': WebConfig.HOST,
            'port': WebConfig.PORT,
            'debug': WebConfig.DEBUG,
            'auto_refresh_interval': WebConfig.AUTO_REFRESH_INTERVAL
        },
        'database': {
            'database_name': DatabaseConfig.DATABASE_NAME,
            'original_emails_collection': DatabaseConfig.ORIGINAL_EMAILS_COLLECTION,
            'email_embeddings_collection': DatabaseConfig.EMAIL_EMBEDDINGS_COLLECTION
        },
        'ai': {
            'embedding_model': AIConfig.EMBEDDING_MODEL,
            'openai_model': AIConfig.OPENAI_MODEL,
            'openai_temperature': AIConfig.OPENAI_TEMPERATURE
        }
    }

if __name__ == "__main__":
    # Print current configuration
    import json
    config = get_config_summary()
    print("Current Email Chatbot Configuration:")
    print("=" * 50)
    print(json.dumps(config, indent=2))
    print("=" * 50)
    print(f"Web application will run on: http://localhost:{WebConfig.PORT}")

