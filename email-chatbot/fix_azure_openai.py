#!/usr/bin/env python3
"""
Azure OpenAI Troubleshooting and Fix Script

This script helps diagnose and fix Azure OpenAI connection issues,
particularly the "unexpected keyword argument 'proxies'" error.
"""

import sys
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_openai_version():
    """Check the installed OpenAI library version"""
    try:
        import openai
        version = openai.__version__
        logger.info(f"OpenAI library version: {version}")
        
        # Check if version is compatible
        major, minor = map(int, version.split('.')[:2])
        if major >= 1 and minor >= 12:
            logger.info("✓ OpenAI library version is compatible")
            return True
        else:
            logger.warning(f"⚠️  OpenAI library version {version} may be outdated")
            logger.info("Recommended: openai>=1.12.0")
            return False
            
    except ImportError:
        logger.error("✗ OpenAI library not installed")
        return False
    except Exception as e:
        logger.error(f"✗ Error checking OpenAI version: {e}")
        return False

def test_azure_openai_import():
    """Test importing AzureOpenAI"""
    try:
        from openai import AzureOpenAI
        logger.info("✓ AzureOpenAI import successful")
        return True
    except ImportError as e:
        logger.error(f"✗ AzureOpenAI import failed: {e}")
        return False

def load_azure_credentials():
    """Load and validate Azure credentials"""
    try:
        with open('../../../azure-gpt-creds/azure-gpt-creds.json', 'r') as f:
            creds = json.load(f)
        
        required_keys = ["azure-api-key", "azure-api-version", "azure-endpoint", "azure-deployment-name"]
        missing_keys = [key for key in required_keys if key not in creds]
        
        if missing_keys:
            logger.error(f"✗ Missing credential keys: {missing_keys}")
            return None
        
        logger.info("✓ Azure credentials loaded successfully")
        logger.info(f"  - Endpoint: {creds['azure-endpoint']}")
        logger.info(f"  - API Version: {creds['azure-api-version']}")
        logger.info(f"  - Deployment: {creds['azure-deployment-name']}")
        
        return creds
        
    except FileNotFoundError:
        logger.error("✗ Azure credentials file not found: ../../../azure-gpt-creds/azure-gpt-creds.json")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"✗ Invalid JSON in credentials file: {e}")
        return None
    except Exception as e:
        logger.error(f"✗ Error loading credentials: {e}")
        return None

def test_azure_client_creation(creds):
    """Test creating Azure OpenAI client"""
    try:
        from openai import AzureOpenAI
        
        # Method 1: Minimal parameters (recommended)
        logger.info("Testing Azure OpenAI client creation (minimal parameters)...")
        client = AzureOpenAI(
            api_version=creds["azure-api-version"],
            azure_endpoint=creds["azure-endpoint"],
            api_key=creds["azure-api-key"]
        )
        logger.info("✓ Azure OpenAI client created successfully")
        return client, creds["azure-deployment-name"]
        
    except Exception as e:
        logger.error(f"✗ Azure OpenAI client creation failed: {e}")
        
        # Try alternative method
        try:
            logger.info("Trying alternative client creation method...")
            client = AzureOpenAI(
                api_key=creds["azure-api-key"],
                api_version=creds["azure-api-version"],
                azure_endpoint=creds["azure-endpoint"]
            )
            logger.info("✓ Azure OpenAI client created with alternative method")
            return client, creds["azure-deployment-name"]
            
        except Exception as e2:
            logger.error(f"✗ Alternative method also failed: {e2}")
            return None, None

def test_completion(client, deployment_name):
    """Test making a completion request"""
    try:
        logger.info("Testing completion request...")
        
        completion = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {
                    "role": "user",
                    "content": "Say 'Hello from Azure OpenAI' in exactly those words."
                }
            ],
            max_tokens=10
        )
        
        response = completion.choices[0].message.content
        logger.info(f"✓ Completion successful: {response}")
        return True
        
    except Exception as e:
        logger.error(f"✗ Completion failed: {e}")
        logger.error(f"Error details: {str(e)}")
        return False

def provide_fix_recommendations():
    """Provide recommendations to fix common issues"""
    logger.info("\n" + "=" * 60)
    logger.info("FIX RECOMMENDATIONS")
    logger.info("=" * 60)
    
    logger.info("1. Update OpenAI library:")
    logger.info("   pip install --upgrade openai>=1.12.0")
    logger.info("")
    
    logger.info("2. If you get 'proxies' error, ensure you're using the latest code:")
    logger.info("   - Check that aug_generate_responses.py uses the updated Azure client initialization")
    logger.info("   - Remove any 'azure_deployment' parameter from AzureOpenAI() constructor")
    logger.info("   - Use deployment name in the model parameter of completions.create()")
    logger.info("")
    
    logger.info("3. Verify credentials file format:")
    logger.info("   {")
    logger.info('     "azure-api-key": "your-key",')
    logger.info('     "azure-api-version": "2024-02-01",')
    logger.info('     "azure-endpoint": "https://your-resource.openai.azure.com/",')
    logger.info('     "azure-deployment-name": "your-deployment"')
    logger.info("   }")
    logger.info("")
    
    logger.info("4. Check network connectivity:")
    logger.info("   - Ensure you can reach the Azure endpoint")
    logger.info("   - Check firewall and proxy settings")
    logger.info("")
    
    logger.info("5. Verify Azure OpenAI resource:")
    logger.info("   - Ensure the deployment exists and is active")
    logger.info("   - Check API key permissions")

def main():
    """Main troubleshooting function"""
    logger.info("=" * 60)
    logger.info("AZURE OPENAI TROUBLESHOOTING")
    logger.info("=" * 60)
    
    # Step 1: Check OpenAI version
    logger.info("\n1. Checking OpenAI library version...")
    version_ok = check_openai_version()
    
    # Step 2: Test import
    logger.info("\n2. Testing AzureOpenAI import...")
    import_ok = test_azure_openai_import()
    
    if not import_ok:
        logger.error("Cannot proceed without successful import")
        provide_fix_recommendations()
        return False
    
    # Step 3: Load credentials
    logger.info("\n3. Loading Azure credentials...")
    creds = load_azure_credentials()
    
    if not creds:
        logger.error("Cannot proceed without valid credentials")
        provide_fix_recommendations()
        return False
    
    # Step 4: Test client creation
    logger.info("\n4. Testing Azure OpenAI client creation...")
    client, deployment_name = test_azure_client_creation(creds)
    
    if not client:
        logger.error("Cannot proceed without successful client creation")
        provide_fix_recommendations()
        return False
    
    # Step 5: Test completion
    logger.info("\n5. Testing completion request...")
    completion_ok = test_completion(client, deployment_name)
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TROUBLESHOOTING SUMMARY")
    logger.info("=" * 60)
    
    tests = [
        ("OpenAI Version", version_ok),
        ("AzureOpenAI Import", import_ok),
        ("Credentials", creds is not None),
        ("Client Creation", client is not None),
        ("Completion Test", completion_ok)
    ]
    
    passed = sum(1 for _, result in tests if result)
    total = len(tests)
    
    for test_name, result in tests:
        status = "✓" if result else "✗"
        logger.info(f"{status} {test_name}")
    
    logger.info(f"\nTests passed: {passed}/{total}")
    
    if passed == total:
        logger.info("🎉 All tests passed! Azure OpenAI is working correctly.")
        logger.info("You can now run the web application without issues.")
        return True
    else:
        logger.error("❌ Some tests failed. Please follow the fix recommendations.")
        provide_fix_recommendations()
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Troubleshooting script error: {e}")
        sys.exit(1)

