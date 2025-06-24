#!/usr/bin/env python3
"""
Startup script for the Email Chatbot Web Application

This script performs pre-flight checks and starts the Flask web application
with proper error handling and logging.
"""

import sys
import os
import json
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('webapp.log')
    ]
)
logger = logging.getLogger(__name__)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        logger.error("Python 3.8 or higher is required")
        return False
    logger.info(f"Python version: {sys.version}")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'flask',
        'pymongo', 
        'sentence_transformers',
        'openai',
        'google.auth',
        'beautifulsoup4'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            logger.info(f"✓ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            logger.error(f"✗ {package} is missing")
    
    if missing_packages:
        logger.error("Missing packages. Install with: pip install -r requirements.txt")
        return False
    
    return True

def check_credentials():
    """Check if credential files exist and are valid"""
    credential_files = [
        '../../../atlas-creds/atlas-creds.json',
        '../../../azure-gpt-creds/azure-gpt-creds.json',
        '../../../email-chatbot-creds/credentials.json'
    ]
    
    for cred_file in credential_files:
        if not os.path.exists(cred_file):
            logger.error(f"Credential file not found: {cred_file}")
            return False
        
        try:
            with open(cred_file, 'r') as f:
                json.load(f)
            logger.info(f"✓ {cred_file} is valid")
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in: {cred_file}")
            return False
    
    return True

def check_aug_scripts():
    """Check if aug scripts are available"""
    aug_scripts = [
        'aug_update_emails.py',
        'aug_generate_embeddings.py', 
        'aug_generate_responses.py'
    ]
    
    for script in aug_scripts:
        if not os.path.exists(script):
            logger.error(f"Required script not found: {script}")
            return False
        logger.info(f"✓ {script} found")
    
    return True

def test_database_connection():
    """Test MongoDB connection"""
    try:
        import pymongo
        
        with open('../../../atlas-creds/atlas-creds.json', 'r') as f:
            creds = json.load(f)
        
        client = pymongo.MongoClient(creds["mdb-connection-string"])
        client.admin.command('ping')
        
        # Check if collections exist
        db = client.email_chatbot
        collections = db.list_collection_names()
        
        if 'original_emails' not in collections:
            logger.warning("Collection 'original_emails' not found - run aug_collect_all_emails.py first")
        else:
            logger.info("✓ original_emails collection found")
            
        if 'email_embeddings' not in collections:
            logger.warning("Collection 'email_embeddings' not found - run aug_generate_embeddings.py first")
        else:
            logger.info("✓ email_embeddings collection found")
        
        logger.info("✓ Database connection successful")
        return True
        
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False

def test_azure_openai():
    """Test Azure OpenAI connection"""
    try:
        from openai import AzureOpenAI
        
        with open('../../../azure-gpt-creds/azure-gpt-creds.json', 'r') as f:
            creds = json.load(f)
        
        client = AzureOpenAI(
            api_version=creds["azure-api-version"],
            azure_endpoint=creds["azure-endpoint"],
            api_key=creds["azure-api-key"]
        )
        
        # Test with a minimal request
        response = client.chat.completions.create(
            model=creds["azure-deployment-name"],  # Use deployment name
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        logger.info("✓ Azure OpenAI connection successful")
        return True
        
    except Exception as e:
        logger.error(f"Azure OpenAI connection failed: {e}")
        return False

def run_preflight_checks():
    """Run all preflight checks"""
    logger.info("=" * 60)
    logger.info("STARTING EMAIL CHATBOT WEB APPLICATION")
    logger.info("=" * 60)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Credentials", check_credentials),
        ("Aug Scripts", check_aug_scripts),
        ("Database Connection", test_database_connection),
        ("Azure OpenAI", test_azure_openai)
    ]
    
    passed = 0
    total = len(checks)
    
    for check_name, check_func in checks:
        logger.info(f"\nChecking {check_name}...")
        try:
            if check_func():
                passed += 1
                logger.info(f"✓ {check_name} passed")
            else:
                logger.error(f"✗ {check_name} failed")
        except Exception as e:
            logger.error(f"✗ {check_name} failed with exception: {e}")
    
    logger.info(f"\nPreflight checks: {passed}/{total} passed")
    
    if passed == total:
        logger.info("✅ All checks passed! Starting web application...")
        return True
    elif passed >= 4:  # Core checks passed
        logger.warning("⚠️  Some checks failed, but core functionality should work")
        return True
    else:
        logger.error("❌ Critical checks failed. Please fix issues before starting.")
        return False

def start_webapp():
    """Start the Flask web application"""
    try:
        # Import configuration
        from config import WebConfig

        # Import and start the webapp
        from webapp import app

        logger.info("Starting Flask web application...")
        logger.info(f"Host: {WebConfig.HOST}")
        logger.info(f"Port: {WebConfig.PORT}")
        logger.info(f"Debug: {WebConfig.DEBUG}")
        logger.info(f"Access the application at: http://localhost:{WebConfig.PORT}")
        logger.info("Press Ctrl+C to stop the server")

        # Start the Flask app
        app.run(
            debug=WebConfig.DEBUG,
            host=WebConfig.HOST,
            port=WebConfig.PORT,
            use_reloader=False  # Disable reloader to avoid double startup
        )
        
    except KeyboardInterrupt:
        logger.info("\nShutting down web application...")
    except Exception as e:
        logger.error(f"Error starting web application: {e}")
        sys.exit(1)

def main():
    """Main function"""
    try:
        # Change to the script directory
        script_dir = Path(__file__).parent
        os.chdir(script_dir)
        
        # Run preflight checks
        if run_preflight_checks():
            # Start the web application
            start_webapp()
        else:
            logger.error("Preflight checks failed. Exiting.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Startup error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
