#!/usr/bin/env python3
"""
Chrome Debugging Setup Script for JustDial Research
Run this script to start Chrome with debugging enabled for JustDial research.
"""

import os
import sys
import time
import subprocess

def start_chrome_with_debugging():
    """Start Chrome with remote debugging enabled"""
    print("\n" + "=" * 80)
    print("🚗 CHROME DEBUGGING SETUP FOR JUSTDIAL RESEARCH")
    print("=" * 80)
    
    # Kill any existing Chrome processes
    print("1. Closing existing Chrome windows...")
    try:
        if os.name == 'nt':  # Windows
            os.system("taskkill /f /im chrome.exe 2>nul")
        else:  # Linux/Mac
            os.system("pkill chrome")
        time.sleep(2)
        print("   ✅ Existing Chrome processes closed")
    except Exception as e:
        print(f"   ⚠️ Could not close Chrome: {e}")

    # Find Chrome executable
    print("2. Finding Chrome installation...")
    chrome_path = None
    debugging_port = "9222"

    if os.name == 'nt':  # Windows
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
        ]
        for path in possible_paths:
            if os.path.exists(path):
                chrome_path = path
                print(f"   ✅ Found Chrome at: {path}")
                break
    else:  # Linux/Mac
        chrome_path = "google-chrome"
        print(f"   ✅ Using Chrome command: {chrome_path}")

    if not chrome_path:
        print("   ❌ Chrome not found!")
        print("   Please install Google Chrome and try again.")
        return False

    # Create user data directory
    print("3. Setting up Chrome profile...")
    user_data_dir = os.path.join(os.path.dirname(__file__), "chrome_debug_profile")
    try:
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)
        print(f"   ✅ Profile directory: {user_data_dir}")
    except Exception as e:
        print(f"   ⚠️ Could not create profile directory: {e}")

    # Start Chrome with debugging
    print("4. Starting Chrome with debugging enabled...")
    cmd = f'"{chrome_path}" --remote-debugging-port={debugging_port} --user-data-dir="{user_data_dir}"'
    
    try:
        if os.name == 'nt':
            subprocess.Popen(cmd, shell=True)
        else:
            subprocess.Popen(cmd, shell=True)
        
        print("   ✅ Chrome started with debugging enabled")
        time.sleep(3)
        
    except Exception as e:
        print(f"   ❌ Failed to start Chrome: {e}")
        return False

    print("\n" + "=" * 80)
    print("🎉 CHROME DEBUGGING SETUP COMPLETE!")
    print("=" * 80)
    print("\n📋 NEXT STEPS:")
    print("1. Chrome should have opened automatically")
    print("2. Go to: https://www.justdial.com")
    print("3. Try a manual search to ensure the site works")
    print("4. Keep this Chrome window open")
    print("5. Now you can use JustDial research in the web interface")
    print("\n⚠️  IMPORTANT:")
    print("- Do NOT close this Chrome window during JustDial research")
    print("- The research will connect to this Chrome instance")
    print("- This avoids automation detection issues")
    
    return True

def test_chrome_connection():
    """Test if Chrome debugging connection is working"""
    print("\n🧪 Testing Chrome debugging connection...")
    
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        
        driver = webdriver.Chrome(options=chrome_options)
        current_url = driver.current_url
        title = driver.title
        driver.quit()
        
        print("✅ Chrome debugging connection successful!")
        print(f"   Current URL: {current_url}")
        print(f"   Page title: {title}")
        return True
        
    except Exception as e:
        print(f"❌ Chrome debugging connection failed: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure Chrome was started with the debugging command")
        print("2. Check if Chrome is still running")
        print("3. Try running this script again")
        return False

if __name__ == "__main__":
    print("🚗 JustDial Research - Chrome Setup Tool")
    
    # Check if selenium is installed
    try:
        from selenium import webdriver
        print("✅ Selenium is installed")
    except ImportError:
        print("❌ Selenium not installed")
        print("Please run: pip install selenium")
        sys.exit(1)
    
    # Start Chrome
    if start_chrome_with_debugging():
        # Test connection
        print("\n" + "="*50)
        test_chrome_connection()
        
        print("\n" + "="*80)
        print("🎯 READY FOR JUSTDIAL RESEARCH!")
        print("You can now use the JustDial research feature in the web interface.")
        print("="*80)
    else:
        print("\n❌ Setup failed. Please check the errors above and try again.")
