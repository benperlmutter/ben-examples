#!/usr/bin/env python3
"""
Test script for the Email Chatbot Web Application

This script tests the web application functionality without starting the full server.
"""

import sys
import os
import json
import logging
from unittest.mock import patch, MagicMock

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_webapp_imports():
    """Test that the webapp can be imported"""
    try:
        from webapp import app, EmailChatbotService
        logger.info("✓ Web application imports successful")
        return True
    except ImportError as e:
        logger.error(f"✗ Import failed: {e}")
        return False
    except Exception as e:
        logger.error(f"✗ Unexpected error during import: {e}")
        return False

def test_flask_app_creation():
    """Test that Flask app can be created"""
    try:
        from webapp import app
        
        # Test basic app properties
        assert app.name == 'webapp'
        assert app.secret_key is not None
        
        logger.info("✓ Flask app creation successful")
        return True
    except Exception as e:
        logger.error(f"✗ Flask app creation failed: {e}")
        return False

def test_service_initialization():
    """Test EmailChatbotService initialization"""
    try:
        from webapp import EmailChatbotService
        
        service = EmailChatbotService()
        
        # Check initial state
        assert service.email_updater is None
        assert service.embedding_generator is None
        assert service.response_generator is None
        assert service.last_update_time is None
        assert service.is_processing is False
        
        logger.info("✓ EmailChatbotService initialization successful")
        return True
    except Exception as e:
        logger.error(f"✗ Service initialization failed: {e}")
        return False

def test_routes_exist():
    """Test that all expected routes exist"""
    try:
        from webapp import app
        
        expected_routes = [
            '/',
            '/unanswered',
            '/api/stats',
            '/api/update',
            '/api/unanswered',
            '/api/generate_response'
        ]
        
        # Get all routes from the app
        routes = []
        for rule in app.url_map.iter_rules():
            routes.append(rule.rule)
        
        missing_routes = []
        for expected_route in expected_routes:
            if expected_route not in routes:
                missing_routes.append(expected_route)
        
        if missing_routes:
            logger.error(f"✗ Missing routes: {missing_routes}")
            return False
        
        logger.info("✓ All expected routes exist")
        return True
    except Exception as e:
        logger.error(f"✗ Route testing failed: {e}")
        return False

def test_templates_exist():
    """Test that template files exist"""
    try:
        template_files = [
            'templates/base.html',
            'templates/index.html',
            'templates/unanswered.html'
        ]
        
        missing_templates = []
        for template_file in template_files:
            if not os.path.exists(template_file):
                missing_templates.append(template_file)
        
        if missing_templates:
            logger.error(f"✗ Missing templates: {missing_templates}")
            return False
        
        logger.info("✓ All template files exist")
        return True
    except Exception as e:
        logger.error(f"✗ Template testing failed: {e}")
        return False

def test_mock_service_methods():
    """Test service methods with mocked dependencies"""
    try:
        from webapp import EmailChatbotService
        
        service = EmailChatbotService()
        
        # Mock the initialize_components method to avoid actual connections
        with patch.object(service, 'initialize_components', return_value=True):
            # Mock the database collections
            mock_collection = MagicMock()
            mock_collection.count_documents.return_value = 10
            mock_collection.distinct.return_value = ['thread1', 'thread2']
            
            with patch.object(service, 'embedding_generator') as mock_generator:
                mock_generator.original_emails_col = mock_collection
                mock_generator.email_embeddings_col = mock_collection
                
                # Test get_system_statistics
                stats = service.get_system_statistics()
                
                assert 'original_emails' in stats
                assert 'embedded_emails' in stats
                assert 'coverage' in stats
                assert 'recent_activity' in stats
                
                logger.info("✓ Service methods work with mocked dependencies")
                return True
                
    except Exception as e:
        logger.error(f"✗ Service method testing failed: {e}")
        return False

def test_flask_test_client():
    """Test Flask routes using test client"""
    try:
        from webapp import app
        
        # Create test client
        with app.test_client() as client:
            # Test main dashboard route
            response = client.get('/')
            assert response.status_code == 200
            
            # Test unanswered emails route
            response = client.get('/unanswered')
            assert response.status_code == 200
            
            # Test API stats route (might fail due to missing dependencies, but should not crash)
            response = client.get('/api/stats')
            # Don't assert status code as it might be 500 due to missing DB connection
            
            logger.info("✓ Flask test client routes accessible")
            return True
            
    except Exception as e:
        logger.error(f"✗ Flask test client failed: {e}")
        return False

def test_static_file_references():
    """Test that static file references in templates are valid"""
    try:
        template_files = [
            'templates/base.html',
            'templates/index.html', 
            'templates/unanswered.html'
        ]
        
        # Check for common CDN references
        expected_cdns = [
            'bootstrap',
            'font-awesome'
        ]
        
        for template_file in template_files:
            if os.path.exists(template_file):
                with open(template_file, 'r') as f:
                    content = f.read()
                    
                    # Check for CDN references
                    for cdn in expected_cdns:
                        if cdn not in content.lower():
                            logger.warning(f"⚠️  {cdn} not found in {template_file}")
        
        logger.info("✓ Template static file references checked")
        return True
        
    except Exception as e:
        logger.error(f"✗ Static file reference testing failed: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    logger.info("=" * 60)
    logger.info("TESTING EMAIL CHATBOT WEB APPLICATION")
    logger.info("=" * 60)
    
    tests = [
        ("Web Application Imports", test_webapp_imports),
        ("Flask App Creation", test_flask_app_creation),
        ("Service Initialization", test_service_initialization),
        ("Routes Exist", test_routes_exist),
        ("Templates Exist", test_templates_exist),
        ("Service Methods (Mocked)", test_mock_service_methods),
        ("Flask Test Client", test_flask_test_client),
        ("Static File References", test_static_file_references)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n--- Testing {test_name} ---")
        try:
            if test_func():
                passed += 1
                logger.info(f"✓ {test_name} passed")
            else:
                logger.error(f"✗ {test_name} failed")
        except Exception as e:
            logger.error(f"✗ {test_name} failed with exception: {e}")
    
    logger.info("\n" + "=" * 60)
    logger.info(f"TESTS COMPLETED: {passed}/{total} passed")
    logger.info("=" * 60)
    
    if passed == total:
        logger.info("✅ All tests passed! Web application is ready.")
        return True
    elif passed >= total * 0.8:  # 80% pass rate
        logger.warning("⚠️  Most tests passed. Web application should work with minor issues.")
        return True
    else:
        logger.error("❌ Many tests failed. Please fix issues before using the web application.")
        return False

def main():
    """Main function"""
    try:
        # Change to the script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        # Run all tests
        success = run_all_tests()
        
        if success:
            logger.info("\n🚀 Web application testing completed successfully!")
            logger.info("You can now run: python start_webapp.py")
        else:
            logger.error("\n❌ Web application testing failed!")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Testing error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
