#!/usr/bin/env python3
"""
Test script for the email response generation functionality
"""
import sys
import os
import json
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all required packages can be imported"""
    try:
        import pymongo
        import json
        from sentence_transformers import SentenceTransformer
        from openai import AzureOpenAI
        print("✓ All required packages imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_credentials():
    """Test that credential files exist and are readable"""
    try:
        # Test Atlas credentials
        with open('../../../atlas-creds/atlas-creds.json', 'r') as f:
            atlas_creds = json.load(f)
        
        if "mdb-connection-string" not in atlas_creds:
            print("✗ Atlas credentials missing mdb-connection-string")
            return False
        
        # Test Azure credentials
        with open('../../../azure-gpt-creds/azure-gpt-creds.json', 'r') as f:
            azure_creds = json.load(f)
        
        required_azure_keys = ["azure-api-key", "azure-api-version", "azure-endpoint", "azure-deployment-name"]
        for key in required_azure_keys:
            if key not in azure_creds:
                print(f"✗ Azure credentials missing {key}")
                return False
        
        print("✓ All credential files found and valid")
        return True
        
    except FileNotFoundError as e:
        print(f"✗ Credential file not found: {e}")
        return False
    except json.JSONDecodeError as e:
        print(f"✗ Invalid JSON in credential file: {e}")
        return False
    except Exception as e:
        print(f"✗ Error reading credentials: {e}")
        return False

def test_database_connection():
    """Test MongoDB connection and collection access"""
    try:
        import pymongo
        
        with open('../../../atlas-creds/atlas-creds.json', 'r') as f:
            creds_data = json.load(f)
        
        mdb_string = creds_data["mdb-connection-string"]
        client = pymongo.MongoClient(mdb_string)
        
        # Test connection
        client.admin.command('ping')
        
        # Test database and collections
        email_chatbot_db = client.email_chatbot
        original_emails_col = email_chatbot_db.original_emails
        email_embeddings_col = email_chatbot_db.email_embeddings
        
        # Get collection stats
        original_count = original_emails_col.count_documents({})
        embeddings_count = email_embeddings_col.count_documents({})
        
        print(f"✓ MongoDB connection successful")
        print(f"  - Original emails: {original_count} documents")
        print(f"  - Email embeddings: {embeddings_count} documents")
        
        if embeddings_count == 0:
            print("⚠️  Warning: No embeddings found. Run aug_generate_embeddings.py first")
        
        return True
        
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False

def test_sentence_transformer():
    """Test SentenceTransformer model loading and encoding"""
    try:
        from sentence_transformers import SentenceTransformer
        
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        # Test encoding
        test_text = "We are interested in hosting a wedding at Big Sur River Inn"
        embedding = model.encode(test_text)
        
        print(f"✓ SentenceTransformer working")
        print(f"  - Model loaded successfully")
        print(f"  - Embedding shape: {embedding.shape}")
        print(f"  - Expected dimension: 384")
        
        if embedding.shape[0] != 384:
            print(f"⚠️  Warning: Unexpected embedding dimension")
        
        return True
        
    except Exception as e:
        print(f"✗ SentenceTransformer test failed: {e}")
        return False

def test_azure_openai():
    """Test Azure OpenAI connection and basic completion"""
    try:
        from openai import AzureOpenAI
        
        with open('../../../azure-gpt-creds/azure-gpt-creds.json', 'r') as f:
            azure_creds = json.load(f)
        
        client = AzureOpenAI(
            api_version=azure_creds["azure-api-version"],
            azure_endpoint=azure_creds["azure-endpoint"],
            api_key=azure_creds["azure-api-key"]
        )
        
        # Test with a simple completion
        completion = client.chat.completions.create(
            model=azure_creds["azure-deployment-name"],  # Use deployment name
            messages=[
                {
                    "role": "user",
                    "content": "Say 'Hello, this is a test' in exactly those words."
                }
            ],
            max_tokens=20
        )
        
        response = completion.choices[0].message.content
        print(f"✓ Azure OpenAI connection successful")
        print(f"  - Test response: {response}")
        
        return True
        
    except Exception as e:
        print(f"✗ Azure OpenAI test failed: {e}")
        return False

def test_response_generator_import():
    """Test that the response generator can be imported"""
    try:
        # Add the current directory to path
        sys.path.insert(0, '/mnt/persist/workspace/email-chatbot')
        
        from aug_generate_responses import EmailResponseGenerator
        
        print("✓ EmailResponseGenerator imported successfully")
        return True
        
    except Exception as e:
        print(f"✗ EmailResponseGenerator import failed: {e}")
        return False

def test_response_generator_initialization():
    """Test that the response generator can be initialized"""
    try:
        sys.path.insert(0, '/mnt/persist/workspace/email-chatbot')
        from aug_generate_responses import EmailResponseGenerator
        
        generator = EmailResponseGenerator()
        print("✓ EmailResponseGenerator initialized successfully")
        
        # Test statistics method
        generator.get_statistics()
        print("✓ Statistics method working")
        
        return True
        
    except Exception as e:
        print(f"✗ EmailResponseGenerator initialization failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Email Response Generation System...")
    print("=" * 60)
    
    tests = [
        ("Package Imports", test_imports),
        ("Credential Files", test_credentials),
        ("Database Connection", test_database_connection),
        ("SentenceTransformer", test_sentence_transformer),
        ("Azure OpenAI", test_azure_openai),
        ("Response Generator Import", test_response_generator_import),
        ("Response Generator Init", test_response_generator_initialization),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- Testing {test_name} ---")
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
        print()
    
    print("=" * 60)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed! The response generation system is ready to use.")
        print("\nNext steps:")
        print("1. Run: python aug_generate_responses.py")
        print("2. Check the generated responses")
        print("3. Adjust parameters as needed")
    else:
        print("❌ Some tests failed. Please fix the issues before using the system.")
        
        if passed >= 5:  # Most core tests passed
            print("\n💡 Core functionality appears to work. You may still be able to run the system.")

if __name__ == "__main__":
    main()

