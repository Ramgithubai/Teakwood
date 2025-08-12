#!/usr/bin/env python3
"""
Human-like Mouse Control for JustDial WhatsApp Interaction
Mimics realistic human clicking patterns to avoid detection
"""

import time
import random
import math
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.common.exceptions import ElementNotInteractableException

class HumanMouseController:
    def __init__(self, driver, logger=None):
        self.driver = driver
        self.logger = logger
        self.last_mouse_position = (0, 0)
        
    def human_mouse_move_to_element(self, element, duration=None):
        """Move mouse to element with human-like curved path"""
        if duration is None:
            duration = random.uniform(0.8, 2.5)  # Human-like timing
            
        try:
            # Get element position
            element_rect = element.rect
            target_x = element_rect['x'] + element_rect['width'] // 2
            target_y = element_rect['y'] + element_rect['height'] // 2
            
            # Add random offset to avoid clicking exact center every time
            offset_x = random.randint(-15, 15)
            offset_y = random.randint(-10, 10)
            target_x += offset_x
            target_y += offset_y
            
            # Get current mouse position (or start from random position)
            start_x, start_y = self.last_mouse_position
            if start_x == 0 and start_y == 0:
                start_x = random.randint(100, 400)
                start_y = random.randint(100, 300)
            
            # Create curved path to target
            steps = max(10, int(duration * 15))  # More steps for smoother movement
            path_points = self.generate_curved_path(start_x, start_y, target_x, target_y, steps)
            
            # Execute movement
            actions = ActionChains(self.driver)
            
            for i, (x, y) in enumerate(path_points):
                # Add slight randomness to each point
                x += random.uniform(-2, 2)
                y += random.uniform(-2, 2)
                
                if i == 0:
                    actions.move_by_offset(x - start_x, y - start_y)
                else:
                    prev_x, prev_y = path_points[i-1]
                    actions.move_by_offset(x - prev_x, y - prev_y)
                
                # Vary speed - slower at beginning and end, faster in middle
                if i < len(path_points) * 0.3 or i > len(path_points) * 0.7:
                    actions.pause(duration / steps * 1.5)  # Slower
                else:
                    actions.pause(duration / steps * 0.8)  # Faster
            
            actions.perform()
            self.last_mouse_position = (target_x, target_y)
            
            if self.logger:
                self.logger.info(f"Mouse moved to element with human-like curve ({duration:.2f}s)")
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error in human mouse movement: {e}")
            return False
    
    def generate_curved_path(self, start_x, start_y, end_x, end_y, steps):
        """Generate a curved path between two points (like human mouse movement)"""
        path_points = []
        
        # Add control points for bezier curve
        distance = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
        
        # Create control points for a natural curve
        mid_x = (start_x + end_x) / 2
        mid_y = (start_y + end_y) / 2
        
        # Add curvature (perpendicular to the direct line)
        curve_intensity = min(distance * 0.2, 50)  # Limit curve for short distances
        angle = math.atan2(end_y - start_y, end_x - start_x) + math.pi/2
        
        control_x = mid_x + math.cos(angle) * curve_intensity * random.uniform(-1, 1)
        control_y = mid_y + math.sin(angle) * curve_intensity * random.uniform(-1, 1)
        
        # Generate points along the curve
        for i in range(steps + 1):
            t = i / steps
            
            # Quadratic bezier curve
            x = (1-t)**2 * start_x + 2*(1-t)*t * control_x + t**2 * end_x
            y = (1-t)**2 * start_y + 2*(1-t)*t * control_y + t**2 * end_y
            
            path_points.append((x, y))
        
        return path_points
    
    def human_click_element(self, element, click_type="single"):
        """Perform human-like click on element"""
        try:
            # Pre-click behaviors
            self.pre_click_behavior(element)
            
            # Move to element with human timing
            if not self.human_mouse_move_to_element(element):
                return False
            
            # Pause before clicking (human reaction time)
            self.human_pause_before_click()
            
            # Perform the click
            success = self.execute_human_click(element, click_type)
            
            # Post-click behaviors
            self.post_click_behavior()
            
            return success
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error in human click: {e}")
            return False
    
    def pre_click_behavior(self, element):
        """Behaviors humans do before clicking"""
        # Sometimes hover over nearby elements first (exploration behavior)
        if random.random() < 0.3:  # 30% chance
            self.explore_nearby_elements(element)
        
        # Sometimes scroll element into better view
        if random.random() < 0.4:  # 40% chance
            self.human_scroll_to_element(element)
    
    def explore_nearby_elements(self, target_element):
        """Briefly hover over nearby elements (human exploration)"""
        try:
            # Find nearby clickable elements
            nearby_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                "button, a, [onclick], [role='button'], .clickable")
            
            if nearby_elements:
                # Pick 1-2 random nearby elements
                explore_count = random.randint(1, min(2, len(nearby_elements)))
                explore_elements = random.sample(nearby_elements, explore_count)
                
                for elem in explore_elements:
                    try:
                        if elem != target_element and elem.is_displayed():
                            # Quick hover
                            ActionChains(self.driver).move_to_element(elem).perform()
                            time.sleep(random.uniform(0.1, 0.3))
                    except:
                        continue
                        
        except Exception as e:
            if self.logger:
                self.logger.debug(f"Error in exploration behavior: {e}")
    
    def human_scroll_to_element(self, element):
        """Scroll to element with human-like behavior"""
        try:
            # Scroll with some overshoot and correction (human behavior)
            self.driver.execute_script("""
                var element = arguments[0];
                var elementTop = element.offsetTop;
                var elementHeight = element.offsetHeight;
                var windowHeight = window.innerHeight;
                
                // Calculate target position with some randomness
                var targetTop = elementTop - (windowHeight / 2) + (elementHeight / 2);
                var overshoot = Math.random() * 100 - 50; // Random overshoot
                
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
            
            time.sleep(random.uniform(0.5, 1.0))
            
        except Exception as e:
            if self.logger:
                self.logger.debug(f"Error in human scrolling: {e}")
    
    def human_pause_before_click(self):
        """Human reaction time pause before clicking"""
        # Human reaction time varies
        reaction_time = random.uniform(0.1, 0.4)  # 100-400ms is typical
        
        # Sometimes humans pause longer (reading, deciding)
        if random.random() < 0.2:  # 20% chance of longer pause
            reaction_time += random.uniform(0.3, 1.0)
        
        time.sleep(reaction_time)
    
    def execute_human_click(self, element, click_type="single"):
        """Execute the actual click with human characteristics"""
        try:
            actions = ActionChains(self.driver)
            
            if click_type == "double":
                # Double click with human timing
                actions.click(element)
                time.sleep(random.uniform(0.05, 0.15))  # Human double-click timing
                actions.click(element)
            else:
                # Single click with human press duration
                actions.click_and_hold(element)
                time.sleep(random.uniform(0.05, 0.12))  # Human click duration
                actions.release(element)
            
            actions.perform()
            
            if self.logger:
                self.logger.info(f"Executed human-like {click_type} click")
            
            return True
            
        except ElementNotInteractableException:
            # Try JavaScript click as fallback
            if self.logger:
                self.logger.info("Element not interactable, trying JavaScript click")
            return self.fallback_javascript_click(element)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error in click execution: {e}")
            return False
    
    def fallback_javascript_click(self, element):
        """Fallback JavaScript click when normal click fails"""
        try:
            # Even JavaScript clicks can be made more human-like
            self.driver.execute_script("""
                var element = arguments[0];
                
                // Create and dispatch mouse events
                var events = ['mousedown', 'mouseup', 'click'];
                
                events.forEach(function(eventType, index) {
                    setTimeout(function() {
                        var event = new MouseEvent(eventType, {
                            view: window,
                            bubbles: true,
                            cancelable: true,
                            clientX: element.getBoundingClientRect().left + element.offsetWidth/2 + (Math.random() * 10 - 5),
                            clientY: element.getBoundingClientRect().top + element.offsetHeight/2 + (Math.random() * 6 - 3)
                        });
                        element.dispatchEvent(event);
                    }, index * 20); // Small delays between events
                });
            """, element)
            
            return True
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error in JavaScript fallback click: {e}")
            return False
    
    def post_click_behavior(self):
        """Behaviors humans do after clicking"""
        # Brief pause after clicking (human processing time)
        time.sleep(random.uniform(0.2, 0.6))
        
        # Sometimes move mouse slightly after clicking
        if random.random() < 0.4:  # 40% chance
            actions = ActionChains(self.driver)
            actions.move_by_offset(
                random.randint(-20, 20), 
                random.randint(-15, 15)
            )
            actions.perform()
    
    def human_type_text(self, element, text):
        """Type text with human-like patterns"""
        try:
            element.clear()
            time.sleep(random.uniform(0.1, 0.3))
            
            for char in text:
                element.send_keys(char)
                
                # Vary typing speed
                if char == ' ':
                    typing_delay = random.uniform(0.1, 0.3)  # Longer pause at spaces
                else:
                    typing_delay = random.uniform(0.05, 0.15)  # Normal typing
                
                # Occasional typos and corrections (very advanced)
                if random.random() < 0.02:  # 2% chance of typo
                    wrong_char = random.choice('abcdefghijklmnopqrstuvwxyz')
                    element.send_keys(wrong_char)
                    time.sleep(random.uniform(0.2, 0.5))  # Realize mistake
                    element.send_keys('\b')  # Backspace
                    time.sleep(random.uniform(0.1, 0.3))
                
                time.sleep(typing_delay)
                
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error in human typing: {e}")


def enhance_whatsapp_clicking_with_human_behavior(justdial_researcher_instance):
    """Enhance the JustDial researcher with human-like WhatsApp clicking"""
    
    def human_click_whatsapp_button(self):
        """Enhanced WhatsApp button clicking with human behavior"""
        self.logger.info("Attempting human-like WhatsApp button clicking...")
        
        # Initialize human mouse controller
        mouse_controller = HumanMouseController(self.driver, self.logger)
        
        # First enhance the buttons (existing functionality)
        enhancement_result = self.enhance_whatsapp_buttons()
        
        # Find WhatsApp buttons
        whatsapp_buttons = self.find_whatsapp_buttons()
        
        if not whatsapp_buttons:
            self.logger.error("No WhatsApp buttons found")
            return False
            
        self.logger.info(f"Found {len(whatsapp_buttons)} WhatsApp buttons")
        
        # Store initial window count
        initial_windows = len(self.driver.window_handles)
        
        # Try human-like clicking on each button
        for i, button in enumerate(whatsapp_buttons):
            self.logger.info(f"Trying human click on button {i+1}/{len(whatsapp_buttons)}")
            
            try:
                # Check if button is visible and clickable
                if not button.is_displayed() or not button.is_enabled():
                    continue
                
                # Human-like pre-click behavior
                self.add_human_reading_pause()
                
                # Perform human-like click
                if mouse_controller.human_click_element(button, "single"):
                    self.logger.info(f"Human-like click successful on button {i+1}")
                    
                    # Wait for response with human patience
                    self.wait_for_response_with_human_patience()
                    
                    # Check if new window opened
                    current_windows = len(self.driver.window_handles)
                    if current_windows > initial_windows:
                        self.logger.info("WhatsApp window opened successfully")
                        return True
                    
                else:
                    self.logger.warning(f"Human click failed on button {i+1}, trying next")
                    continue
                    
            except Exception as e:
                self.logger.error(f"Error with human click on button {i+1}: {e}")
                continue
        
        self.logger.error("All human-like click attempts failed")
        return False
    
    def add_human_reading_pause(self):
        """Add realistic pause as if human is reading the page"""
        reading_time = random.uniform(1.0, 3.0)  # 1-3 seconds to "read"
        self.logger.info(f"Adding human reading pause: {reading_time:.1f}s")
        time.sleep(reading_time)
    
    def wait_for_response_with_human_patience(self):
        """Wait for page response with human-like patience"""
        # Humans wait a bit longer and check multiple times
        patience_time = random.uniform(3.0, 6.0)
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
    
    # Replace the existing method with human version
    justdial_researcher_instance.click_first_whatsapp_button = human_click_whatsapp_button.__get__(
        justdial_researcher_instance, type(justdial_researcher_instance))
    
    justdial_researcher_instance.add_human_reading_pause = add_human_reading_pause.__get__(
        justdial_researcher_instance, type(justdial_researcher_instance))
    
    justdial_researcher_instance.wait_for_response_with_human_patience = wait_for_response_with_human_patience.__get__(
        justdial_researcher_instance, type(justdial_researcher_instance))


if __name__ == "__main__":
    print("Human-like mouse controller module ready!")
    print("Use enhance_whatsapp_clicking_with_human_behavior(researcher) to enable human clicking")
