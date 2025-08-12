#!/usr/bin/env python3
"""
Enhanced JustDial Research Runner
Combines all anti-detection measures for maximum success
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def print_banner():
    """Print startup banner"""
    print("=" * 70)
    print("🎭 ENHANCED JUSTDIAL WHATSAPP RESEARCH")
    print("   Maximum Anti-Detection + Human-Like Clicking")
    print("=" * 70)

def check_prerequisites():
    """Check that all required files exist"""
    required_files = [
        "enhanced_whatsapp_clicking.py",
        "justdial_anti_detection.py", 
        "justdial_whatsapp_connector_vision_fixed.py",
        "ai_csv_analyzer.py"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
    
    if missing_files:
        print("❌ Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        return False
    
    print("✅ All required files found")
    return True

def run_test_suite():
    """Run the test suite to verify setup"""
    print("\n🧪 Running setup verification tests...")
    
    try:
        result = subprocess.run([sys.executable, "test_enhanced_setup.py"], 
                              capture_output=True, text=True, timeout=60)
        
        # Print the output
        print(result.stdout)
        if result.stderr:
            print("Warnings/Errors:")
            print(result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("⚠️ Test suite timed out")
        return False
    except Exception as e:
        print(f"❌ Could not run test suite: {e}")
        return False

def start_anti_detection():
    """Start anti-detection Chrome session"""
    print("\n🛡️ Starting anti-detection Chrome session...")
    
    try:
        # Run the anti-detection script
        print("Starting enhanced Chrome session...")
        subprocess.run([sys.executable, "justdial_anti_detection.py"], check=False)
        
        # Wait for Chrome to be ready
        print("\n⏳ Waiting for Chrome to initialize...")
        time.sleep(3)
        
        return True
    except Exception as e:
        print(f"❌ Failed to start anti-detection: {e}")
        return False

def run_research():
    """Run the main research application"""
    print("\n🔬 Starting enhanced research application...")
    
    try:
        # Run the main CSV analyzer with enhanced features
        subprocess.run([sys.executable, "ai_csv_analyzer.py"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Research application failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Error running research: {e}")
        return False

def main():
    """Main execution flow"""
    print_banner()
    
    # Step 1: Check prerequisites
    print("\n📋 Step 1: Checking prerequisites...")
    if not check_prerequisites():
        print("\n❌ Prerequisites check failed!")
        print("Please ensure all required files are present.")
        input("Press Enter to exit...")
        return
    
    # Step 2: Run tests (optional)
    print("\n📋 Step 2: Setup verification...")
    user_choice = input("Run setup verification tests? (y/n, default=y): ").strip().lower()
    
    if user_choice != 'n':
        if not run_test_suite():
            print("\n⚠️ Some tests failed, but continuing anyway...")
            proceed = input("Continue with research? (y/n): ").strip().lower()
            if proceed != 'y':
                print("Exiting...")
                return
    
    # Step 3: Start anti-detection
    print("\n📋 Step 3: Anti-detection setup...")
    print("This will start Chrome with enhanced anti-detection measures.")
    print("You'll need to:")
    print("1. Login to JustDial (preferably with a different mobile number)")
    print("2. Complete any verification steps")
    print("3. Return here to continue")
    
    proceed = input("\nStart anti-detection Chrome session? (y/n): ").strip().lower()
    if proceed == 'y':
        if not start_anti_detection():
            print("❌ Anti-detection setup failed!")
            fallback = input("Continue without anti-detection? (y/n): ").strip().lower()
            if fallback != 'y':
                return
    
    # Step 4: Run research
    print("\n📋 Step 4: Starting research...")
    print("This will launch the main research application with:")
    print("✅ Human-like mouse movements")
    print("✅ Natural clicking patterns") 
    print("✅ Reading and hesitation simulation")
    print("✅ Advanced anti-detection measures")
    print("✅ WhatsApp vision extraction")
    print("✅ Fallback phone extraction")
    
    proceed = input("\nStart enhanced research? (y/n): ").strip().lower()
    if proceed == 'y':
        if run_research():
            print("\n🎉 Research completed successfully!")
        else:
            print("\n❌ Research encountered issues")
    
    print("\n" + "=" * 70)
    print("🎭 Enhanced JustDial Research Session Complete")
    print("=" * 70)
    input("Press Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Session interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        input("Press Enter to exit...")
