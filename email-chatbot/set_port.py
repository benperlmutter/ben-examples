#!/usr/bin/env python3
"""
Simple script to change the web application port

Usage:
    python set_port.py 3000    # Set port to 3000
    python set_port.py         # Show current port
"""

import sys
import os
import re

def get_current_port():
    """Get the current port from config.py"""
    try:
        with open('config.py', 'r') as f:
            content = f.read()
        
        # Look for PORT = int(os.environ.get('PORT', XXXX))
        match = re.search(r"PORT = int\(os\.environ\.get\('PORT', (\d+)\)\)", content)
        if match:
            return int(match.group(1))
        
        return None
    except Exception as e:
        print(f"Error reading config.py: {e}")
        return None

def set_port(new_port):
    """Set a new port in config.py"""
    try:
        with open('config.py', 'r') as f:
            content = f.read()
        
        # Replace the port number
        pattern = r"(PORT = int\(os\.environ\.get\('PORT', )\d+(\)\))"
        replacement = f"\\g<1>{new_port}\\g<2>"
        new_content = re.sub(pattern, replacement, content)
        
        if new_content != content:
            with open('config.py', 'w') as f:
                f.write(new_content)
            print(f"✅ Port updated to {new_port}")
            return True
        else:
            print("❌ Could not find port configuration to update")
            return False
            
    except Exception as e:
        print(f"❌ Error updating config.py: {e}")
        return False

def show_usage():
    """Show usage information"""
    print("Port Configuration Tool for Email Chatbot Web App")
    print("=" * 50)
    print("Usage:")
    print("  python set_port.py           # Show current port")
    print("  python set_port.py 3000      # Set port to 3000")
    print("  python set_port.py 5000      # Set port to 5000")
    print("  python set_port.py 8080      # Set port to 8080")
    print("")
    print("Common ports:")
    print("  3000 - React/Node.js development")
    print("  5000 - Flask default")
    print("  8000 - Django development")
    print("  8080 - Common alternative (current default)")
    print("  9000 - High port alternative")
    print("")
    print("Environment variable override:")
    print("  export PORT=3000")
    print("  python start_webapp.py")

def main():
    """Main function"""
    if len(sys.argv) == 1:
        # Show current port
        current_port = get_current_port()
        if current_port:
            print(f"Current port: {current_port}")
            print(f"Web app will run on: http://localhost:{current_port}")
            print("")
            print("To change the port, run:")
            print(f"  python set_port.py <new_port>")
        else:
            print("❌ Could not determine current port")
        
    elif len(sys.argv) == 2:
        if sys.argv[1] in ['-h', '--help', 'help']:
            show_usage()
            return
            
        try:
            new_port = int(sys.argv[1])
            
            # Validate port range
            if new_port < 1 or new_port > 65535:
                print("❌ Port must be between 1 and 65535")
                return
            
            # Check if port is commonly used by system services
            if new_port < 1024:
                print(f"⚠️  Warning: Port {new_port} is in the system/privileged range (1-1023)")
                print("   You may need administrator privileges to use this port")
                response = input("Continue? (y/N): ")
                if response.lower() != 'y':
                    print("Port change cancelled")
                    return
            
            current_port = get_current_port()
            if current_port == new_port:
                print(f"Port is already set to {new_port}")
                return
            
            if set_port(new_port):
                print(f"Port changed from {current_port} to {new_port}")
                print(f"Web app will now run on: http://localhost:{new_port}")
                print("")
                print("To start the web app with the new port:")
                print("  python start_webapp.py")
            
        except ValueError:
            print("❌ Invalid port number. Please provide a valid integer.")
            print("Example: python set_port.py 3000")
    
    else:
        print("❌ Too many arguments")
        show_usage()

if __name__ == "__main__":
    main()

