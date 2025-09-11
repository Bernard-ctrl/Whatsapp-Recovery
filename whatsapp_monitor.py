"""
WhatsApp Web monitor for detecting and storing messages
"""
import time
import re
import logging
from datetime import datetime
from typing import List, Dict, Optional, Set
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import config
from database import MessageDatabase

class WhatsAppMonitor:
    def __init__(self):
        self.db = MessageDatabase()
        self.driver = None
        self.is_running = False
        self.current_messages = {}  # Store current state of messages
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=getattr(logging, config.LOG_LEVEL),
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(config.LOG_FILE),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def setup_driver(self) -> bool:
        """Initialize Chrome WebDriver with WhatsApp Web"""
        try:
            chrome_options = Options()
            chrome_options.add_argument(f"--user-data-dir={config.CHROME_PROFILE_PATH}")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--window-size=1920,1080")
            
            if config.HEADLESS_MODE:
                chrome_options.add_argument("--headless")
            
            # Install and setup ChromeDriver
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            self.logger.info("Chrome WebDriver initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup WebDriver: {e}")
            return False
    
    def connect_to_whatsapp(self) -> bool:
        """Connect to WhatsApp Web and wait for QR code scan if needed"""
        try:
            self.driver.get(config.WHATSAPP_WEB_URL)
            self.logger.info("Navigated to WhatsApp Web")
            
            # Wait for QR code or main interface
            try:
                # Check if already logged in
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="chat-list"]'))
                )
                self.logger.info("Already logged in to WhatsApp Web")
                return True
                
            except TimeoutException:
                # QR code might be present
                try:
                    qr_code = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-ref]'))
                    )
                    self.logger.info("QR Code detected. Please scan with your phone.")
                    
                    # Wait for successful login (up to 2 minutes)
                    WebDriverWait(self.driver, 120).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, '[data-testid="chat-list"]'))
                    )
                    self.logger.info("Successfully logged in to WhatsApp Web")
                    return True
                    
                except TimeoutException:
                    self.logger.error("Timeout waiting for WhatsApp Web login")
                    return False
                    
        except Exception as e:
            self.logger.error(f"Error connecting to WhatsApp Web: {e}")
            return False
    
    def extract_chat_id(self, chat_element) -> Optional[str]:
        """Extract unique chat ID from chat element"""
        try:
            # Try to get chat ID from data attributes or href
            chat_link = chat_element.find_element(By.TAG_NAME, "a")
            href = chat_link.get_attribute("href")
            if href:
                # Extract chat ID from URL
                match = re.search(r'chat/([^/]+)', href)
                if match:
                    return match.group(1)
            
            # Fallback: use chat title as ID
            title_element = chat_element.find_element(By.CSS_SELECTOR, '[data-testid="conversation-info-header"]')
            return title_element.text.strip()
            
        except Exception as e:
            self.logger.debug(f"Error extracting chat ID: {e}")
            return None
    
    def extract_messages_from_chat(self, chat_id: str) -> List[Dict]:
        """Extract messages from currently open chat"""
        messages = []
        try:
            # Wait for messages to load
            time.sleep(2)
            
            # Get all message elements
            message_elements = self.driver.find_elements(
                By.CSS_SELECTOR, '[data-testid="conversation-panel-messages"] > div > div'
            )
            
            for msg_element in message_elements[-50:]:  # Process last 50 messages
                try:
                    message_data = self.parse_message_element(msg_element, chat_id)
                    if message_data:
                        messages.append(message_data)
                except Exception as e:
                    self.logger.debug(f"Error parsing message element: {e}")
                    continue
            
            return messages
            
        except Exception as e:
            self.logger.error(f"Error extracting messages from chat {chat_id}: {e}")
            return []
    
    def parse_message_element(self, element, chat_id: str) -> Optional[Dict]:
        """Parse individual message element"""
        try:
            # Check if message is deleted (common indicators)
            deleted_indicators = [
                "This message was deleted",
                "You deleted this message",
                "message-deleted"
            ]
            
            element_html = element.get_attribute('outerHTML')
            is_potentially_deleted = any(indicator in element_html for indicator in deleted_indicators)
            
            # Extract message text
            message_text = ""
            text_elements = element.find_elements(By.CSS_SELECTOR, '[data-testid="conversation-text"]')
            if text_elements:
                message_text = text_elements[0].text
            
            # Extract sender information
            sender = "You"  # Default for outgoing messages
            sender_elements = element.find_elements(By.CSS_SELECTOR, '[data-testid="message-author"]')
            if sender_elements:
                sender = sender_elements[0].text
            
            # Extract timestamp
            timestamp = datetime.now()
            time_elements = element.find_elements(By.CSS_SELECTOR, '[data-testid="msg-time"]')
            if time_elements:
                time_text = time_elements[0].get_attribute('title') or time_elements[0].text
                timestamp = self.parse_timestamp(time_text)
            
            # Generate message ID
            message_id = self.generate_message_id(element_html, timestamp, sender)
            
            return {
                'chat_id': chat_id,
                'message_id': message_id,
                'sender': sender,
                'content': message_text,
                'timestamp': timestamp,
                'message_type': 'text',
                'is_potentially_deleted': is_potentially_deleted
            }
            
        except Exception as e:
            self.logger.debug(f"Error parsing message element: {e}")
            return None
    
    def generate_message_id(self, element_html: str, timestamp: datetime, sender: str) -> str:
        """Generate a unique message ID"""
        # Use a combination of content hash and timestamp
        import hashlib
        content_hash = hashlib.md5(f"{element_html}{timestamp}{sender}".encode()).hexdigest()[:8]
        return f"{timestamp.strftime('%Y%m%d_%H%M%S')}_{content_hash}"
    
    def parse_timestamp(self, time_text: str) -> datetime:
        """Parse WhatsApp timestamp format"""
        try:
            # Handle different timestamp formats
            if ':' in time_text and len(time_text) <= 8:
                # Format: HH:MM or HH:MM AM/PM
                today = datetime.now().date()
                if 'AM' in time_text or 'PM' in time_text:
                    time_obj = datetime.strptime(time_text, '%I:%M %p').time()
                else:
                    time_obj = datetime.strptime(time_text, '%H:%M').time()
                return datetime.combine(today, time_obj)
            else:
                # Fallback to current time
                return datetime.now()
        except:
            return datetime.now()
    
    def scan_active_chats(self) -> List[str]:
        """Get list of active chat IDs"""
        chat_ids = []
        try:
            # Find all chat elements
            chat_elements = self.driver.find_elements(
                By.CSS_SELECTOR, '[data-testid="chat-list"] > div'
            )
            
            for chat_element in chat_elements[:10]:  # Limit to top 10 chats
                try:
                    chat_id = self.extract_chat_id(chat_element)
                    if chat_id:
                        chat_ids.append(chat_id)
                except Exception as e:
                    self.logger.debug(f"Error processing chat element: {e}")
                    continue
            
            return chat_ids
            
        except Exception as e:
            self.logger.error(f"Error scanning active chats: {e}")
            return []
    
    def click_chat(self, chat_element) -> bool:
        """Click on a chat to open it"""
        try:
            chat_element.click()
            time.sleep(1)  # Wait for chat to load
            return True
        except Exception as e:
            self.logger.debug(f"Error clicking chat: {e}")
            return False
    
    def detect_deleted_messages(self, current_messages: List[Dict], stored_messages: List[Dict]):
        """Compare current messages with stored ones to detect deletions"""
        stored_ids = {msg['message_id'] for msg in stored_messages}
        current_ids = {msg['message_id'] for msg in current_messages}
        
        # Messages that were stored but no longer present
        deleted_ids = stored_ids - current_ids
        
        for deleted_id in deleted_ids:
            # Find the original message
            original_msg = next((msg for msg in stored_messages if msg['message_id'] == deleted_id), None)
            if original_msg:
                self.db.mark_message_deleted(original_msg['chat_id'], deleted_id)
                self.logger.info(f"Detected deleted message: {deleted_id} from {original_msg['sender']}")
    
    def monitor_messages(self):
        """Main monitoring loop"""
        self.logger.info("Starting WhatsApp message monitoring...")
        
        while self.is_running:
            try:
                # Get list of active chats
                chat_elements = self.driver.find_elements(
                    By.CSS_SELECTOR, '[data-testid="chat-list"] > div'
                )
                
                for chat_element in chat_elements[:5]:  # Monitor top 5 chats
                    try:
                        # Click on chat
                        if not self.click_chat(chat_element):
                            continue
                        
                        chat_id = self.extract_chat_id(chat_element)
                        if not chat_id:
                            continue
                        
                        # Extract messages from current chat
                        current_messages = self.extract_messages_from_chat(chat_id)
                        
                        # Store new messages
                        for message in current_messages:
                            if not message.get('is_potentially_deleted'):
                                self.db.store_message(
                                    message['chat_id'],
                                    message['message_id'],
                                    message['sender'],
                                    message['content'],
                                    message['timestamp'],
                                    message['message_type']
                                )
                        
                        # Compare with stored messages to detect deletions
                        stored_messages = self.db.get_chat_messages(chat_id, 50)
                        self.detect_deleted_messages(current_messages, stored_messages)
                        
                    except Exception as e:
                        self.logger.debug(f"Error processing chat: {e}")
                        continue
                
                # Wait before next scan
                time.sleep(config.SCAN_INTERVAL)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(config.SCAN_INTERVAL * 2)  # Wait longer on error
    
    def start_monitoring(self) -> bool:
        """Start the monitoring process"""
        try:
            if not self.setup_driver():
                return False
            
            if not self.connect_to_whatsapp():
                return False
            
            self.is_running = True
            self.monitor_messages()
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting monitoring: {e}")
            return False
    
    def stop_monitoring(self):
        """Stop the monitoring process"""
        self.is_running = False
        if self.driver:
            self.driver.quit()
            self.logger.info("WhatsApp monitoring stopped")
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.stop_monitoring()