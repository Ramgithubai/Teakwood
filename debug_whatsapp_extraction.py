#!/usr/bin/env python3
"""
Debug WhatsApp Vision Extraction
Run this script to test your vision extraction with the specific screenshot
"""

import os
import sys
import logging

# Add the modules directory to path
sys.path.append('C:/01_Projects/Teakwood_Business/Web_Scraping/Dashboard/modules')

from justdial_researcher import JustDialStreamlitResearcher

def debug_whatsapp_extraction():
    """Debug the WhatsApp extraction issue"""
    print("=" * 80)
    print("🔧 DEBUGGING WHATSAPP VISION EXTRACTION")
    print("=" * 80)
    
    # Setup logging to see detailed output
    logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
    
    try:
        # Initialize researcher
        print("📍 Step 1: Initializing JustDial researcher...")
        researcher = JustDialStreamlitResearcher()
        
        # Check API key
        print("📍 Step 2: Checking GROQ API key...")
        if researcher.groq_api_key:
            print(f"✅ API key found: {researcher.groq_api_key[:10]}...")
        else:
            print("❌ GROQ_API_KEY not found!")
            print("💡 Make sure you have GROQ_API_KEY in your .env file")
            return False
        
        # Test with your specific screenshot
        screenshot_path = "whatsapp_contact_20250811_212042.png"
        
        print(f"📍 Step 3: Testing with screenshot: {screenshot_path}")
        
        # Check if screenshot exists
        if not os.path.exists(screenshot_path):
            print(f"❌ Screenshot not found: {screenshot_path}")
            print("💡 Make sure the screenshot is in the current directory")
            
            # List current directory files
            print("📁 Files in current directory:")
            for file in os.listdir('.'):
                if file.endswith('.png'):
                    print(f"   📸 {file}")
            return False
        
        print(f"✅ Screenshot found: {os.path.getsize(screenshot_path)} bytes")
        
        # Test vision extraction
        print("📍 Step 4: Testing vision extraction...")
        result = researcher.test_vision_extraction_with_screenshot(screenshot_path)
        
        if result:
            print("=" * 80)
            print(f"🎉 SUCCESS! Extracted phone number: {result}")
            print("=" * 80)
            return result
        else:
            print("=" * 80)
            print("❌ FAILED: Could not extract phone number")
            print("💡 Check the logs above for specific error details")
            print("=" * 80)
            return None
            
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        return None

def check_environment():
    """Check environment setup"""
    print("🔍 ENVIRONMENT CHECK:")
    print("-" * 40)
    
    # Check .env file
    env_files = ['.env', '../.env', '../../.env']
    env_found = False
    
    for env_file in env_files:
        if os.path.exists(env_file):
            print(f"✅ Found .env file: {env_file}")
            env_found = True
            
            # Check if GROQ_API_KEY is in the file
            try:
                with open(env_file, 'r') as f:
                    content = f.read()
                    if 'GROQ_API_KEY' in content:
                        print("✅ GROQ_API_KEY found in .env file")
                    else:
                        print("❌ GROQ_API_KEY not found in .env file")
            except:
                print("⚠️ Could not read .env file")
            break
    
    if not env_found:
        print("❌ No .env file found")
        print("💡 Create a .env file with: GROQ_API_KEY=your_api_key_here")
    
    # Check environment variable
    groq_key = os.getenv('GROQ_API_KEY')
    if groq_key:
        print(f"✅ GROQ_API_KEY in environment: {groq_key[:10]}...")
    else:
        print("❌ GROQ_API_KEY not in environment")
    
    print("-" * 40)

if __name__ == "__main__":
    # Change to the Dashboard directory
    os.chdir('C:/01_Projects/Teakwood_Business/Web_Scraping/Dashboard')
    
    check_environment()
    result = debug_whatsapp_extraction()
    
    if result:
        print(f"\n🎯 Expected result for your screenshot: {result}")
        print("   (This should be: 8056175751)")
    else:
        print("\n❌ Extraction failed. Please check the error messages above.")
