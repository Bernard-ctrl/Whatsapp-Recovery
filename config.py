"""
Configuration settings for WhatsApp Recovery application
"""
import os

# Database settings
DATABASE_NAME = "whatsapp_messages.db"
DATABASE_PATH = os.path.join(os.path.dirname(__file__), DATABASE_NAME)

# WhatsApp Web settings
WHATSAPP_WEB_URL = "https://web.whatsapp.com"
SCAN_INTERVAL = 5  # seconds between message scans
MAX_RETRIES = 3

# Chrome driver settings
CHROME_PROFILE_PATH = os.path.join(os.path.dirname(__file__), "whatsapp_session")
HEADLESS_MODE = False  # Set to True to run without GUI

# GUI settings
WINDOW_TITLE = "WhatsApp Deleted Message Recovery"
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600

# Message settings
MAX_MESSAGES_PER_CHAT = 1000  # Limit to prevent database from growing too large
MESSAGE_RETENTION_DAYS = 30  # Keep deleted messages for 30 days

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "whatsapp_recovery.log"