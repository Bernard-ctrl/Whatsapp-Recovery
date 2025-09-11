"""
GUI application for viewing and managing deleted WhatsApp messages
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
from datetime import datetime
from typing import Dict, List
import logging
import config
from database import MessageDatabase
from whatsapp_monitor import WhatsAppMonitor

class WhatsAppRecoveryGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.db = MessageDatabase()
        self.monitor = None
        self.monitoring_thread = None
        self.is_monitoring = False
        
        self.setup_gui()
        self.refresh_data()
        
    def setup_gui(self):
        """Initialize the GUI components"""
        self.root.title(config.WINDOW_TITLE)
        self.root.geometry(f"{config.WINDOW_WIDTH}x{config.WINDOW_HEIGHT}")
        self.root.resizable(True, True)
        
        # Create main notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab 1: Deleted Messages
        self.deleted_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.deleted_tab, text="Deleted Messages")
        self.setup_deleted_messages_tab()
        
        # Tab 2: All Chats
        self.chats_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.chats_tab, text="All Chats")
        self.setup_chats_tab()
        
        # Tab 3: Monitor Control
        self.monitor_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.monitor_tab, text="Monitor Control")
        self.setup_monitor_tab()
        
        # Tab 4: Statistics
        self.stats_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.stats_tab, text="Statistics")
        self.setup_statistics_tab()
        
        # Status bar
        self.status_frame = ttk.Frame(self.root)
        self.status_frame.pack(fill='x', padx=10, pady=5)
        
        self.status_label = ttk.Label(self.status_frame, text="Ready")
        self.status_label.pack(side='left')
        
        self.refresh_button = ttk.Button(self.status_frame, text="Refresh", command=self.refresh_data)
        self.refresh_button.pack(side='right')
    
    def setup_deleted_messages_tab(self):
        """Setup the deleted messages tab"""
        # Filter frame
        filter_frame = ttk.LabelFrame(self.deleted_tab, text="Filters", padding=10)
        filter_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(filter_frame, text="Chat:").grid(row=0, column=0, sticky='w', padx=5)
        self.chat_filter = ttk.Combobox(filter_frame, width=30)
        self.chat_filter.grid(row=0, column=1, padx=5)
        self.chat_filter.bind('<<ComboboxSelected>>', self.filter_deleted_messages)
        
        ttk.Button(filter_frame, text="Show All", command=self.show_all_deleted).grid(row=0, column=2, padx=5)
        
        # Messages frame
        messages_frame = ttk.LabelFrame(self.deleted_tab, text="Deleted Messages", padding=5)
        messages_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Treeview for deleted messages
        columns = ('Time', 'Chat', 'Sender', 'Message', 'Deleted At')
        self.deleted_tree = ttk.Treeview(messages_frame, columns=columns, show='tree headings')
        
        # Configure columns
        self.deleted_tree.heading('#0', text='ID')
        self.deleted_tree.column('#0', width=50, anchor='center')
        
        for col in columns:
            self.deleted_tree.heading(col, text=col)
            if col == 'Message':
                self.deleted_tree.column(col, width=400)
            elif col in ['Time', 'Deleted At']:
                self.deleted_tree.column(col, width=120)
            else:
                self.deleted_tree.column(col, width=150)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(messages_frame, orient='vertical', command=self.deleted_tree.yview)
        h_scrollbar = ttk.Scrollbar(messages_frame, orient='horizontal', command=self.deleted_tree.xview)
        self.deleted_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.deleted_tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        messages_frame.grid_rowconfigure(0, weight=1)
        messages_frame.grid_columnconfigure(0, weight=1)
        
        # Bind double-click to show full message
        self.deleted_tree.bind('<Double-1>', self.show_full_message)
    
    def setup_chats_tab(self):
        """Setup the all chats tab"""
        # Chat selection frame
        chat_frame = ttk.LabelFrame(self.chats_tab, text="Chat Selection", padding=10)
        chat_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(chat_frame, text="Select Chat:").grid(row=0, column=0, sticky='w', padx=5)
        self.selected_chat = ttk.Combobox(chat_frame, width=40)
        self.selected_chat.grid(row=0, column=1, padx=5)
        self.selected_chat.bind('<<ComboboxSelected>>', self.load_chat_messages)
        
        # Messages display frame
        display_frame = ttk.LabelFrame(self.chats_tab, text="Messages", padding=5)
        display_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Treeview for all messages in selected chat
        chat_columns = ('Time', 'Sender', 'Message', 'Status')
        self.chat_tree = ttk.Treeview(display_frame, columns=chat_columns, show='tree headings')
        
        self.chat_tree.heading('#0', text='ID')
        self.chat_tree.column('#0', width=50, anchor='center')
        
        for col in chat_columns:
            self.chat_tree.heading(col, text=col)
            if col == 'Message':
                self.chat_tree.column(col, width=400)
            elif col == 'Time':
                self.chat_tree.column(col, width=120)
            else:
                self.chat_tree.column(col, width=100)
        
        # Scrollbars for chat tree
        chat_v_scroll = ttk.Scrollbar(display_frame, orient='vertical', command=self.chat_tree.yview)
        chat_h_scroll = ttk.Scrollbar(display_frame, orient='horizontal', command=self.chat_tree.xview)
        self.chat_tree.configure(yscrollcommand=chat_v_scroll.set, xscrollcommand=chat_h_scroll.set)
        
        self.chat_tree.grid(row=0, column=0, sticky='nsew')
        chat_v_scroll.grid(row=0, column=1, sticky='ns')
        chat_h_scroll.grid(row=1, column=0, sticky='ew')
        
        display_frame.grid_rowconfigure(0, weight=1)
        display_frame.grid_columnconfigure(0, weight=1)
    
    def setup_monitor_tab(self):
        """Setup the monitor control tab"""
        # Control frame
        control_frame = ttk.LabelFrame(self.monitor_tab, text="Monitoring Control", padding=20)
        control_frame.pack(fill='x', padx=20, pady=20)
        
        # Status display
        self.monitor_status_label = ttk.Label(control_frame, text="Monitor Status: Stopped", 
                                            font=('Arial', 12, 'bold'))
        self.monitor_status_label.pack(pady=10)
        
        # Control buttons
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(pady=10)
        
        self.start_button = ttk.Button(button_frame, text="Start Monitoring", 
                                     command=self.start_monitoring, width=15)
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="Stop Monitoring", 
                                    command=self.stop_monitoring, width=15, state='disabled')
        self.stop_button.pack(side='left', padx=5)
        
        # Instructions
        instructions_frame = ttk.LabelFrame(self.monitor_tab, text="Instructions", padding=20)
        instructions_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        instructions_text = """
Instructions for using WhatsApp Recovery:

1. Click "Start Monitoring" to begin watching for deleted messages
2. A Chrome browser window will open with WhatsApp Web
3. If not already logged in, scan the QR code with your phone
4. The app will automatically monitor your active chats
5. When messages are deleted, they will appear in the "Deleted Messages" tab
6. You can view all messages for specific chats in the "All Chats" tab

Important Notes:
- Keep the Chrome window open while monitoring
- The app monitors only your most recent active chats
- Deleted messages are stored locally on your computer
- This app respects WhatsApp's terms of service and only monitors your own messages

Privacy:
- All data is stored locally on your device
- No messages are sent to external servers
- You can stop monitoring at any time
        """
        
        self.instructions_text = scrolledtext.ScrolledText(instructions_frame, wrap=tk.WORD, 
                                                          width=70, height=15, state='disabled')
        self.instructions_text.pack(fill='both', expand=True)
        
        # Insert instructions
        self.instructions_text.config(state='normal')
        self.instructions_text.insert('1.0', instructions_text.strip())
        self.instructions_text.config(state='disabled')
    
    def setup_statistics_tab(self):
        """Setup the statistics tab"""
        stats_frame = ttk.LabelFrame(self.stats_tab, text="Database Statistics", padding=20)
        stats_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Create labels for statistics
        self.stats_labels = {}
        stats_items = [
            ('Total Messages:', 'total_messages'),
            ('Active Messages:', 'active_messages'),
            ('Deleted Messages:', 'deleted_messages'),
            ('Total Chats:', 'total_chats')
        ]
        
        for i, (label_text, key) in enumerate(stats_items):
            ttk.Label(stats_frame, text=label_text, font=('Arial', 12)).grid(
                row=i, column=0, sticky='w', pady=5, padx=10)
            
            self.stats_labels[key] = ttk.Label(stats_frame, text="0", 
                                             font=('Arial', 12, 'bold'))
            self.stats_labels[key].grid(row=i, column=1, sticky='w', pady=5, padx=20)
        
        # Refresh stats button
        ttk.Button(stats_frame, text="Refresh Statistics", 
                  command=self.refresh_statistics).grid(row=len(stats_items), column=0, 
                                                       columnspan=2, pady=20)
    
    def refresh_data(self):
        """Refresh all data in the GUI"""
        self.load_deleted_messages()
        self.load_chat_list()
        self.refresh_statistics()
        self.update_status("Data refreshed")
    
    def load_deleted_messages(self):
        """Load deleted messages into the treeview"""
        # Clear existing items
        for item in self.deleted_tree.get_children():
            self.deleted_tree.delete(item)
        
        # Get deleted messages from database
        deleted_messages = self.db.get_deleted_messages(limit=500)
        
        # Populate treeview
        for i, msg in enumerate(deleted_messages):
            timestamp = self.format_timestamp(msg['timestamp'])
            deleted_at = self.format_timestamp(msg['deleted_at'])
            
            self.deleted_tree.insert('', 'end', iid=str(i),
                                   text=str(i + 1),
                                   values=(timestamp, msg['chat_id'], msg['sender'], 
                                         self.truncate_text(msg['content'], 50), deleted_at))
        
        # Update chat filter options
        chat_ids = list(set([msg['chat_id'] for msg in deleted_messages]))
        self.chat_filter['values'] = ['All Chats'] + sorted(chat_ids)
        if not self.chat_filter.get():
            self.chat_filter.set('All Chats')
    
    def load_chat_list(self):
        """Load chat list for selection"""
        chats = self.db.get_all_chats()
        chat_options = [f"{chat['chat_id']} ({chat['total_messages']} msgs, "
                       f"{chat['deleted_messages']} deleted)" for chat in chats]
        
        self.selected_chat['values'] = chat_options
        if chat_options and not self.selected_chat.get():
            self.selected_chat.set(chat_options[0])
    
    def load_chat_messages(self, event=None):
        """Load messages for selected chat"""
        selected = self.selected_chat.get()
        if not selected:
            return
        
        # Extract chat_id from selection
        chat_id = selected.split(' (')[0]
        
        # Clear existing items
        for item in self.chat_tree.get_children():
            self.chat_tree.delete(item)
        
        # Get messages for chat
        messages = self.db.get_chat_messages(chat_id, limit=200)
        
        # Populate treeview
        for i, msg in enumerate(messages):
            timestamp = self.format_timestamp(msg['timestamp'])
            status = "DELETED" if msg['is_deleted'] else "Active"
            
            # Use different colors for deleted messages
            tags = ('deleted',) if msg['is_deleted'] else ()
            
            self.chat_tree.insert('', 'end', iid=str(i),
                                text=str(i + 1),
                                values=(timestamp, msg['sender'], 
                                      self.truncate_text(msg['content'], 60), status),
                                tags=tags)
        
        # Configure tag colors
        self.chat_tree.tag_configure('deleted', background='#ffcccc')
    
    def filter_deleted_messages(self, event=None):
        """Filter deleted messages by selected chat"""
        selected_chat = self.chat_filter.get()
        
        if selected_chat == 'All Chats':
            self.show_all_deleted()
            return
        
        # Clear and reload with filter
        for item in self.deleted_tree.get_children():
            self.deleted_tree.delete(item)
        
        deleted_messages = self.db.get_deleted_messages(chat_id=selected_chat, limit=500)
        
        for i, msg in enumerate(deleted_messages):
            timestamp = self.format_timestamp(msg['timestamp'])
            deleted_at = self.format_timestamp(msg['deleted_at'])
            
            self.deleted_tree.insert('', 'end', iid=str(i),
                                   text=str(i + 1),
                                   values=(timestamp, msg['chat_id'], msg['sender'], 
                                         self.truncate_text(msg['content'], 50), deleted_at))
    
    def show_all_deleted(self):
        """Show all deleted messages"""
        self.chat_filter.set('All Chats')
        self.load_deleted_messages()
    
    def show_full_message(self, event):
        """Show full message content in a popup"""
        selection = self.deleted_tree.selection()
        if not selection:
            return
        
        item = self.deleted_tree.item(selection[0])
        values = item['values']
        
        if len(values) >= 4:
            # Create popup window
            popup = tk.Toplevel(self.root)
            popup.title("Full Message Details")
            popup.geometry("600x400")
            
            # Message details
            details_frame = ttk.Frame(popup, padding=20)
            details_frame.pack(fill='both', expand=True)
            
            ttk.Label(details_frame, text=f"Time: {values[0]}", font=('Arial', 10, 'bold')).pack(anchor='w')
            ttk.Label(details_frame, text=f"Chat: {values[1]}", font=('Arial', 10, 'bold')).pack(anchor='w')
            ttk.Label(details_frame, text=f"Sender: {values[2]}", font=('Arial', 10, 'bold')).pack(anchor='w')
            ttk.Label(details_frame, text=f"Deleted At: {values[4]}", font=('Arial', 10, 'bold')).pack(anchor='w')
            
            ttk.Separator(details_frame, orient='horizontal').pack(fill='x', pady=10)
            
            ttk.Label(details_frame, text="Message Content:", font=('Arial', 10, 'bold')).pack(anchor='w')
            
            # Message content text widget
            text_widget = scrolledtext.ScrolledText(details_frame, wrap=tk.WORD, width=60, height=15)
            text_widget.pack(fill='both', expand=True, pady=5)
            text_widget.insert('1.0', values[3])
            text_widget.config(state='disabled')
            
            # Close button
            ttk.Button(details_frame, text="Close", command=popup.destroy).pack(pady=10)
    
    def start_monitoring(self):
        """Start the WhatsApp monitoring process"""
        if self.is_monitoring:
            return
        
        try:
            self.start_button.config(state='disabled')
            self.update_status("Starting monitoring...")
            
            # Create and start monitor in separate thread
            self.monitor = WhatsAppMonitor()
            self.monitoring_thread = threading.Thread(target=self._monitor_worker, daemon=True)
            self.monitoring_thread.start()
            
            self.is_monitoring = True
            self.stop_button.config(state='normal')
            self.monitor_status_label.config(text="Monitor Status: Running", foreground='green')
            self.update_status("Monitoring started - Check Chrome window for WhatsApp Web")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start monitoring: {str(e)}")
            self.start_button.config(state='normal')
            self.update_status(f"Error: {str(e)}")
    
    def _monitor_worker(self):
        """Worker function for monitoring thread"""
        try:
            self.monitor.start_monitoring()
        except Exception as e:
            logging.error(f"Monitoring thread error: {e}")
            # Update GUI in main thread
            self.root.after(0, self._monitoring_error, str(e))
    
    def _monitoring_error(self, error_msg):
        """Handle monitoring errors in main thread"""
        self.stop_monitoring()
        messagebox.showerror("Monitoring Error", f"Monitoring stopped due to error: {error_msg}")
    
    def stop_monitoring(self):
        """Stop the WhatsApp monitoring process"""
        if not self.is_monitoring:
            return
        
        try:
            self.update_status("Stopping monitoring...")
            
            if self.monitor:
                self.monitor.stop_monitoring()
            
            self.is_monitoring = False
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            self.monitor_status_label.config(text="Monitor Status: Stopped", foreground='red')
            self.update_status("Monitoring stopped")
            
            # Refresh data after stopping
            self.refresh_data()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error stopping monitoring: {str(e)}")
    
    def refresh_statistics(self):
        """Refresh database statistics"""
        stats = self.db.get_statistics()
        
        for key, label in self.stats_labels.items():
            value = stats.get(key, 0)
            label.config(text=str(value))
    
    def update_status(self, message: str):
        """Update status bar message"""
        self.status_label.config(text=f"{datetime.now().strftime('%H:%M:%S')} - {message}")
    
    def format_timestamp(self, timestamp_str: str) -> str:
        """Format timestamp for display"""
        try:
            if isinstance(timestamp_str, str):
                # Parse string timestamp
                dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            else:
                dt = timestamp_str
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except:
            return str(timestamp_str)
    
    def truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text for display in treeview"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    def run(self):
        """Start the GUI application"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """Handle application closing"""
        if self.is_monitoring:
            if messagebox.askokcancel("Quit", "Monitoring is active. Stop monitoring and quit?"):
                self.stop_monitoring()
                self.root.destroy()
        else:
            self.root.destroy()

if __name__ == "__main__":
    app = WhatsAppRecoveryGUI()
    app.run()