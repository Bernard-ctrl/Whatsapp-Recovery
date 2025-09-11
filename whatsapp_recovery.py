#!/usr/bin/env python3
"""
WhatsApp Deleted Message Recovery Application

This application monitors WhatsApp Web for deleted messages and stores them
locally so you can see what messages were deleted.

Usage:
    python whatsapp_recovery.py [--headless] [--config CONFIG_FILE]

Features:
- Real-time monitoring of WhatsApp Web messages
- Automatic detection of deleted messages
- Local storage of all messages and deleted message history
- GUI interface for viewing deleted messages
- Support for both individual and group chats
- Privacy-focused: all data stored locally

Author: WhatsApp Recovery Team
License: MIT
"""

import argparse
import logging
import sys
import os
from pathlib import Path

# Add current directory to Python path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import config
from gui import WhatsAppRecoveryGUI
from whatsapp_monitor import WhatsAppMonitor
from database import MessageDatabase

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = [
        'selenium',
        'beautifulsoup4',
        'webdriver_manager',
        'tkinter'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            elif package == 'beautifulsoup4':
                import bs4
            elif package == 'webdriver_manager':
                import webdriver_manager
            else:
                __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("Error: Missing required packages:")
        for package in missing_packages:
            print(f"  - {package}")
        print("\nInstall missing packages with:")
        print("  pip install -r requirements.txt")
        return False
    
    return True

def create_directories():
    """Create necessary directories for the application"""
    directories = [
        os.path.dirname(config.DATABASE_PATH),
        config.CHROME_PROFILE_PATH,
        os.path.dirname(config.LOG_FILE)
    ]
    
    for directory in directories:
        if directory and not os.path.exists(directory):
            try:
                os.makedirs(directory, exist_ok=True)
                logging.info(f"Created directory: {directory}")
            except OSError as e:
                logging.error(f"Failed to create directory {directory}: {e}")
                return False
    
    return True

def test_database():
    """Test database connection and setup"""
    try:
        db = MessageDatabase()
        stats = db.get_statistics()
        logging.info(f"Database connection successful. Stats: {stats}")
        return True
    except Exception as e:
        logging.error(f"Database test failed: {e}")
        return False

def run_cli_mode():
    """Run in CLI mode (headless monitoring)"""
    print("Starting WhatsApp Recovery in CLI mode...")
    print("This will start monitoring in the background.")
    print("Press Ctrl+C to stop.\n")
    
    monitor = WhatsAppMonitor()
    
    try:
        if monitor.start_monitoring():
            print("Monitoring started successfully!")
        else:
            print("Failed to start monitoring. Check logs for details.")
            return False
    except KeyboardInterrupt:
        print("\nStopping monitoring...")
        monitor.stop_monitoring()
        print("Monitoring stopped.")
    except Exception as e:
        print(f"Error during monitoring: {e}")
        return False
    
    return True

def run_gui_mode():
    """Run in GUI mode"""
    try:
        app = WhatsAppRecoveryGUI()
        app.run()
        return True
    except Exception as e:
        logging.error(f"GUI mode failed: {e}")
        print(f"Error starting GUI: {e}")
        print("Try running with --cli flag for command-line mode.")
        return False

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(
        description="WhatsApp Deleted Message Recovery Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python whatsapp_recovery.py                    # Run with GUI
  python whatsapp_recovery.py --cli             # Run in CLI mode
  python whatsapp_recovery.py --headless        # Run GUI in headless mode
  python whatsapp_recovery.py --check           # Check system requirements
        """
    )
    
    parser.add_argument(
        '--cli', 
        action='store_true',
        help='Run in CLI mode without GUI'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run Chrome in headless mode (no browser window)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        help='Path to custom configuration file'
    )
    
    parser.add_argument(
        '--check',
        action='store_true',
        help='Check system requirements and exit'
    )
    
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Set logging level'
    )
    
    args = parser.parse_args()
    
    # Update config based on arguments
    if args.headless:
        config.HEADLESS_MODE = True
    
    if args.log_level:
        config.LOG_LEVEL = args.log_level
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting WhatsApp Recovery Application")
    logger.info(f"Arguments: {vars(args)}")
    
    # Check system requirements
    print("WhatsApp Deleted Message Recovery")
    print("=" * 35)
    print("Checking system requirements...")
    
    if not check_dependencies():
        return 1
    print("✓ Dependencies check passed")
    
    if not create_directories():
        print("✗ Failed to create required directories")
        return 1
    print("✓ Directory structure check passed")
    
    if not test_database():
        print("✗ Database test failed")
        return 1
    print("✓ Database check passed")
    
    if args.check:
        print("\nAll system requirements satisfied!")
        print("You can now run the application normally.")
        return 0
    
    print("✓ All checks passed\n")
    
    # Run the application
    try:
        if args.cli:
            success = run_cli_mode()
        else:
            success = run_gui_mode()
        
        if success:
            logger.info("Application completed successfully")
            return 0
        else:
            logger.error("Application failed")
            return 1
            
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
        print("\nApplication stopped by user.")
        return 0
    except Exception as e:
        logger.error(f"Unhandled exception: {e}", exc_info=True)
        print(f"Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)