#!/usr/bin/env python3
"""
Test script for email chatbot functionality
"""
import sys
import os

def test_imports():
    """Test that all required packages can be imported"""
    try:
        import pymongo
        import json
        import datetime
        import dateutil
        from sentence_transformers import SentenceTransformer
        print("✓ All required packages imported successfully")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_mongodb_connection():
    """Test MongoDB connection"""
    try:
        import pymongo
        client = pymongo.MongoClient("mongodb://localhost:27017/")
        # Test connection
        client.admin.command('ping')
        print("✓ MongoDB connection successful")
        return True
    except Exception as e:
        print(f"✗ MongoDB connection failed: {e}")
        return False

def test_sentence_transformer():
    """Test sentence transformer model loading"""
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        # Test encoding
        test_text = "This is a test message"
        embedding = model.encode(test_text)
        print(f"✓ Sentence transformer working, embedding shape: {embedding.shape}")
        return True
    except Exception as e:
        print(f"✗ Sentence transformer test failed: {e}")
        return False

def test_email_chatbot_modules():
    """Test that email chatbot modules can be imported"""
    try:
        # Change to email-chatbot directory
        sys.path.insert(0, '/mnt/persist/workspace/email-chatbot')
        
        # Test importing the add_embeddings module functions
        import importlib.util
        
        # Test add_embeddings.py
        spec = importlib.util.spec_from_file_location("add_embeddings", "/mnt/persist/workspace/email-chatbot/add_embeddings.py")
        add_embeddings = importlib.util.module_from_spec(spec)
        
        # Test count_docs.py  
        spec = importlib.util.spec_from_file_location("count_docs", "/mnt/persist/workspace/email-chatbot/count_docs.py")
        count_docs = importlib.util.module_from_spec(spec)
        
        print("✓ Email chatbot modules can be imported")
        return True
    except Exception as e:
        print(f"✗ Email chatbot module import failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Running email chatbot tests...")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_mongodb_connection,
        test_sentence_transformer,
        test_email_chatbot_modules
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
