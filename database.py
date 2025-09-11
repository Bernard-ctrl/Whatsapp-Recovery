"""
Database operations for WhatsApp message storage and retrieval
"""
import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import logging
import config

class MessageDatabase:
    def __init__(self):
        self.db_path = config.DATABASE_PATH
        self.setup_database()
        
    def setup_database(self):
        """Initialize the database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Messages table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS messages (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        chat_id TEXT NOT NULL,
                        message_id TEXT NOT NULL,
                        sender TEXT,
                        content TEXT,
                        timestamp DATETIME,
                        message_type TEXT DEFAULT 'text',
                        is_deleted BOOLEAN DEFAULT FALSE,
                        deleted_at DATETIME,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(chat_id, message_id)
                    )
                ''')
                
                # Chats table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS chats (
                        chat_id TEXT PRIMARY KEY,
                        chat_name TEXT,
                        chat_type TEXT DEFAULT 'individual',
                        last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Create indexes for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_chat_timestamp ON messages(chat_id, timestamp)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_deleted ON messages(is_deleted)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_message_id ON messages(chat_id, message_id)')
                
                conn.commit()
                logging.info("Database initialized successfully")
                
        except sqlite3.Error as e:
            logging.error(f"Database setup error: {e}")
            raise
    
    def store_message(self, chat_id: str, message_id: str, sender: str, 
                     content: str, timestamp: datetime, message_type: str = 'text') -> bool:
        """Store a new message or update existing one"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Insert or replace message
                cursor.execute('''
                    INSERT OR REPLACE INTO messages 
                    (chat_id, message_id, sender, content, timestamp, message_type)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (chat_id, message_id, sender, content, timestamp, message_type))
                
                # Update chat info
                cursor.execute('''
                    INSERT OR REPLACE INTO chats (chat_id, last_updated)
                    VALUES (?, ?)
                ''', (chat_id, datetime.now()))
                
                conn.commit()
                return True
                
        except sqlite3.Error as e:
            logging.error(f"Error storing message: {e}")
            return False
    
    def mark_message_deleted(self, chat_id: str, message_id: str) -> bool:
        """Mark a message as deleted"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE messages 
                    SET is_deleted = TRUE, deleted_at = ?
                    WHERE chat_id = ? AND message_id = ?
                ''', (datetime.now(), chat_id, message_id))
                
                conn.commit()
                return cursor.rowcount > 0
                
        except sqlite3.Error as e:
            logging.error(f"Error marking message as deleted: {e}")
            return False
    
    def get_deleted_messages(self, chat_id: Optional[str] = None, 
                           limit: int = 100) -> List[Dict]:
        """Retrieve deleted messages"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                if chat_id:
                    cursor.execute('''
                        SELECT chat_id, message_id, sender, content, timestamp, 
                               message_type, deleted_at
                        FROM messages 
                        WHERE is_deleted = TRUE AND chat_id = ?
                        ORDER BY deleted_at DESC
                        LIMIT ?
                    ''', (chat_id, limit))
                else:
                    cursor.execute('''
                        SELECT chat_id, message_id, sender, content, timestamp, 
                               message_type, deleted_at
                        FROM messages 
                        WHERE is_deleted = TRUE
                        ORDER BY deleted_at DESC
                        LIMIT ?
                    ''', (limit,))
                
                columns = ['chat_id', 'message_id', 'sender', 'content', 
                          'timestamp', 'message_type', 'deleted_at']
                
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            logging.error(f"Error retrieving deleted messages: {e}")
            return []
    
    def get_chat_messages(self, chat_id: str, limit: int = 100) -> List[Dict]:
        """Get all messages for a specific chat"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT message_id, sender, content, timestamp, message_type, is_deleted
                    FROM messages 
                    WHERE chat_id = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (chat_id, limit))
                
                columns = ['message_id', 'sender', 'content', 'timestamp', 
                          'message_type', 'is_deleted']
                
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            logging.error(f"Error retrieving chat messages: {e}")
            return []
    
    def get_all_chats(self) -> List[Dict]:
        """Get all chats with message counts"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT c.chat_id, c.chat_name, c.chat_type,
                           COUNT(m.id) as total_messages,
                           SUM(CASE WHEN m.is_deleted THEN 1 ELSE 0 END) as deleted_messages,
                           MAX(m.timestamp) as last_message_time
                    FROM chats c
                    LEFT JOIN messages m ON c.chat_id = m.chat_id
                    GROUP BY c.chat_id, c.chat_name, c.chat_type
                    ORDER BY last_message_time DESC
                ''')
                
                columns = ['chat_id', 'chat_name', 'chat_type', 'total_messages', 
                          'deleted_messages', 'last_message_time']
                
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
                
        except sqlite3.Error as e:
            logging.error(f"Error retrieving chats: {e}")
            return []
    
    def cleanup_old_messages(self):
        """Remove messages older than retention period"""
        try:
            cutoff_date = datetime.now() - timedelta(days=config.MESSAGE_RETENTION_DAYS)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    DELETE FROM messages 
                    WHERE timestamp < ? AND is_deleted = FALSE
                ''', (cutoff_date,))
                
                deleted_count = cursor.rowcount
                conn.commit()
                
                if deleted_count > 0:
                    logging.info(f"Cleaned up {deleted_count} old messages")
                
        except sqlite3.Error as e:
            logging.error(f"Error during cleanup: {e}")
    
    def get_statistics(self) -> Dict:
        """Get database statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total messages
                cursor.execute('SELECT COUNT(*) FROM messages')
                total_messages = cursor.fetchone()[0]
                
                # Deleted messages
                cursor.execute('SELECT COUNT(*) FROM messages WHERE is_deleted = TRUE')
                deleted_messages = cursor.fetchone()[0]
                
                # Total chats
                cursor.execute('SELECT COUNT(*) FROM chats')
                total_chats = cursor.fetchone()[0]
                
                return {
                    'total_messages': total_messages,
                    'deleted_messages': deleted_messages,
                    'active_messages': total_messages - deleted_messages,
                    'total_chats': total_chats
                }
                
        except sqlite3.Error as e:
            logging.error(f"Error getting statistics: {e}")
            return {}