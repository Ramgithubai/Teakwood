#!/usr/bin/env python3
"""
Enhanced WhatsApp Click Strategy for JustDial Anti-Detection
Combines multiple human-like behaviors to bypass blocking
"""

import time
import random
import math
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotInteractableException

class EnhancedWhatsAppClicker:
    def __init__(self, driver, logger=None):
        self.driver = driver
        self.logger = logger
        self.click_attempts = []  # Track clicking patterns
        self.session_start = time.time()
        
    def simulate_human_research_behavior(self):
        """Simulate human researching behavior before clicking WhatsApp"""
        if self.logger:
            self.logger.info("🎭 Starting human research behavior simulation...")
            
        behaviors = [
            self.simulate_reading_business_info,
            self.simulate_comparing_options,
            self.simulate_scrolling_exploration,
            self.simulate_hesitation_behavior
        ]
        
        # Execute 2-3 random behaviors
        selected_behaviors = random.sample(behaviors, random.randint(2, 3))
        
        for behavior in selected_behaviors:
            try:
                behavior()
            except Exception as e:
                if self.logger:
                    self.logger.debug(f"Behavior simulation error: {e}")
                continue
    
    def simulate_reading_business_info(self):
        """Simulate reading business information"""
        if self.logger:
            self.logger.info("1. 📖 Simulate reading business info (2-4 seconds)")
            
        # Look for business name, address, ratings
        info_selectors = [
            'h1', 'h2', 'h3',  # Business names
            '[class*="rating"]', '[class*="star"]',  # Ratings
            '[class*="address"]', '[class*="location"]',  # Address
            '[class*="about"]', '[class*="description"]'  # About section
        ]
        
        for selector in info_selectors:
            try:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    # Random element selection
                    element = random.choice(elements[:3])  # First 3 elements
                    
                    # Scroll to element and "read" it
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    
                    # Reading time based on text length
                    text_length = len(element.text) if element.text else 50
                    reading_time = min(max(text_length * 0.05, 1.0), 4.0)  # 1-4 seconds
                    
                    if self.logger:
                        self.logger.info(f"👁️ Reading element text ({len(element.text or '')} chars) for {reading_time:.1f}s")
                    
                    time.sleep(reading_time)
                    break
            except:
                continue
    
    def simulate_comparing_options(self):
        """Simulate comparing multiple businesses"""
        if self.logger:
            self.logger.info("2. 👀 Compare other business options (1-3 businesses)")
            
        try:
            # Look for other business listings
            business_cards = self.driver.find_elements(By.CSS_SELECTOR, 
                '[class*="card"], [class*="listing"], [class*="business"]')
            
            if len(business_cards) > 1:
                # Quickly view 1-2 other businesses
                comparison_count = random.randint(1, min(2, len(business_cards)-1))
                
                if self.logger:
                    self.logger.info(f"👀 Comparing {comparison_count} other options...")
                
                for _ in range(comparison_count):
                    card = random.choice(business_cards)
                    try:
                        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
                        time.sleep(random.uniform(1.5, 3.0))  # Brief comparison
                    except:
                        continue
        except Exception as e:
            if self.logger:
                self.logger.debug(f"Comparison simulation error: {e}")
    
    def simulate_scrolling_exploration(self):
        """Simulate natural page exploration"""
        if self.logger:
            self.logger.info("3. 📜 Natural page scrolling (explorer/reader pattern)")
            
        # Random scrolling patterns
        scroll_patterns = [
            self.scroll_pattern_explorer,
            self.scroll_pattern_reader,
            self.scroll_pattern_scanner
        ]
        
        selected_pattern = random.choice(scroll_patterns)
        selected_pattern()
    
    def scroll_pattern_explorer(self):
        """Exploration scrolling - up and down movements"""
        for _ in range(random.randint(2, 4)):
            # Scroll down
            scroll_amount = random.randint(200, 500)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(0.8, 2.0))
            
            # Sometimes scroll back up
            if random.random() < 0.4:
                back_scroll = random.randint(100, scroll_amount//2)
                self.driver.execute_script(f"window.scrollBy(0, -{back_scroll});")
                time.sleep(random.uniform(0.5, 1.5))
    
    def scroll_pattern_reader(self):
        """Reading scrolling - steady downward movement"""
        for _ in range(random.randint(1, 3)):
            scroll_amount = random.randint(150, 300)
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
            time.sleep(random.uniform(1.5, 3.0))  # Longer pauses for reading
    
    def scroll_pattern_scanner(self):
        """Scanning scrolling - quick movements"""
        for _ in range(random.randint(3, 6)):
            scroll_amount = random.randint(100, 250)
            direction = random.choice([1, -1])
            self.driver.execute_script(f"window.scrollBy(0, {scroll_amount * direction});")
            time.sleep(random.uniform(0.3, 0.8))  # Quick scanning
    
    def simulate_hesitation_behavior(self):
        """Simulate human hesitation before contacting"""
        if self.logger:
            self.logger.info("4. 🤔 Decision hesitation (3-8 seconds pause)")
            
        hesitation_behaviors = [
            lambda: time.sleep(random.uniform(2.0, 5.0)),  # Just pause
            self.look_for_reviews,  # Check reviews
            self.check_contact_options,  # Look at contact methods
            self.reread_key_info  # Re-read important info
        ]
        
        # Execute 1-2 hesitation behaviors
        selected = random.sample(hesitation_behaviors, random.randint(1, 2))
        for behavior in selected:
            behavior()
    
    def look_for_reviews(self):
        """Look for and read reviews"""
        try:
            review_selectors = [
                '[class*="review"]', '[class*="feedback"]', 
                '[class*="rating"]', '[class*="comment"]'
            ]
            
            for selector in review_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    element = random.choice(elements[:2])
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    time.sleep(random.uniform(2.0, 4.0))
                    break
        except:
            pass
    
    def check_contact_options(self):
        """Check different contact options"""
        try:
            contact_selectors = [
                '[class*="phone"]', '[class*="call"]', 
                '[class*="whatsapp"]', '[class*="contact"]',
                '[href*="tel:"]', '[href*="whatsapp"]'
            ]
            
            for selector in contact_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    # Hover over contact options
                    for element in elements[:2]:
                        try:
                            ActionChains(self.driver).move_to_element(element).perform()
                            time.sleep(random.uniform(0.5, 1.0))
                        except:
                            continue
                    break
        except:
            pass
    
    def reread_key_info(self):
        """Re-read business name or key information"""
        try:
            key_selectors = ['h1', 'h2', '[class*="title"]', '[class*="name"]']
            
            for selector in key_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    element = elements[0]
                    self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
                    time.sleep(random.uniform(1.0, 2.5))
                    break
        except:
            pass
    
    def enhanced_whatsapp_click_sequence(self, whatsapp_buttons):
        """Execute enhanced WhatsApp clicking with full human behavior"""
        if self.logger:
            self.logger.info("🚀 Starting enhanced WhatsApp click sequence...")
        
        # Phase 1: Pre-click behavior (human research)
        self.simulate_human_research_behavior()
        
        # Phase 2: Decision-making pause
        decision_time = random.uniform(3.0, 8.0)
        if self.logger:
            self.logger.info(f"4. 🤔 Decision hesitation ({decision_time:.1f} seconds pause)")
        time.sleep(decision_time)
        
        # Phase 3: Click attempt with human characteristics
        return self.attempt_human_whatsapp_click(whatsapp_buttons)
    
    def attempt_human_whatsapp_click(self, whatsapp_buttons):
        """Attempt clicking with maximum human-like behavior"""
        for i, button in enumerate(whatsapp_buttons):
            if self.logger:
                self.logger.info(f"🖱️ Attempting human click on WhatsApp button {i+1}")
            
            try:
                # Human eye movement to button (look before click)
                self.simulate_eye_movement_to_element(button)
                
                # Human hesitation before click
                self.add_click_hesitation()
                
                # Enhanced human click
                if self.perform_enhanced_human_click(button):
                    # Post-click behavior
                    self.simulate_post_click_behavior()
                    
                    # Wait for WhatsApp to open
                    if self.wait_for_whatsapp_redirect():
                        if self.logger:
                            self.logger.info("✅ WhatsApp redirection successful!")
                        return True
                    
            except Exception as e:
                if self.logger:
                    self.logger.error(f"Click attempt {i+1} failed: {e}")
                continue
        
        return False
    
    def simulate_eye_movement_to_element(self, element):
        """Simulate human eye movement before clicking"""
        if self.logger:
            self.logger.info("5. 👁️ Eye movement to WhatsApp button")
        try:
            # Scroll element into view first
            self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
            time.sleep(random.uniform(0.5, 1.0))
            
            # Move mouse near element (peripheral vision)
            element_rect = element.rect
            near_x = element_rect['x'] + random.randint(-50, 50)
            near_y = element_rect['y'] + random.randint(-30, 30)
            
            try:
                ActionChains(self.driver).move_by_offset(near_x, near_y).perform()
                time.sleep(random.uniform(0.3, 0.8))  # Eye focusing time
            except:
                # Fallback if offset movement fails
                ActionChains(self.driver).move_to_element(element).perform()
                time.sleep(random.uniform(0.3, 0.8))
            
        except Exception as e:
            if self.logger:
                self.logger.debug(f"Eye movement simulation error: {e}")
    
    def add_click_hesitation(self):
        """Add natural hesitation before clicking"""
        hesitation_types = [
            lambda: time.sleep(random.uniform(0.5, 2.0)),  # Simple pause
            self.micro_movements,  # Small mouse movements
            self.hover_and_wait,  # Hover and consider
            self.double_check_button  # Look at button text
        ]
        
        # 70% chance of hesitation
        if random.random() < 0.7:
            selected_hesitation = random.choice(hesitation_types)
            selected_hesitation()
    
    def micro_movements(self):
        """Small mouse movements indicating consideration"""
        for _ in range(random.randint(1, 3)):
            move_x = random.randint(-15, 15)
            move_y = random.randint(-10, 10)
            try:
                ActionChains(self.driver).move_by_offset(move_x, move_y).perform()
                time.sleep(random.uniform(0.2, 0.5))
            except:
                break
    
    def hover_and_wait(self):
        """Hover over element and wait"""
        time.sleep(random.uniform(0.8, 2.0))
    
    def double_check_button(self):
        """Look at button text/icon to confirm"""
        time.sleep(random.uniform(0.5, 1.5))
    
    def perform_enhanced_human_click(self, element):
        """Perform the most human-like click possible"""
        try:
            # Get element center with human offset
            rect = element.rect
            
            # Ensure element is visible and has valid dimensions
            if rect['width'] == 0 or rect['height'] == 0:
                if self.logger:
                    self.logger.warning("Element has zero dimensions, using JavaScript click")
                return self.fallback_javascript_click(element)
            
            center_x = rect['x'] + rect['width'] // 2
            center_y = rect['y'] + rect['height'] // 2
            
            # Human offset (never click exact center)
            offset_x = random.randint(-int(rect['width']*0.3), int(rect['width']*0.3))
            offset_y = random.randint(-int(rect['height']*0.3), int(rect['height']*0.3))
            
            # Ensure offset doesn't go outside element bounds
            offset_x = max(-rect['width']//3, min(rect['width']//3, offset_x))
            offset_y = max(-rect['height']//3, min(rect['height']//3, offset_y))
            
            # Move to target with curve
            actions = ActionChains(self.driver)
            actions.move_to_element_with_offset(element, offset_x, offset_y)
            
            # Human click duration
            actions.click_and_hold(element)
            time.sleep(random.uniform(0.08, 0.15))  # Human click duration
            actions.release(element)
            
            actions.perform()
            
            # Record click attempt
            self.click_attempts.append({
                'time': time.time(),
                'offset_x': offset_x,
                'offset_y': offset_y,
                'element_type': 'whatsapp_button'
            })
            
            if self.logger:
                self.logger.info(f"6. 🖱️ Human-like click with random offset ({offset_x}, {offset_y})")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.warning(f"Enhanced click failed: {e}")
                self.logger.info("8. 🔄 Fallback methods if needed")
            return self.fallback_javascript_click(element)
    
    def fallback_javascript_click(self, element):
        """Fallback JavaScript click when normal click fails"""
        try:
            # Even JavaScript clicks can be made more human-like
            self.driver.execute_script("""
                var element = arguments[0];
                
                // Create and dispatch mouse events with human-like properties
                var events = ['mousedown', 'mouseup', 'click'];
                
                events.forEach(function(eventType, index) {
                    setTimeout(function() {
                        var rect = element.getBoundingClientRect();
                        var centerX = rect.left + rect.width/2;
                        var centerY = rect.top + rect.height/2;
                        
                        // Add human offset
                        var offsetX = (Math.random() * 10 - 5);
                        var offsetY = (Math.random() * 6 - 3);
                        
                        var event = new MouseEvent(eventType, {
                            view: window,
                            bubbles: true,
                            cancelable: true,
                            clientX: centerX + offsetX,
                            clientY: centerY + offsetY
                        });
                        element.dispatchEvent(event);
                    }, index * 20); // Small delays between events
                });
            """, element)
            
            if self.logger:
                self.logger.info("✅ JavaScript fallback click performed")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"JavaScript fallback click failed: {e}")
            return False
    
    def simulate_post_click_behavior(self):
        """Simulate behavior after clicking"""
        post_behaviors = [
            lambda: time.sleep(random.uniform(1.0, 3.0)),  # Wait and see
            self.check_for_loading,  # Look for loading indicators
            self.slight_mouse_movement,  # Small movement
            self.prepare_for_new_tab  # Prepare for tab switch
        ]
        
        # Execute 1-2 post-click behaviors
        selected = random.sample(post_behaviors, random.randint(1, 2))
        for behavior in selected:
            behavior()
    
    def check_for_loading(self):
        """Look for loading indicators"""
        try:
            loading_selectors = [
                '[class*="loading"]', '[class*="spinner"]',
                '[class*="wait"]', '[aria-label*="loading"]'
            ]
            
            for selector in loading_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    if self.logger:
                        self.logger.info("⏳ Waiting for loading to complete...")
                    time.sleep(random.uniform(1.0, 2.0))
                    break
        except:
            pass
    
    def slight_mouse_movement(self):
        """Small mouse movement after click"""
        try:
            move_x = random.randint(-20, 20)
            move_y = random.randint(-15, 15)
            ActionChains(self.driver).move_by_offset(move_x, move_y).perform()
        except:
            pass
    
    def prepare_for_new_tab(self):
        """Prepare for potential new tab opening"""
        time.sleep(random.uniform(1.0, 2.5))
    
    def wait_for_whatsapp_redirect(self, timeout=10):
        """Wait for WhatsApp redirection with human patience"""
        if self.logger:
            self.logger.info("7. ⏳ Wait for response with human patience")
        start_time = time.time()
        initial_windows = len(self.driver.window_handles)
        
        while time.time() - start_time < timeout:
            # Check for new windows
            current_windows = len(self.driver.window_handles)
            if current_windows > initial_windows:
                if self.logger:
                    self.logger.info("🎉 New window detected - WhatsApp opened!")
                return True
            
            # Check for WhatsApp URL in current tab
            try:
                current_url = self.driver.current_url.lower()
                if 'whatsapp' in current_url or 'wa.me' in current_url:
                    if self.logger:
                        self.logger.info("🎉 WhatsApp URL detected in current tab!")
                    return True
            except:
                pass
            
            # Human-like checking interval
            time.sleep(random.uniform(0.8, 1.5))
        
        if self.logger:
            self.logger.warning("⚠️ WhatsApp redirection timeout")
        return False


def integrate_enhanced_whatsapp_clicking(connector_instance):
    """Integrate enhanced clicking into existing WhatsApp connector"""
    
    def enhanced_click_whatsapp_button(self, method="enhanced_human"):
        """Replace existing WhatsApp click method with enhanced human version"""
        clicker = EnhancedWhatsAppClicker(self.driver, self.logger)
        
        self.logger.info("🎭 Using Enhanced Human-Like WhatsApp Clicking")
        
        # First enhance the buttons using existing method
        enhancement_result = self.enhance_whatsapp_buttons()
        
        # Get WhatsApp buttons using existing method
        whatsapp_buttons = self.find_whatsapp_buttons()
        
        if not whatsapp_buttons:
            self.logger.error("No WhatsApp buttons found")
            return False
        
        self.logger.info(f"Found {len(whatsapp_buttons)} WhatsApp buttons")
        
        # Execute enhanced clicking sequence
        return clicker.enhanced_whatsapp_click_sequence(whatsapp_buttons)
    
    # Replace the existing method
    connector_instance.click_whatsapp_button = enhanced_click_whatsapp_button.__get__(
        connector_instance, type(connector_instance))
    
    connector_instance.logger.info("✅ Enhanced human-like clicking integrated!")
    return connector_instance


if __name__ == "__main__":
    print("Enhanced WhatsApp Clicker for JustDial Anti-Detection")
    print("Integrates maximum human-like behavior for WhatsApp clicking")
    print("\nFeatures:")
    print("✅ Pre-click research simulation")
    print("✅ Human hesitation and decision-making")
    print("✅ Natural mouse movements and clicking")
    print("✅ Post-click behavior simulation")
    print("✅ Advanced timing variations")
    print("✅ Multiple fallback methods")
