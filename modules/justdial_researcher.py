#!/usr/bin/env python3
"""
JustDial Researcher - Streamlit Integration Module
FIXED VERSION - Complete with missing WhatsApp methods
Modified for programmatic use with consignee names and cities
"""

import os
import re
import json
import base64
import time
import logging
import asyncio
import requests
import random
from datetime import datetime

# Import enhanced human-like clicking if available
try:
    from .enhanced_whatsapp_clicking import EnhancedWhatsAppClicker
    ENHANCED_CLICKING_AVAILABLE = True
    print("[INFO] ✅ Enhanced human-like clicking loaded successfully")
except ImportError as e:
    ENHANCED_CLICKING_AVAILABLE = False
    print(f"[INFO] ⚠️ Enhanced clicking not available: {e}")
    print("[INFO] Using basic human-like clicking instead")

import pandas as pd
import streamlit as st

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class JustDialStreamlitResearcher:
    def __init__(self, groq_api_key=None, use_existing_chrome=True, headless=False):
        """Initialize the JustDial researcher for Streamlit"""
        self.driver = None
        self.groq_api_key = groq_api_key or self.get_groq_api_key()
        self.use_existing_chrome = use_existing_chrome
        self.headless = headless
        self.setup_logging()
        self.results = []
        
        # FIXED: Add missing attributes for WhatsApp management
        self.existing_whatsapp_window = None
        self.whatsapp_tab_to_close = None
        
        # Log enhanced clicking availability
        if ENHANCED_CLICKING_AVAILABLE:
            self.logger.info("🎭 Enhanced human-like clicking enabled")
        else:
            self.logger.info("⚠️ Using basic human-like clicking")
        
    
    def detect_whatsapp_page_type(self):
        """Detect what type of WhatsApp page we're currently on"""
        try:
            self.logger.info("🔍 Detecting WhatsApp page type...")
            
            # Check for QR code (login page) - CRITICAL CHECK
            qr_indicators = [
                "[data-testid='qr-code']",
                "canvas[aria-label*='QR']",
                ".landing-window",
                "div[data-ref='qr']",
                "img[alt*='QR']"
            ]
            
            for selector in qr_indicators:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and any(elem.is_displayed() for elem in elements):
                        self.logger.info(f"🔍 Detected: Login page (QR code) via {selector}")
                        return "login_required"
                except:
                    continue
            
            # Check for QR code via text
            try:
                elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), 'QR code') or contains(text(), 'Scan') or contains(text(), 'Steps to log in')]")
                if elements:
                    self.logger.info("🔍 Detected: Login page (QR code) via text")
                    return "login_required"
            except:
                pass
            
            # Check for main chat interface (logged in)
            main_interface_indicators = [
                "[data-testid='chat-list']",
                "[data-testid='chatlist-search']", 
                ".two._aigs",  # Main WhatsApp interface
                "div[role='application']",  # WhatsApp app container
                "[aria-label*='Chat list']",
                "div[data-testid='side-panel']"
            ]
            
            for selector in main_interface_indicators:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and any(elem.is_displayed() for elem in elements):
                        # Check if we're in a specific contact chat
                        if self.is_in_contact_chat():
                            self.logger.info("🔍 Detected: Contact chat page")
                            return "contact_chat"
                        else:
                            self.logger.info("🔍 Detected: Main interface (logged in)")
                            return "logged_in_main"
                except:
                    continue
            
            # Check for direct contact chat indicators
            contact_chat_indicators = [
                "header[data-testid='conversation-header']",
                "div[data-testid='conversation-info-header']",
                "div[data-testid='chat-header']",
                "header div[title*='+91']",
                "header span[title*='+91']"
            ]
            
            for selector in contact_chat_indicators:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and any(elem.is_displayed() for elem in elements):
                        self.logger.info("🔍 Detected: Direct contact chat")
                        return "contact_chat"
                except:
                    continue
            
            self.logger.warning("❓ Could not determine page type")
            return "unknown"
            
        except Exception as e:
            self.logger.error(f"Error detecting page type: {e}")
            return "unknown"

    def is_in_contact_chat(self):
        """Check if we're currently in a specific contact chat"""
        contact_chat_selectors = [
            "header[data-testid='conversation-header']",
            "div[data-testid='conversation-info-header']",
            "div[data-testid='chat-header']",
            "header div[title*='+']",  # Phone number in header
            "div[data-testid='conversation-panel-wrapper']"
        ]
        
        for selector in contact_chat_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements and any(elem.is_displayed() for elem in elements):
                    return True
            except:
                continue
        return False

    def try_to_find_recent_contact(self):
        """Try to find and open a recent contact from the chat list - IMPROVED"""
        self.logger.info("🔍 Looking for recent contact in chat list...")
        
        try:
            # Wait a bit for chat list to load
            time.sleep(5)  # Increased wait time
            
            # Look for chat list items with multiple strategies
            chat_selectors = [
                "[data-testid*='chat-list-item']",
                "div[role='listitem']",
                "div[data-testid='cell-frame-container']",
                "div[tabindex='-1'][role='row']",
                "div[data-testid='list-item']",
                "div[data-testid='conversation-panel-wrapper'] div[role='row']",
                "div[aria-label*='chat']",
                "span[title*='+']",  # Look for phone numbers directly
                "div[data-testid='contact-wrapper']"
            ]
            
            for selector in chat_selectors:
                try:
                    chat_items = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if chat_items:
                        self.logger.info(f"📞 Found {len(chat_items)} chat items with selector: {selector}")
                        
                        # Try clicking the first few chat items to find one with contact info
                        for i, chat_item in enumerate(chat_items[:5]):  # Try first 5 items
                            try:
                                # Scroll into view first
                                self.driver.execute_script("arguments[0].scrollIntoView(true);", chat_item)
                                time.sleep(1)
                                
                                # Check if this item has contact info
                                item_text = chat_item.text.strip()
                                if '+' in item_text or any(char.isdigit() for char in item_text):
                                    self.logger.info(f"📞 Clicking chat item {i+1} with contact info: {item_text[:50]}...")
                                    
                                    # Click with human-like behavior
                                    chat_item.click()
                                    time.sleep(5)  # Wait longer for chat to load
                                    
                                    # Check if we're now in a contact chat
                                    if self.is_in_contact_chat():
                                        self.logger.info("✅ Successfully opened contact chat")
                                        return True
                                    else:
                                        self.logger.warning(f"⚠️ Chat item {i+1} didn't open contact chat, trying next...")
                                        continue
                                        
                            except Exception as item_error:
                                self.logger.debug(f"Error clicking chat item {i+1}: {item_error}")
                                continue
                        
                        # If we found items but none worked, break to avoid trying other selectors
                        break
                        
                except Exception as e:
                    self.logger.debug(f"Error with selector {selector}: {e}")
                    continue
            
            # Alternative strategy: Look for any contact directly
            self.logger.info("🔍 Trying alternative contact search...")
            return self.find_any_contact_alternative()
                    
        except Exception as e:
            self.logger.error(f"Error finding recent contact: {e}")
            return False
    
    def find_any_contact_alternative(self):
        """Alternative method to find any contact"""
        try:
            # Look for phone numbers or contact names anywhere
            phone_patterns = [
                "span[title*='+91']",
                "div[title*='+91']", 
                "span[title*='+44']",  # UK numbers
                "span[title*='+1']",   # US numbers
                "[title*='+']",        # Any international number
                "div[data-testid*='chat']",
                "div[data-testid*='contact']"
            ]
            
            for pattern in phone_patterns:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, pattern)
                    for element in elements:
                        if element.is_displayed():
                            title = element.get_attribute('title') or ''
                            if '+' in title and any(char.isdigit() for char in title):
                                self.logger.info(f"📞 Found contact element with title: {title}")
                                
                                # Click the parent element or the element itself
                                clickable_element = element
                                try:
                                    # Try to find clickable parent
                                    parent = element.find_element(By.XPATH, "..")
                                    if parent.tag_name in ['div', 'span'] and parent.is_displayed():
                                        clickable_element = parent
                                except:
                                    pass
                                
                                clickable_element.click()
                                time.sleep(5)
                                
                                if self.is_in_contact_chat():
                                    self.logger.info("✅ Successfully opened contact via alternative method")
                                    return True
                except Exception as e:
                    self.logger.debug(f"Error with pattern {pattern}: {e}")
                    continue
                    
            self.logger.warning("⚠️ No suitable contact found with alternative method")
            return False
            
        except Exception as e:
            self.logger.error(f"Error in alternative contact search: {e}")
            return False

    def wait_for_contact_to_load_enhanced(self):
        """Enhanced waiting for WhatsApp contact to load properly"""
        self.logger.info("⏳ Enhanced waiting for WhatsApp contact to load completely...")
        
        try:
            wait = WebDriverWait(self.driver, 25)  # Increased timeout
            
            # Phase 1: Wait for basic WhatsApp interface
            self.logger.info("🔄 Phase 1: Waiting for basic interface...")
            basic_selectors = [
                "div[role='application']", 
                "#main", 
                "[data-testid='conversation-panel-wrapper']",
                "div[data-testid='app']"
            ]
            
            interface_loaded = False
            for selector in basic_selectors:
                try:
                    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
                    self.logger.info(f"✅ Basic interface loaded: {selector}")
                    interface_loaded = True
                    break
                except:
                    continue
            
            if not interface_loaded:
                self.logger.warning("⚠️ Basic interface not detected with known selectors")
            
            # Phase 2: Wait for contact header with extended time
            self.logger.info("🔄 Phase 2: Waiting for contact header...")
            time.sleep(5)  # Increased wait time for header to appear
            
            header_loaded = False
            header_selectors = [
                "header[data-testid='conversation-header']",
                "div[data-testid='conversation-info-header']",
                "div[data-testid='chat-header']",
                "header div[title*='+']",
                "header span[title*='+']",
                "div[data-testid='cell-frame-title']"
            ]
            
            for selector in header_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and any(elem.is_displayed() for elem in elements):
                        self.logger.info(f"✅ Contact header found: {selector}")
                        header_loaded = True
                        break
                except:
                    continue
            
            if not header_loaded:
                self.logger.warning("⚠️ Contact header not found with known selectors")
            
            # Phase 3: Wait for loading indicators to disappear
            self.logger.info("🔄 Phase 3: Waiting for loading to complete...")
            
            loading_selectors = [
                "[data-testid='msg-dblcheck-sending']",
                "div[role='progressbar']",
                ".spinner",
                "[aria-label*='Loading']",
                "[aria-label*='loading']",
                "div[data-testid='startup-animation']"
            ]
            
            for selector in loading_selectors:
                try:
                    # Wait up to 10 seconds for each loading indicator to disappear
                    WebDriverWait(self.driver, 10).until_not(
                        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                    )
                    self.logger.info(f"✅ Loading indicator disappeared: {selector}")
                except:
                    continue  # Not found or already gone
            
            # Phase 4: Verify contact information is loaded
            self.logger.info("🔄 Phase 4: Verifying contact information...")
            contact_verified = self.verify_contact_info_loaded()
            
            # Phase 5: Final stability wait
            self.logger.info("🔄 Phase 5: Final stability wait...")
            time.sleep(6)  # Increased final wait for complete stabilization
            
            if contact_verified:
                self.logger.info("✅ Contact fully loaded and verified - ready for extraction")
            else:
                self.logger.warning("⚠️ Contact info verification failed - proceeding anyway")
            
        except Exception as e:
            self.logger.warning(f"⚠️ Error during enhanced contact loading wait: {e}")
            self.logger.info("🔄 Using extended fallback wait strategy...")
            time.sleep(20)  # Extended fallback wait

    def verify_contact_info_loaded(self):
        """Verify that contact information is actually loaded"""
        try:
            # Look for contact name or phone number in header
            info_selectors = [
                "header span[title*='+']",  # Phone number
                "header div[title]",  # Contact name
                "span[data-testid='conversation-info-header-chat-title']",
                "div[data-testid='cell-frame-title']",
                "header span[title]"  # Any title in header
            ]
            
            for selector in info_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for elem in elements:
                        if elem.is_displayed() and elem.text.strip():
                            text_preview = elem.text[:30] + "..." if len(elem.text) > 30 else elem.text
                            self.logger.info(f"✅ Contact info verified: '{text_preview}'")
                            return True
                except:
                    continue
            
            # Fallback: check for any visible text in header area
            try:
                header = self.driver.find_element(By.CSS_SELECTOR, "header")
                if header and header.text.strip():
                    self.logger.info("✅ Contact info found in header (fallback method)")
                    return True
            except:
                pass
            
            self.logger.warning("⚠️ No contact info found in header")
            return False
            
        except Exception as e:
            self.logger.error(f"Error verifying contact info: {e}")
            return False

    def connect_to_whatsapp(self):
        """Connect to WhatsApp Web - FIXED to directly use specific business contact"""
        self.logger.info("🔗 Connecting to WhatsApp Web for specific business contact...")

        # Store original window
        original_window = self.driver.current_window_handle
        
        # Wait for potential new tab opening
        time.sleep(3)
        current_windows = self.driver.window_handles

        # Find the new WhatsApp window that should have opened
        whatsapp_window = None
        for window in current_windows:
            if window != original_window:
                try:
                    self.driver.switch_to.window(window)
                    current_url = self.driver.current_url
                    
                    self.logger.info(f"🔍 Checking window: {current_url}")
                    
                    # Check if this is a WhatsApp URL
                    if 'whatsapp' in current_url.lower() or 'wa.me' in current_url.lower():
                        whatsapp_window = window
                        self.logger.info(f"✅ Found WhatsApp window: {current_url}")
                        
                        # Wait for WhatsApp to redirect to web.whatsapp.com
                        self.wait_for_whatsapp_redirect()
                        
                        # Check final URL after redirect
                        final_url = self.driver.current_url
                        self.logger.info(f"📱 Final WhatsApp URL: {final_url}")
                        
                        if 'web.whatsapp.com' not in final_url:
                            self.logger.error("❌ WhatsApp Web did not load properly")
                            self.driver.close()
                            if original_window in self.driver.window_handles:
                                self.driver.switch_to.window(original_window)
                            return "whatsapp_web_failed"
                        
                        # Check login status
                        page_type = self.detect_whatsapp_page_type()
                        if page_type == "login_required":
                            self.logger.error("❌ WhatsApp login required")
                            self.driver.close()
                            if original_window in self.driver.window_handles:
                                self.driver.switch_to.window(original_window)
                            return "login_required"
                        
                        # Should be directly in contact chat - wait for it to load
                        self.wait_for_specific_contact_to_load()
                        
                        # Save screenshot for debugging
                        screenshot_path = f"whatsapp_contact_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                        self.driver.save_screenshot(screenshot_path)
                        self.logger.info(f"📸 Contact screenshot saved: {screenshot_path}")
                        
                        # Mark this tab for closure later
                        self.whatsapp_tab_to_close = window
                        
                        return final_url
                        
                except Exception as e:
                    self.logger.debug(f"Error checking window: {e}")
                    continue

        # If we get here, no WhatsApp window was found
        if original_window in self.driver.window_handles:
            self.driver.switch_to.window(original_window)
        
        self.logger.error("❌ No WhatsApp window found")
        return None

    def wait_for_whatsapp_redirect(self):
        """Wait for WhatsApp to redirect from wa.me to web.whatsapp.com"""
        self.logger.info("⏳ Waiting for WhatsApp redirect...")
        
        max_wait = 15  # Maximum 15 seconds
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            current_url = self.driver.current_url
            
            if 'web.whatsapp.com' in current_url:
                self.logger.info("✅ WhatsApp Web loaded successfully")
                return True
            elif 'whatsapp://' in current_url:
                self.logger.warning("⚠️ WhatsApp app redirect detected")
                time.sleep(2)
            
            time.sleep(1)
        
        self.logger.warning("⚠️ WhatsApp redirect took longer than expected")
        return False

    def wait_for_specific_contact_to_load(self):
        """Wait for the specific business contact to load (NOT search through chat lists)"""
        self.logger.info("⏳ Waiting for specific business contact to load...")
        
        # Extended wait for contact header to appear
        max_wait = 20
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                # Look for contact header indicators
                header_selectors = [
                    "header[data-testid='conversation-header']",
                    "div[data-testid='conversation-info-header']", 
                    "div[data-testid='chat-header']",
                    "header span[title*='+']",  # Phone number in header
                    "header div[title]",        # Contact name in header
                    "span[data-testid='conversation-info-header-chat-title']"
                ]
                
                contact_found = False
                for selector in header_selectors:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and any(elem.is_displayed() for elem in elements):
                        self.logger.info(f"✅ Contact header found: {selector}")
                        contact_found = True
                        break
                
                if contact_found:
                    # Additional wait to ensure everything is loaded
                    time.sleep(5)
                    self.logger.info("✅ Specific business contact loaded successfully")
                    return True
                    
            except Exception as e:
                self.logger.debug(f"Waiting for contact: {e}")
                
            time.sleep(1)
        
        self.logger.warning("⚠️ Contact loading took longer than expected, proceeding anyway")
        return False

    # FIXED: Added missing is_whatsapp_logged_in method
    def is_whatsapp_logged_in(self):
        """Check if WhatsApp Web is logged in"""
        try:
            # Look for indicators that WhatsApp is logged in
            logged_in_indicators = [
                "[data-testid='chat-list']",
                "[data-testid='chatlist-search']", 
                ".two._aigs",  # Main WhatsApp interface
                "div[role='application']",  # WhatsApp app container
                "[aria-label*='Chat list']"
            ]
            
            for selector in logged_in_indicators:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and any(elem.is_displayed() for elem in elements):
                        return True
                except:
                    continue
                    
            # Check for QR code (means not logged in)
            qr_indicators = [
                "[data-testid='qr-code']",
                "canvas[aria-label*='QR']",
                ".landing-window"
            ]
            
            for selector in qr_indicators:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if elements and any(elem.is_displayed() for elem in elements):
                        return False
                except:
                    continue
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking WhatsApp login status: {e}")
            return False

    # FIXED: Added missing close_duplicate_whatsapp_tabs method
    def close_duplicate_whatsapp_tabs(self, original_window, keep_window):
        """Close duplicate WhatsApp tabs except the one we want to keep"""
        try:
            current_windows = self.driver.window_handles[:]
            for window in current_windows:
                if window != original_window and window != keep_window:
                    try:
                        self.driver.switch_to.window(window)
                        current_url = self.driver.current_url
                        
                        if 'whatsapp' in current_url.lower():
                            self.logger.info(f"🗑️ Closing duplicate WhatsApp tab: {current_url}")
                            self.driver.close()
                    except Exception as e:
                        self.logger.debug(f"Error closing duplicate tab: {e}")
                        continue
            
            # Switch back to the window we want to keep
            self.driver.switch_to.window(keep_window)
            
        except Exception as e:
            self.logger.error(f"Error closing duplicate tabs: {e}")

    # FIXED: Added missing close_whatsapp_tab method
    def close_whatsapp_tab(self):
        """Close the WhatsApp tab that was opened for extraction"""
        if self.whatsapp_tab_to_close and self.whatsapp_tab_to_close in self.driver.window_handles:
            try:
                current_window = self.driver.current_window_handle
                self.driver.switch_to.window(self.whatsapp_tab_to_close)
                self.logger.info("🗑️ Closing WhatsApp tab after extraction")
                self.driver.close()
                
                # Switch back to a remaining window
                remaining_windows = self.driver.window_handles
                if remaining_windows:
                    if current_window in remaining_windows:
                        self.driver.switch_to.window(current_window)
                    else:
                        self.driver.switch_to.window(remaining_windows[0])
                
                self.whatsapp_tab_to_close = None
                self.logger.info("✅ WhatsApp tab closed successfully")
                
            except Exception as e:
                self.logger.error(f"Error closing WhatsApp tab: {e}")
        else:
            self.logger.info("No WhatsApp tab to close or tab already closed")

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def get_groq_api_key(self):
        """Get Groq API key from environment"""
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            pass
        
        api_key = os.getenv('GROQ_API_KEY')
        if not api_key:
            self.logger.warning("GROQ_API_KEY not found in environment variables")
        return api_key
        
    def setup_driver(self, headless=None):
        """Setup Chrome driver - either connect to existing or create new"""
        if headless is None:
            headless = self.headless
            
        if self.use_existing_chrome:
            return self.connect_to_existing_chrome()
        else:
            return self.create_new_chrome_driver(headless)
            
    def connect_to_existing_chrome(self):
        """Connect to existing Chrome browser with debugging enabled"""
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

        try:
            self.logger.info("Attempting to connect to existing Chrome browser...")
            self.driver = webdriver.Chrome(options=chrome_options)
            
            # Test the connection
            current_url = self.driver.current_url
            self.logger.info(f"[SUCCESS] Connected to existing Chrome browser")
            self.logger.info(f"Current URL: {current_url}")
            
            # Hide webdriver property
            try:
                self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                self.logger.info("[SUCCESS] Webdriver property hidden")
            except Exception as js_error:
                self.logger.warning(f"[WARNING] Could not hide webdriver property: {js_error}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"[ERROR] Could not connect to existing Chrome: {e}")
            self.logger.error("Solutions:")
            self.logger.error("1. Start Chrome with: chrome.exe --remote-debugging-port=9222")
            self.logger.error("2. Or set use_existing_chrome=False to create new browser")
            return False
            
    def create_new_chrome_driver(self, headless=False):
        """Create new Chrome driver with optimized options"""
        chrome_options = Options()
        
        if headless:
            chrome_options.add_argument("--headless")
            self.logger.info("Running in headless mode")
        else:
            self.logger.info("Running with visible browser")
        
        # Enhanced options for better compatibility
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        
        # Disable images for faster loading (optional)
        if headless:
            chrome_options.add_argument("--disable-images")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            self.logger.info("Chrome driver initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"Failed to initialize Chrome driver: {e}")
            return False
            
    def search_business_on_justdial(self, business_name, city=""):
        """Search for business on JustDial"""
        try:
            self.logger.info(f"Searching for: '{business_name}' in '{city}'")
            
            # Navigate to JustDial
            self.driver.get("https://www.justdial.com")
            time.sleep(3)
            
            # Handle any popups
            self.handle_popups()
            
            # Find search box
            search_box = self.find_search_box()
            if not search_box:
                raise Exception("Could not find search box")
                
            # Clear and enter business name
            search_box.clear()
            time.sleep(0.5)
            search_box.send_keys(business_name)
            
            # Handle city if provided
            if city.strip():
                city_box = self.find_city_box()
                if city_box:
                    city_box.clear()
                    time.sleep(0.5)
                    city_box.send_keys(city.strip())
            
            # Submit search
            search_box.send_keys(Keys.RETURN)
            time.sleep(5)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return False
            
    def find_search_box(self):
        """Find search box using multiple selectors"""
        search_selectors = [
            "#srchbx",
            "input[name='ss']",
            "input[placeholder*='Search']",
            "input[placeholder*='search']",
            ".search-input",
            "#search-input"
        ]
        
        for selector in search_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed():
                    return element
            except:
                continue
        return None
        
    def find_city_box(self):
        """Find city input box"""
        city_selectors = [
            "input[placeholder*='City']",
            "input[placeholder*='city']",
            "input[name*='city']",
            "#city-input"
        ]
        
        for selector in city_selectors:
            try:
                element = self.driver.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed():
                    return element
            except:
                continue
        return None
        
    def handle_popups(self):
        """Handle various popups that may appear"""
        popup_selectors = [
            "button[class*='later']",
            "button[class*='close']",
            ".popup-close",
            "[aria-label*='close']",
            "[aria-label*='later']"
        ]
        
        for selector in popup_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    if elem.is_displayed():
                        elem.click()
                        time.sleep(1)
                        break
            except:
                continue
                
    def find_whatsapp_buttons(self):
        """Find all WhatsApp buttons using comprehensive selectors"""
        whatsapp_selectors = [
            # Standard selectors
            "span[class*='WhatsApp']",
            "a[class*='WhatsApp']",
            "div[class*='WhatsApp']",
            "button[class*='WhatsApp']",
            
            # Case insensitive
            "[class*='whatsapp' i]",
            "[aria-label*='whatsapp' i]",
            "[title*='whatsapp' i]",
            
            # Specific JustDial classes
            ".ml-5.si_WhatsApp",
            "span.ml-5[class*='WhatsApp']",
            
            # Link-based
            "a[href*='whatsapp']",
            "a[href*='wa.me']",
            
            # Image-based
            "img[alt*='WhatsApp']",
            "img[src*='whatsapp']",
            
            # React/Node.js component selectors
            "[data-testid*='whatsapp']",
            "[data-cy*='whatsapp']",
            "[data-qa*='whatsapp']",
            "div[role='button'][aria-label*='WhatsApp']"
        ]
        
        found_elements = []
        for selector in whatsapp_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for elem in elements:
                    if elem.is_displayed() and elem not in found_elements:
                        found_elements.append(elem)
            except:
                continue
                
        return found_elements
        
    def enhance_whatsapp_buttons(self):
        """Enhance WhatsApp buttons for better clicking (React/Node.js handling)"""
        enhancement_script = """
        // Enhanced WhatsApp button handler for React/Node.js components
        var enhanced = 0;
        var whatsappUrl = null;
        
        // Find WhatsApp URL from any source
        document.querySelectorAll('a[href*="whatsapp"], a[href*="wa.me"]').forEach(function(a) {
            if (!whatsappUrl && a.href) {
                whatsappUrl = a.href;
            }
        });
        
        // Enhanced selectors for React components
        var selectors = [
            '[class*="WhatsApp"]',
            '[class*="whatsapp" i]',
            '[aria-label*="whatsapp" i]',
            '[data-testid*="whatsapp"]',
            'div[role="button"][aria-label*="WhatsApp"]',
            'span.ml-5.si_WhatsApp'
        ];
        
        selectors.forEach(function(selector) {
            document.querySelectorAll(selector).forEach(function(elem) {
                // Visual enhancement
                elem.style.border = '2px solid #25D366';
                elem.style.backgroundColor = 'rgba(37, 211, 102, 0.1)';
                elem.style.cursor = 'pointer';
                elem.style.zIndex = '10000';
                elem.style.position = 'relative';
                
                // Remove blocking styles
                elem.style.pointerEvents = 'auto';
                elem.style.userSelect = 'auto';
                
                // Add React-compatible event handlers
                if (whatsappUrl) {
                    // Method 1: Standard onclick
                    elem.onclick = function(e) {
                        e.preventDefault();
                        e.stopPropagation();
                        window.open(whatsappUrl, '_blank');
                        return false;
                    };
                    
                    // Method 2: React synthetic events
                    ['click', 'mousedown', 'mouseup', 'touchstart', 'touchend'].forEach(function(eventType) {
                        elem.addEventListener(eventType, function(e) {
                            e.preventDefault();
                            e.stopPropagation();
                            if (eventType === 'click') {
                                window.open(whatsappUrl, '_blank');
                            }
                        }, true);
                    });
                    
                    enhanced++;
                }
            });
        });
        
        return {
            enhanced: enhanced,
            whatsappUrl: whatsappUrl
        };
        """
        
        result = self.driver.execute_script(enhancement_script)
        self.logger.info(f"Enhanced {result['enhanced']} WhatsApp buttons")
        return result
        
    def wait_for_new_whatsapp_tab(self):
        """Wait for a new WhatsApp tab to open and detect it - FIXED using reference code approach"""
        self.logger.info("⏳ Waiting for WhatsApp tab to open...")
        
        # Wait for potential new tab - simplified approach like reference code
        time.sleep(3)
        
        current_windows = len(self.driver.window_handles)
        self.logger.info(f"🔍 Detected {current_windows} total windows")
        
        return True  # Always return True since we'll verify in the next step

    def verify_whatsapp_tab_opened(self):
        """Verify that a WhatsApp tab was successfully opened - FIXED using reference code approach"""
        try:
            current_windows = self.driver.window_handles
            original_window = self.driver.current_window_handle
            
            self.logger.info(f"🔍 Checking {len(current_windows)} windows for WhatsApp...")
            
            # Check each window to find WhatsApp - approach from reference code
            for window in current_windows:
                if window != original_window:
                    try:
                        self.driver.switch_to.window(window)
                        current_url = self.driver.current_url
                        
                        self.logger.info(f"🔍 Checking window: {current_url}")
                        
                        if 'whatsapp' in current_url.lower() or 'wa.me' in current_url.lower():
                            self.logger.info(f"✅ WhatsApp tab confirmed: {current_url}")
                            return True, window
                            
                    except Exception as e:
                        self.logger.debug(f"Error checking window {window}: {e}")
                        continue
            
            # Switch back to original window if no WhatsApp found
            if original_window in self.driver.window_handles:
                self.driver.switch_to.window(original_window)
            
            self.logger.warning("⚠️ No WhatsApp tab found in any window")
            return False, None
            
        except Exception as e:
            self.logger.error(f"Error verifying WhatsApp tab: {e}")
            return False, None

    def click_first_whatsapp_button(self):
        """Click WhatsApp button using enhanced human-like behaviors or fallback to basic"""
        
        # Use enhanced clicking if available
        if ENHANCED_CLICKING_AVAILABLE:
            return self.enhanced_whatsapp_click_sequence_fixed()
        else:
            return self.basic_whatsapp_click_sequence_fixed()
    
    def enhanced_whatsapp_click_sequence_fixed(self):
        """FIXED enhanced WhatsApp clicking - properly triggers all human-like behaviors"""
        self.logger.info("🎭 Starting Enhanced Human-Like WhatsApp Click Sequence...")
        self.logger.info("📋 This will execute:")
        self.logger.info("   1. 📖 Simulate reading business info (2-4 seconds)")
        self.logger.info("   2. 👀 Compare other business options (1-3 businesses)")
        self.logger.info("   3. 📜 Natural page scrolling (explorer/reader pattern)")
        self.logger.info("   4. 🤔 Decision hesitation (3-8 seconds pause)")
        self.logger.info("   5. 👁️ Eye movement to WhatsApp button")
        self.logger.info("   6. 🖱️ Human-like click with random offset")
        self.logger.info("   7. ⏳ Wait for response with human patience")
        self.logger.info("   8. 🔄 Fallback methods if needed")
        
        try:
            # Initialize enhanced clicker
            clicker = EnhancedWhatsAppClicker(self.driver, self.logger)
            
            # First enhance the buttons using existing method
            enhancement_result = self.enhance_whatsapp_buttons()
            
            # Get WhatsApp buttons using existing method
            whatsapp_buttons = self.find_whatsapp_buttons()
            
            if not whatsapp_buttons:
                self.logger.error("❌ No WhatsApp buttons found")
                return False
            
            self.logger.info(f"📱 Found {len(whatsapp_buttons)} WhatsApp buttons")
            
            # FIXED: Call the enhanced clicking sequence with ALL buttons
            # This will trigger the complete human behavior simulation
            self.logger.info("🚀 Executing full enhanced human behavior sequence...")
            success = clicker.enhanced_whatsapp_click_sequence(whatsapp_buttons)
            
            if success:
                self.logger.info("✅ Enhanced human-like clicking completed successfully")
                return True
            else:
                self.logger.warning("❌ Enhanced clicking failed, falling back to basic clicking...")
                return self.basic_whatsapp_click_sequence_fixed()
                
        except Exception as e:
            self.logger.error(f"❌ Enhanced clicking failed: {e}")
            self.logger.info("🔄 Falling back to basic clicking...")
            return self.basic_whatsapp_click_sequence_fixed()
    
    def basic_whatsapp_click_sequence_fixed(self):
        """ENHANCED basic WhatsApp button clicking with detailed logging"""
        self.logger.info("🖱️ Starting Basic WhatsApp Button Click Sequence...")
        self.logger.info("📋 Basic sequence includes:")
        self.logger.info("   • Button enhancement and detection")
        self.logger.info("   • Human-like pauses before clicking")
        self.logger.info("   • Multiple click methods (Regular, JS, ActionChains, React)")
        self.logger.info("   • Proper error handling and fallbacks")
        
        # First enhance the buttons
        self.logger.info("🔧 Enhancing WhatsApp buttons for better detection...")
        enhancement_result = self.enhance_whatsapp_buttons()
        
        # Find WhatsApp buttons
        self.logger.info("🔍 Searching for WhatsApp buttons...")
        whatsapp_buttons = self.find_whatsapp_buttons()
        
        if not whatsapp_buttons:
            self.logger.error("❌ No WhatsApp buttons found")
            return False
            
        self.logger.info(f"✅ Found {len(whatsapp_buttons)} WhatsApp buttons")
        
        # Try clicking each button with detailed logging
        for i, button in enumerate(whatsapp_buttons):
            button_num = i + 1
            self.logger.info(f"\n🎯 === Attempting Button {button_num}/{len(whatsapp_buttons)} ===")
            
            try:
                # Check if button is visible and clickable
                if not button.is_displayed() or not button.is_enabled():
                    self.logger.warning(f"⚠️ Button {button_num} not clickable, skipping")
                    continue
                
                # Add human-like pause before clicking
                pause_time = random.uniform(1.0, 2.5)
                self.logger.info(f"⏳ Human pause before click: {pause_time:.1f}s")
                time.sleep(pause_time)
                
                # Scroll to button
                self.logger.info(f"📜 Scrolling button {button_num} into view...")
                self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", button)
                time.sleep(1)
                
                # Try different click methods with detailed logging
                click_methods = [
                    ("Regular click", lambda: button.click()),
                    ("JavaScript click", lambda: self.driver.execute_script("arguments[0].click();", button)),
                    ("ActionChains click", lambda: ActionChains(self.driver).move_to_element(button).click().perform()),
                    ("React event dispatch", lambda: self.driver.execute_script("""
                        var elem = arguments[0];
                        var events = ['mousedown', 'click', 'mouseup'];
                        events.forEach(function(eventType) {
                            var event = new MouseEvent(eventType, {
                                view: window,
                                bubbles: true,
                                cancelable: true
                            });
                            elem.dispatchEvent(event);
                        });
                    """, button))
                ]
                
                for method_name, click_method in click_methods:
                    try:
                        self.logger.info(f"🔄 Attempting {method_name} on button {button_num}")
                        click_method()
                        self.logger.info(f"✅ {method_name} executed successfully")
                        
                        # Wait for response
                        wait_time = random.uniform(3.0, 5.0)
                        self.logger.info(f"⏳ Waiting for response: {wait_time:.1f}s")
                        time.sleep(wait_time)
                        
                        self.logger.info(f"✅ Button {button_num} click sequence completed successfully")
                        return True
                        
                    except Exception as click_error:
                        self.logger.debug(f"❌ {method_name} failed: {click_error}")
                        continue
                        
            except Exception as e:
                self.logger.error(f"❌ Error with button {button_num}: {e}")
                continue
        
        self.logger.error("❌ All WhatsApp button click attempts failed")
        return False
        
    def human_click_element(self, element):
        """Perform human-like click on element with realistic mouse movement"""
        try:
            # Get element position
            element_rect = element.rect
            target_x = element_rect['x'] + element_rect['width'] // 2
            target_y = element_rect['y'] + element_rect['height'] // 2
            
            # Add random offset to avoid clicking exact center every time
            offset_x = random.randint(-10, 10)
            offset_y = random.randint(-8, 8)
            target_x += offset_x
            target_y += offset_y
            
            # Scroll element into view with human-like behavior
            self.driver.execute_script("""
                var element = arguments[0];
                var elementTop = element.offsetTop;
                var elementHeight = element.offsetHeight;
                var windowHeight = window.innerHeight;
                
                // Calculate target position with some randomness
                var targetTop = elementTop - (windowHeight / 2) + (elementHeight / 2);
                var overshoot = Math.random() * 50 - 25; // Random overshoot
                
                // Scroll with overshoot
                window.scrollTo({
                    top: targetTop + overshoot,
                    behavior: 'smooth'
                });
                
                // Correct the overshoot after a delay
                setTimeout(function() {
                    window.scrollTo({
                        top: targetTop,
                        behavior: 'smooth'
                    });
                }, 200 + Math.random() * 300);
            """, element)
            
            time.sleep(random.uniform(0.5, 1.2))  # Wait for scroll to complete
            
            # Human-like mouse movement and click
            actions = ActionChains(self.driver)
            
            # Move to element with some randomness
            actions.move_to_element_with_offset(element, offset_x, offset_y)
            
            # Human reaction time pause
            reaction_time = random.uniform(0.2, 0.6)
            if random.random() < 0.2:  # 20% chance of longer pause (reading/deciding)
                reaction_time += random.uniform(0.5, 1.5)
            
            actions.pause(reaction_time)
            
            # Human-like click (with press duration)
            actions.click_and_hold()
            actions.pause(random.uniform(0.08, 0.15))  # Human click duration
            actions.release()
            
            actions.perform()
            
            # Post-click human behavior
            time.sleep(random.uniform(0.3, 0.8))
            
            # Sometimes move mouse slightly after clicking
            if random.random() < 0.4:  # 40% chance
                post_actions = ActionChains(self.driver)
                post_actions.move_by_offset(
                    random.randint(-25, 25), 
                    random.randint(-20, 20)
                )
                post_actions.perform()
            
            self.logger.info("Human-like click executed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error in human click: {e}")
            return False
    
    def add_human_reading_pause(self):
        """Add realistic pause as if human is reading the page"""
        reading_time = random.uniform(1.2, 3.5)  # 1.2-3.5 seconds to "read"
        self.logger.info(f"Adding human reading pause: {reading_time:.1f}s")
        time.sleep(reading_time)
    
    def wait_for_response_with_human_patience(self):
        """Wait for page response with human-like patience"""
        # Humans wait a bit longer and check multiple times
        patience_time = random.uniform(4.0, 7.0)
        check_interval = 0.5
        
        start_time = time.time()
        while time.time() - start_time < patience_time:
            time.sleep(check_interval)
            # Check if something is loading
            try:
                loading_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                    "[class*='loading'], [class*='spinner'], [aria-label*='loading']")
                if not loading_elements:
                    break  # Nothing loading, can proceed
            except:
                pass
    
    def fallback_click_methods_with_timing(self, button, button_num):
        """Enhanced fallback click methods with improved timing and verification"""
        self.logger.info(f"🔄 Trying fallback click methods for button {button_num}...")
        
        fallback_methods = [
            ("JavaScript click", lambda: self.driver.execute_script("arguments[0].click();", button)),
            ("ActionChains click", lambda: ActionChains(self.driver).move_to_element(button).click().perform()),
            ("Offset click", lambda: ActionChains(self.driver).move_to_element_with_offset(button, 5, 5).click().perform()),
            ("React event dispatch", lambda: self.driver.execute_script("""
                var elem = arguments[0];
                var events = ['mousedown', 'click', 'mouseup'];
                events.forEach(function(eventType) {
                    var event = new MouseEvent(eventType, {
                        view: window,
                        bubbles: true,
                        cancelable: true
                    });
                    elem.dispatchEvent(event);
                });
            """, button)),
            ("Force click", lambda: self.driver.execute_script("""
                arguments[0].style.pointerEvents = 'auto';
                arguments[0].click();
            """, button))
        ]
        
        initial_windows = len(self.driver.window_handles)
        
        for method_name, click_method in fallback_methods:
            try:
                self.logger.info(f"🔄 Trying {method_name} on button {button_num}")
                click_method()
                
                # Wait for potential response with timing
                time.sleep(random.uniform(2.5, 4.0))
                
                # Check if new window opened
                current_windows = len(self.driver.window_handles)
                if current_windows > initial_windows:
                    self.logger.info(f"✅ {method_name} successful - new window detected")
                    return True
                    
            except Exception as click_error:
                self.logger.debug(f"❌ {method_name} failed: {click_error}")
                continue
                
        self.logger.warning(f"⚠️ All fallback methods failed for button {button_num}")
        return False
            
    def extract_phone_from_whatsapp(self):
        """Extract phone number from WhatsApp - FIXED to work with both direct contact and main interface"""
        try:
            self.logger.info("🔍 Extracting phone number from WhatsApp interface...")
            
            # Verify we're in a logged-in WhatsApp (not login page)
            page_type = self.detect_whatsapp_page_type()
            
            if page_type == "login_required":
                self.logger.error("❌ WhatsApp login required")
                return "LOGIN_REQUIRED"
            
            # Handle both contact_chat and logged_in_main cases
            if page_type in ["contact_chat", "logged_in_main"]:
                self.logger.info(f"✅ WhatsApp page type: {page_type} - proceeding with extraction")
                
                # For main interface, wait a bit for any contact to load
                if page_type == "logged_in_main":
                    self.logger.info("🔍 Main interface detected - checking for contact information...")
                    time.sleep(3)  # Give time for contact to appear
                    
                    # Check if we can find contact info in the interface
                    contact_found = self.check_for_contact_info_in_interface()
                    if contact_found:
                        self.logger.info("✅ Contact information found in main interface")
                    else:
                        self.logger.warning("⚠️ No obvious contact information found, but proceeding with screenshot")
                
                # Take screenshot regardless - vision model can handle both cases
                screenshot_path = f"whatsapp_extraction_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                self.driver.save_screenshot(screenshot_path)
                self.logger.info(f"📸 Screenshot taken for extraction: {screenshot_path}")
                
                # Extract number using vision model
                phone_number = self.extract_whatsapp_number_with_vision(screenshot_path)
                
                # Clean up screenshot
                try:
                    os.remove(screenshot_path)
                except:
                    pass
                    
                if phone_number:
                    self.logger.info(f"✅ Successfully extracted phone: {phone_number}")
                    return phone_number
                else:
                    self.logger.warning("⚠️ Vision extraction failed, trying backup method")
                    # Try backup extraction from page elements
                    phone_number = self.extract_phone_from_whatsapp_elements()
                    if phone_number:
                        self.logger.info(f"✅ Backup extraction successful: {phone_number}")
                        return phone_number
                    else:
                        self.logger.warning("⚠️ Both vision and backup extraction failed")
                        return None
            else:
                self.logger.error(f"❌ Unsupported WhatsApp page type: {page_type}")
                return f"UNSUPPORTED_PAGE_TYPE_{page_type.upper()}"
                
        except Exception as e:
            self.logger.error(f"Error extracting phone from WhatsApp: {e}")
            return None

    def check_for_contact_info_in_interface(self):
        """Check if contact information is visible in the WhatsApp interface"""
        try:
            # Look for contact information indicators in the interface
            contact_indicators = [
                "header span[title*='+']",  # Phone number in header
                "header div[title*='+']",   # Phone number in header div
                "span[data-testid='conversation-info-header-chat-title']",  # Contact name
                "div[data-testid='cell-frame-title']",  # Contact title
                "header[data-testid='conversation-header']",  # Conversation header
                "div[data-testid='conversation-info-header']",  # Conversation info
                "span[title*='+91']",  # Specific Indian numbers
                "div[title*='+91']",   # Indian numbers in div
                "[aria-label*='Chat with']",  # Chat with label
                "header span[title]",  # Any title in header
                "header div[title]"   # Any title in header div
            ]
            
            contact_info_found = False
            for selector in contact_indicators:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            text = element.text.strip() or element.get_attribute('title') or ''
                            if text and ('+' in text or any(char.isdigit() for char in text)):
                                self.logger.info(f"✅ Found contact indicator: '{text[:50]}...' via {selector}")
                                contact_info_found = True
                                break
                    if contact_info_found:
                        break
                except:
                    continue
            
            # Also check for any visible phone numbers in the page
            if not contact_info_found:
                try:
                    page_text = self.driver.find_element(By.TAG_NAME, "body").text
                    if '+91' in page_text or re.search(r'\d{10}', page_text):
                        self.logger.info("✅ Found phone number pattern in page text")
                        contact_info_found = True
                except:
                    pass
            
            return contact_info_found
            
        except Exception as e:
            self.logger.debug(f"Error checking for contact info: {e}")
            return False

    def extract_phone_from_whatsapp_elements(self):
        """Backup method: Extract phone from WhatsApp page elements"""
        try:
            self.logger.info("🔄 Trying backup extraction from page elements...")
            
            # Look for phone number in header elements
            phone_selectors = [
                "header span[title*='+91']",
                "header div[title*='+91']",
                "header span[title*='+']",
                "span[data-testid='conversation-info-header-chat-title']",
                "div[data-testid='cell-frame-title']"
            ]
            
            for selector in phone_selectors:
                try:
                    elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            title = element.get_attribute('title') or element.text
                            if title and '+' in title:
                                # Extract phone number
                                phone_match = re.search(r'\+91[\s-]?(\d{10})', title)
                                if phone_match:
                                    phone_number = phone_match.group(1)
                                    self.logger.info(f"✅ Backup extraction successful: {phone_number}")
                                    return phone_number
                                    
                                # Try without country code
                                phone_match = re.search(r'(\d{10})', title)
                                if phone_match and phone_match.group(1)[0] in '6789':
                                    phone_number = phone_match.group(1)
                                    self.logger.info(f"✅ Backup extraction successful: {phone_number}")
                                    return phone_number
                except:
                    continue
                    
            self.logger.warning("⚠️ Backup extraction also failed")
            return None
            
        except Exception as e:
            self.logger.error(f"Error in backup extraction: {e}")
            return None

    def extract_whatsapp_number_with_vision(self, screenshot_path):
        """Extract WhatsApp number using Groq vision model with enhanced header-focused prompting"""
        self.logger.info("🔍 Extracting WhatsApp number using vision model...")
        
        if not self.groq_api_key:
            self.logger.error("❌ Groq API key not available")
            return None
            
        try:
            # Read and encode screenshot
            with open(screenshot_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Prepare Groq API request with enhanced header-focused prompt
            headers = {
                'Authorization': f'Bearer {self.groq_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Look at this WhatsApp Web screenshot. Extract the phone number that's currently visible in the interface. This could be in the TOP HEADER area of an active chat, or visible anywhere in the main interface. IGNORE phone numbers from the chat list on the left side. Focus on the MAIN CONTENT area where contact information would be displayed. Look for patterns like +91 XXXXXXXXXX or similar. Extract ONLY the 10-digit number (without +91 country code). Example: if you see '+91 80561 75751' respond with '8056175751'. If no phone number is clearly visible, respond with 'NOT_FOUND'. Respond with ONLY the 10-digit number, nothing else."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 30,
                "temperature": 0.0
            }
            
            # Make API request
            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                extracted_text = result['choices'][0]['message']['content'].strip()
                
                self.logger.info(f"🤖 Groq vision model response: {extracted_text}")
                
                # Extract phone number from response
                if extracted_text != 'NOT_FOUND':
                    # Clean the response and extract digits
                    phone_number = re.sub(r'\D', '', extracted_text)  # Remove non-digits
                    
                    # Validate phone number (should be 10 digits for Indian numbers)
                    if len(phone_number) >= 10:
                        # Take last 10 digits in case there's country code
                        phone_number = phone_number[-10:]
                        self.logger.info(f"✅ WhatsApp number extracted via vision: {phone_number}")
                        return phone_number
                    else:
                        self.logger.warning(f"⚠️ Invalid phone number format: {phone_number}")
                        # Try a second extraction attempt with different prompting
                        return self.retry_number_extraction(screenshot_path)
                else:
                    self.logger.warning("⚠️ No phone number found in WhatsApp screenshot header")
                    # Try a second extraction attempt
                    return self.retry_number_extraction(screenshot_path)
            else:
                self.logger.error(f"❌ Groq API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error in vision-based number extraction: {e}")
            return None

    def retry_number_extraction(self, screenshot_path):
        """Retry number extraction with alternative prompting"""
        self.logger.info("🔄 Retrying number extraction with alternative approach...")
        
        try:
            # Read and encode screenshot
            with open(screenshot_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            headers = {
                'Authorization': f'Bearer {self.groq_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "In this WhatsApp screenshot, look for a phone number that's visible in the interface. This could be in the TOP HEADER area, in the main content area, or anywhere contact information is displayed. Ignore phone numbers from the chat list on the left. Look for patterns like: +91 XXXXXXXXXX, 91 XXXXXXXXXX, or +91-XXXX-XXXXXX. Extract only the 10-digit mobile number (without country code +91). Example: if you see '+91 80561 75751' respond with '8056175751'. Respond with only the 10 digits."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 30,
                "temperature": 0.0
            }
            
            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                extracted_text = result['choices'][0]['message']['content'].strip()
                
                self.logger.info(f"🔄 Retry extraction response: {extracted_text}")
                
                # Extract phone number from response
                phone_number = re.sub(r'\D', '', extracted_text)
                
                if len(phone_number) >= 10:
                    phone_number = phone_number[-10:]
                    self.logger.info(f"✅ WhatsApp number extracted via retry: {phone_number}")
                    return phone_number
                else:
                    self.logger.warning("⚠️ Retry extraction also failed")
                    return None
            else:
                self.logger.error(f"❌ Retry API error: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error in retry extraction: {e}")
            return None

    def close_any_extra_windows(self):
        """Close any extra windows and return to original JustDial window"""
        try:
            current_windows = self.driver.window_handles
            if len(current_windows) > 1:
                # Keep only the first window (JustDial)
                original_window = current_windows[0]
                
                # Close all other windows
                for window in current_windows[1:]:
                    try:
                        self.driver.switch_to.window(window)
                        self.driver.close()
                    except:
                        pass
                
                # Switch back to original window
                self.driver.switch_to.window(original_window)
                self.logger.info("✅ Closed extra windows and returned to JustDial")
                
        except Exception as e:
            self.logger.error(f"Error closing extra windows: {e}")

    def test_vision_extraction_with_screenshot(self, screenshot_path):
        """Test vision extraction with the provided screenshot"""
        self.logger.info(f"🧪 Testing vision extraction with screenshot: {screenshot_path}")
        
        # Check if file exists
        if not os.path.exists(screenshot_path):
            self.logger.error(f"❌ Screenshot file not found: {screenshot_path}")
            return False
        
        # Check API key
        if not self.groq_api_key:
            self.logger.error("❌ GROQ_API_KEY not found in environment")
            return False
        
        self.logger.info(f"✅ API key found: {self.groq_api_key[:10]}...")
        
        # Test the vision extraction
        try:
            phone_number = self.extract_whatsapp_number_with_vision(screenshot_path)
            
            if phone_number:
                self.logger.info(f"✅ Vision extraction successful: {phone_number}")
                return phone_number
            else:
                self.logger.warning("⚠️ Vision extraction returned None")
                
                # Try backup extraction
                self.logger.info("🔄 Trying backup element extraction...")
                backup_number = self.extract_phone_from_whatsapp_elements()
                
                if backup_number:
                    self.logger.info(f"✅ Backup extraction successful: {backup_number}")
                    return backup_number
                else:
                    self.logger.error("❌ Both vision and backup extraction failed")
                    return None
                    
        except Exception as e:
            self.logger.error(f"❌ Test vision extraction failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    def research_single_business(self, business_name, city=""):
        """Research a single business with anti-detection and fallback methods"""
        try:
            self.logger.info(f"🔍 Starting research for: '{business_name}' in '{city}'")
            
            # Setup driver with the configured method
            if not self.setup_driver():
                self.logger.error("❌ Driver setup failed")
                return {
                    'business_name': business_name,
                    'city': city,
                    'justdial_phone': 'Driver setup failed',
                    'status': 'driver_error',
                    'research_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
            # Add anti-detection delays
            time.sleep(random.uniform(3, 7))  # Random delay between requests
            
            # Search business
            self.logger.info(f"🔎 Searching for business on JustDial...")
            if not self.search_business_on_justdial(business_name, city):
                self.logger.error("❌ Business search failed")
                return {
                    'business_name': business_name,
                    'city': city,
                    'justdial_phone': 'Search failed',
                    'status': 'search_error',
                    'research_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
            # Add human-like delay after search
            time.sleep(random.uniform(2, 4))
                
            # Try WhatsApp extraction first
            self.logger.info(f"📱 Attempting WhatsApp extraction...")
            whatsapp_result = self.try_whatsapp_extraction(business_name, city)
            if whatsapp_result and whatsapp_result.get('status') == 'success':
                self.logger.info(f"✅ WhatsApp extraction successful for {business_name}")
                return whatsapp_result
                
            # Fallback: Direct phone extraction from JustDial page
            self.logger.info(f"🔄 WhatsApp extraction failed for {business_name}, trying direct extraction")
            phone_number = self.extract_phone_directly_from_page()
            
            result = {
                'business_name': business_name,
                'city': city,
                'justdial_phone': phone_number if phone_number else 'Not found',
                'status': 'direct_extraction' if phone_number else 'failed',
                'extraction_method': 'direct_justdial',
                'research_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            if phone_number:
                self.logger.info(f"✅ Direct extraction successful: {phone_number}")
            else:
                self.logger.warning(f"⚠️ No phone number found for {business_name}")
                
            return result
                
        except Exception as e:
            self.logger.error(f"❌ Error researching {business_name}: {e}")
            import traceback
            traceback.print_exc()
            return {
                'business_name': business_name,
                'city': city,
                'justdial_phone': 'Error',
                'status': 'error',
                'error_message': str(e),
                'research_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        finally:
            # Cleanup and anti-detection measures
            if self.driver:
                # Add random delay before closing/reusing
                time.sleep(random.uniform(1, 3))

    def try_whatsapp_extraction(self, business_name, city):
        """FIXED WhatsApp extraction - simplified flow"""
        try:
            self.logger.info(f"📱 Starting WhatsApp extraction for {business_name}")
            
            # Click WhatsApp button - should open direct contact
            if not self.click_first_whatsapp_button():
                self.logger.warning(f"❌ No WhatsApp button found for {business_name}")
                return {
                    'business_name': business_name,
                    'city': city,
                    'justdial_phone': 'No WhatsApp button found',
                    'status': 'no_whatsapp_button',
                    'research_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
            # Connect to WhatsApp (should be direct contact)
            whatsapp_url = self.connect_to_whatsapp()
            
            # Handle connection results
            if whatsapp_url == "login_required":
                self.close_any_extra_windows()
                return {
                    'business_name': business_name,
                    'city': city,
                    'justdial_phone': 'WhatsApp login required',
                    'status': 'whatsapp_login_required',
                    'research_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
            elif whatsapp_url == "whatsapp_web_failed":
                self.close_any_extra_windows()
                return {
                    'business_name': business_name,
                    'city': city,
                    'justdial_phone': 'WhatsApp Web failed to load',
                    'status': 'whatsapp_web_failed',
                    'research_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
            elif whatsapp_url and 'web.whatsapp.com' in whatsapp_url:
                # Extract phone number directly (no searching needed)
                phone_number = self.extract_phone_from_whatsapp()
                
                # Close WhatsApp tab and return to JustDial
                self.close_whatsapp_tab()
                
                # Handle extraction results
                if phone_number == "LOGIN_REQUIRED":
                    return {
                        'business_name': business_name,
                        'city': city,
                        'justdial_phone': 'WhatsApp login required',
                        'status': 'whatsapp_login_required',
                        'research_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                elif phone_number == "UNEXPECTED_MAIN_INTERFACE":
                    return {
                        'business_name': business_name,
                        'city': city,
                        'justdial_phone': 'WhatsApp opened to main interface',
                        'status': 'whatsapp_wrong_page',
                        'research_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                else:
                    return {
                        'business_name': business_name,
                        'city': city,
                        'justdial_phone': phone_number if phone_number else 'Not found',
                        'status': 'success' if phone_number else 'extraction_failed',
                        'extraction_method': 'whatsapp_direct_contact',
                        'research_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
            else:
                self.close_any_extra_windows()
                return {
                    'business_name': business_name,
                    'city': city,
                    'justdial_phone': 'WhatsApp connection failed',
                    'status': 'whatsapp_connection_failed',
                    'research_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
        except Exception as e:
            self.logger.error(f"❌ WhatsApp extraction error for {business_name}: {e}")
            self.close_any_extra_windows()
            return {
                'business_name': business_name,
                'city': city,
                'justdial_phone': 'Extraction error',
                'status': 'error',
                'error_message': str(e),
                'research_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

    def extract_phone_directly_from_page(self):
        """Extract phone numbers directly from JustDial page without WhatsApp"""
        self.logger.info("📋 Attempting direct phone extraction from JustDial page...")
        
        phone_numbers = []
        
        # Method 1: Look for phone numbers in contact sections
        contact_selectors = [
            "[class*='contact']",
            "[class*='phone']", 
            "[class*='mobile']",
            "[class*='number']",
            ".phn",
            ".contact-info",
            ".phone-number",
            ".callcontent",
            ".tel",
            ".phoneNumber",
            "[data-phone]",
            "[data-contact]",
            "span[title*='phone']",
            "div[title*='contact']",
            "a[href*='tel:']"
        ]
        
        for selector in contact_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for element in elements:
                    if element.is_displayed():
                        text = element.text.strip()
                        if text:
                            phone_numbers.append(text)
                            
                        # Check data attributes
                        for attr in ['data-phone', 'data-contact', 'title', 'alt']:
                            attr_value = element.get_attribute(attr)
                            if attr_value:
                                phone_numbers.append(attr_value)
                                
            except Exception as e:
                self.logger.debug(f"Error with selector {selector}: {e}")
                continue
        
        # Method 2: Click show number buttons first
        self.click_show_number_buttons()
        time.sleep(3)
        
        # Method 3: Extract from page text
        try:
            page_text = self.driver.find_element(By.TAG_NAME, "body").text
            patterns = [
                r'\+91[\s-]?[6-9]\d{9}',  # +91 format
                r'\b[6-9]\d{9}\b',        # 10 digit mobile
                r'\d{3}[\s-]\d{3}[\s-]\d{4}',  # 3-3-4 format
                r'\d{5}[\s-]\d{5}',       # 5-5 format
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, page_text)
                phone_numbers.extend(matches)
                
        except Exception as e:
            self.logger.debug(f"Error extracting from page text: {e}")
        
        # Clean and validate phone numbers
        clean_numbers = self.clean_and_validate_numbers(phone_numbers)
        
        if clean_numbers:
            self.logger.info(f"✅ Found {len(clean_numbers)} phone numbers via direct extraction: {clean_numbers}")
            return clean_numbers[0]  # Return first valid number
        else:
            self.logger.warning("⚠️ No phone numbers found via direct extraction")
            return None

    def click_show_number_buttons(self):
        """Click any 'Show Number' or similar buttons to reveal phone numbers"""
        show_number_selectors = [
            "button[class*='show']",
            "button[class*='number']", 
            "button[class*='contact']",
            ".show-number",
            ".reveal-number",
            "a[class*='show']",
            "[onclick*='number']",
            "[onclick*='phone']"
        ]
        
        clicked_any = False
        
        for selector in show_number_selectors:
            try:
                buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for button in buttons:
                    if button.is_displayed() and button.is_enabled():
                        button_text = button.text.lower()
                        if any(keyword in button_text for keyword in ['show', 'reveal', 'number', 'contact']):
                            try:
                                button.click()
                                time.sleep(2)
                                clicked_any = True
                                self.logger.info(f"✅ Clicked show number button: {button.text}")
                            except:
                                pass
                                
            except Exception as e:
                self.logger.debug(f"Error clicking show number buttons: {e}")
                continue
                
        return clicked_any

    def clean_and_validate_numbers(self, phone_numbers):
        """Clean and validate extracted phone numbers"""
        clean_numbers = []
        
        for number in phone_numbers:
            # Remove non-numeric characters
            clean_number = re.sub(r'[^\d]', '', str(number))
            
            # Handle +91 country code
            if clean_number.startswith('91') and len(clean_number) == 12:
                clean_number = clean_number[2:]
            elif clean_number.startswith('91') and len(clean_number) == 13:
                clean_number = clean_number[3:]
                
            # Validate Indian mobile number (10 digits, starts with 6-9)
            if len(clean_number) == 10 and clean_number[0] in '6789':
                if clean_number not in clean_numbers:  # Avoid duplicates
                    clean_numbers.append(clean_number)
                    
        return clean_numbers

    def extract_whatsapp_number_with_vision(self, screenshot_path):
        """Extract WhatsApp number using Groq vision model with enhanced header-focused prompting"""
        self.logger.info("🔍 Extracting WhatsApp number using vision model...")
        
        if not self.groq_api_key:
            self.logger.error("❌ Groq API key not available")
            return None
            
        try:
            # Read and encode screenshot
            with open(screenshot_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            # Prepare Groq API request with enhanced header-focused prompt
            headers = {
                'Authorization': f'Bearer {self.groq_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Look at this WhatsApp Web screenshot. I need you to extract the phone number of the ACTIVE CONTACT from the TOP HEADER area of the chat. IGNORE all phone numbers in the chat list on the left side - those are other contacts. Focus ONLY on the header area at the TOP where the current active contact's information is displayed. The number will appear as +91 XXXXXXXXXX or similar. Extract ONLY the 10-digit number (without +91 country code). Example: if you see '+91 81440 06802' respond with '8144006802'. If no phone number is visible in the TOP HEADER area, respond with 'NOT_FOUND'. Respond with ONLY the 10-digit number, nothing else."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 30,
                "temperature": 0.0
            }
            
            # Make API request
            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                extracted_text = result['choices'][0]['message']['content'].strip()
                
                self.logger.info(f"🤖 Groq vision model response: {extracted_text}")
                
                # Extract phone number from response
                if extracted_text != 'NOT_FOUND':
                    # Clean the response and extract digits
                    phone_number = re.sub(r'\D', '', extracted_text)  # Remove non-digits
                    
                    # Validate phone number (should be 10 digits for Indian numbers)
                    if len(phone_number) >= 10:
                        # Take last 10 digits in case there's country code
                        phone_number = phone_number[-10:]
                        self.logger.info(f"✅ WhatsApp number extracted via vision: {phone_number}")
                        return phone_number
                    else:
                        self.logger.warning(f"⚠️ Invalid phone number format: {phone_number}")
                        # Try a second extraction attempt with different prompting
                        return self.retry_number_extraction(screenshot_path)
                else:
                    self.logger.warning("⚠️ No phone number found in WhatsApp screenshot header")
                    # Try a second extraction attempt
                    return self.retry_number_extraction(screenshot_path)
            else:
                self.logger.error(f"❌ Groq API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error in vision-based number extraction: {e}")
            return None

    def retry_number_extraction(self, screenshot_path):
        """Retry number extraction with alternative prompting"""
        self.logger.info("🔄 Retrying number extraction with alternative approach...")
        
        try:
            # Read and encode screenshot
            with open(screenshot_path, 'rb') as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            headers = {
                'Authorization': f'Bearer {self.groq_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "model": "meta-llama/llama-4-scout-17b-16e-instruct",
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "In this WhatsApp screenshot, look specifically at the TOP of the screen where the contact name and number are shown in the header bar. Ignore all phone numbers from the chat list on the left. Find the phone number that appears near the contact name at the very top. Look for patterns like: +91 XXXXXXXXXX, 91 XXXXXXXXXX, or +91-XXXX-XXXXXX. Extract only the 10-digit mobile number (without country code +91). Example: if you see '+91 81440 06802' respond with '8144006802'. Respond with only the 10 digits."
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{image_data}"
                                }
                            }
                        ]
                    }
                ],
                "max_tokens": 30,
                "temperature": 0.0
            }
            
            response = requests.post(
                'https://api.groq.com/openai/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                extracted_text = result['choices'][0]['message']['content'].strip()
                
                self.logger.info(f"🔄 Retry extraction response: {extracted_text}")
                
                # Extract phone number from response
                phone_number = re.sub(r'\D', '', extracted_text)
                
                if len(phone_number) >= 10:
                    phone_number = phone_number[-10:]
                    self.logger.info(f"✅ WhatsApp number extracted via retry: {phone_number}")
                    return phone_number
                else:
                    self.logger.warning("⚠️ Retry extraction also failed")
                    return None
            else:
                self.logger.error(f"❌ Retry API error: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"❌ Error in retry extraction: {e}")
            return None


# Keep all the remaining code exactly the same (async functions, etc.)
async def research_businesses_justdial(businesses_data, use_existing_chrome=True, headless=False):
    """
    Research businesses using JustDial
    
    Args:
        businesses_data: List of tuples (business_name, city)
        use_existing_chrome: Whether to connect to existing Chrome browser
        headless: Whether to run in headless mode (if creating new browser)
    
    Returns:
        List of research results
    """
    try:
        print(f"research_businesses_justdial called with {len(businesses_data)} businesses")
        print(f"Using existing Chrome: {use_existing_chrome}, Headless: {headless}")
        
        groq_api_key = os.getenv('GROQ_API_KEY')
        if not groq_api_key:
            raise Exception("GROQ_API_KEY not found in environment")
            
        researcher = JustDialStreamlitResearcher(
            groq_api_key=groq_api_key,
            use_existing_chrome=use_existing_chrome,
            headless=headless
        )
        results = []
        
        for i, (business_name, city) in enumerate(businesses_data):
            print(f"Researching {i+1}/{len(businesses_data)}: {business_name} in {city}")
            
            # Update progress in Streamlit if available
            try:
                if 'st' in globals():
                    st.info(f"Researching: {business_name} in {city}")
            except:
                pass
                
            result = researcher.research_single_business(business_name, city)
            if result:
                results.append(result)
                print(f"Research completed for {business_name}: {result.get('status', 'unknown')}")
            else:
                print(f"No result for {business_name}")
                
            # Small delay between requests
            await asyncio.sleep(1)
            
        print(f"Completed research, returning {len(results)} results")
        return results
        
    except Exception as e:
        print(f"Error in research_businesses_justdial: {e}")
        import traceback
        traceback.print_exc()
        return []


# Function to be called from web_scraping_module.py
async def research_selected_businesses_justdial(selected_business_names, df, consignee_column):
    """
    Research selected businesses using JustDial
    
    Args:
        selected_business_names: List of business names
        df: DataFrame containing business data
        consignee_column: Column name containing business names
        
    Returns:
        tuple: (results_dataframe, summary_dict, csv_filename)
    """
    # Ensure pandas is available in function scope
    import pandas as pd
    
    try:
        print(f"Starting JustDial research for {len(selected_business_names)} businesses")
        
        # Prepare business data with cities
        businesses_data = []
        
        # Find city column (common patterns)
        city_column = None
        for col in df.columns:
            col_lower = col.lower()
            if any(keyword in col_lower for keyword in ['city', 'location', 'place', 'address']):
                city_column = col
                break
                
        print(f"Found city column: {city_column}")
                
        for business_name in selected_business_names:
            # Find the business in the dataframe
            business_rows = df[df[consignee_column] == business_name]
            if not business_rows.empty:
                city = ""
                if city_column and city_column in business_rows.columns:
                    city_value = business_rows.iloc[0][city_column]
                    # Use pandas.isna for null checking
                    if pd.isna(city_value) or str(city_value).lower() == 'nan':
                        city = ""
                    else:
                        city = str(city_value)
                businesses_data.append((business_name, city))
                print(f"Added business: {business_name} in {city}")
            else:
                businesses_data.append((business_name, ""))
                print(f"Added business: {business_name} (no location)")
                
        # Research businesses with existing Chrome browser connection
        print("Starting research process...")
        research_results = await research_businesses_justdial(
            businesses_data, 
            use_existing_chrome=True, 
            headless=False
        )
        
        # Convert to DataFrame
        if research_results:
            print(f"Got {len(research_results)} research results")
            results_df = pd.DataFrame(research_results)
            
            # Calculate summary
            total_processed = len(research_results)
            successful = len([r for r in research_results if r.get('status') == 'success'])
            failed = total_processed - successful
            
            summary = {
                'total_processed': total_processed,
                'successful': successful,
                'failed': failed,
                'success_rate': (successful / total_processed * 100) if total_processed > 0 else 0,
                'research_method': 'justdial'
            }
            
            # Save to CSV
            csv_filename = f"justdial_research_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
            results_df.to_csv(csv_filename, index=False)
            print(f"Results saved to {csv_filename}")
            
            return results_df, summary, csv_filename
        else:
            print("No research results obtained")
            return None, None, None
            
    except Exception as e:
        print(f"Error in research_selected_businesses_justdial: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None


def start_chrome_with_debugging():
    """Start Chrome with remote debugging enabled"""
    print("\n" + "=" * 80)
    print("STARTING CHROME WITH REMOTE DEBUGGING")
    print("=" * 80)
    print("\nThis will open Chrome where you can manually navigate and login to JustDial")
    print("Keep this Chrome window open during research")
    print("=" * 80)

    # Kill any existing Chrome processes
    try:
        if os.name == 'nt':  # Windows
            os.system("taskkill /f /im chrome.exe 2>nul")
        else:  # Linux/Mac
            os.system("pkill chrome")
        time.sleep(2)
    except:
        pass

    # Start Chrome with remote debugging
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
                break
    else:  # Linux/Mac
        chrome_path = "google-chrome"  # Assumes chrome is in PATH

    if chrome_path:
        # Create user data directory
        user_data_dir = os.path.join(os.path.dirname(__file__), "chrome_debug_profile")
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)

        # Start Chrome
        cmd = f'"{chrome_path}" --remote-debugging-port={debugging_port} --user-data-dir="{user_data_dir}"'

        print(f"\nStarting Chrome with command:")
        print(cmd)

        # Start Chrome in background
        if os.name == 'nt':
            import subprocess
            subprocess.Popen(cmd, shell=True)
        else:
            import subprocess
            subprocess.Popen(cmd, shell=True)

        time.sleep(3)

        print("\n[SUCCESS] Chrome started with debugging enabled")
        print("\n" + "=" * 80)
        print("IMPORTANT STEPS:")
        print("=" * 80)
        print("1. Go to https://www.justdial.com in the opened Chrome")
        print("2. Navigate and search manually to ensure the site loads properly")
        print("3. Keep this Chrome window open")
        print("4. Now you can run JustDial research from the web interface")
        print("=" * 80)

        return True
    else:
        print("[ERROR] Could not find Chrome installation")
        return False


def check_chrome_debugging_connection():
    """Check if Chrome is running with debugging enabled"""
    try:
        chrome_options = Options()
        chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        
        driver = webdriver.Chrome(options=chrome_options)
        current_url = driver.current_url
        driver.quit()
        
        print(f"✅ Chrome debugging connection successful")
        print(f"Current URL: {current_url}")
        return True
        
    except Exception as e:
        print(f"❌ Chrome debugging connection failed: {e}")
        print("\nTo fix this:")
        print("1. Close all Chrome windows")
        print("2. Run: chrome.exe --remote-debugging-port=9222")
        print("3. Or use the start_chrome_with_debugging() function")
        return False