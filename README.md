# WhatsApp Deleted Message Recovery 📱💬

A Python-based application that helps you recover WhatsApp messages that have been deleted by the sender. When someone sends you a message and then deletes it, this app will let you see what the original message was.

## 🌟 Features

- **Real-time Monitoring**: Continuously monitors your WhatsApp Web conversations
- **Automatic Detection**: Automatically detects when messages are deleted
- **Local Storage**: All messages are stored securely on your local device
- **User-friendly GUI**: Easy-to-use graphical interface to view deleted messages
- **Chat Management**: View messages from individual chats or groups
- **Privacy-focused**: No data is sent to external servers
- **Cross-platform**: Works on Windows, macOS, and Linux

## 📋 Requirements

- Python 3.7 or higher
- Chrome/Chromium browser
- Active WhatsApp account
- Internet connection

## 🚀 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Bernard-ctrl/Whatsapp-Recovery.git
   cd Whatsapp-Recovery
   ```

2. **Install required dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify installation:**
   ```bash
   python whatsapp_recovery.py --check
   ```

## 💻 Usage

### GUI Mode (Recommended)

Start the application with the graphical interface:

```bash
python whatsapp_recovery.py
```

### CLI Mode

For command-line operation:

```bash
python whatsapp_recovery.py --cli
```

### Headless Mode

Run without showing the Chrome browser window:

```bash
python whatsapp_recovery.py --headless
```

## 📖 How It Works

1. **Launch the Application**: Run the main script to open the GUI
2. **Start Monitoring**: Click "Start Monitoring" to begin watching for deleted messages
3. **Login to WhatsApp**: A Chrome window will open with WhatsApp Web - scan the QR code if needed
4. **Automatic Detection**: The app monitors your active chats and stores messages as they arrive
5. **View Deleted Messages**: When messages are deleted, they appear in the "Deleted Messages" tab

## 🖥️ Interface Overview

### Tabs

- **Deleted Messages**: View all messages that have been deleted
- **All Chats**: Browse messages from specific chats
- **Monitor Control**: Start/stop monitoring and view instructions
- **Statistics**: View database statistics and message counts

### Features

- **Message Filtering**: Filter deleted messages by chat
- **Full Message View**: Double-click to see complete message content
- **Real-time Updates**: Automatically refreshes when new deletions are detected
- **Status Indicators**: Shows monitoring status and system messages

## ⚙️ Configuration

Edit `config.py` to customize settings:

```python
# Monitoring interval (seconds)
SCAN_INTERVAL = 5

# Message retention period (days)  
MESSAGE_RETENTION_DAYS = 30

# Maximum messages per chat to store
MAX_MESSAGES_PER_CHAT = 1000

# Chrome settings
HEADLESS_MODE = False  # Set to True for headless operation
```

## 📊 Database

The application uses SQLite to store messages locally:

- **Location**: `whatsapp_messages.db` (in application directory)
- **Tables**: `messages` (all messages), `chats` (chat information)
- **Privacy**: All data stays on your local device

## 🔒 Privacy & Security

- **Local Storage Only**: All messages are stored on your local device
- **No External Servers**: No data is transmitted to external servers
- **Secure Access**: Uses your existing WhatsApp Web session
- **Data Control**: You have full control over your data

## ⚠️ Important Notes

1. **WhatsApp Terms**: This tool respects WhatsApp's terms of service and only accesses your own messages
2. **Browser Window**: Keep the Chrome browser window open while monitoring
3. **Active Chats Only**: Monitors only your most recently active conversations
4. **Legal Use**: Use responsibly and respect others' privacy
5. **Data Retention**: Configure retention periods to manage storage space

## 🛠️ Troubleshooting

### Common Issues

**Chrome Driver Issues:**
```bash
# The app automatically downloads ChromeDriver, but if issues persist:
pip install --upgrade webdriver-manager
```

**Permission Errors:**
```bash
# Make sure you have write permissions in the application directory
chmod +w whatsapp_messages.db
```

**GUI Not Starting:**
```bash
# Try CLI mode first to test functionality:
python whatsapp_recovery.py --cli
```

**WhatsApp Login Issues:**
- Ensure you have an active internet connection
- Try refreshing WhatsApp Web manually
- Clear browser cache and restart the application

### Logs

Check `whatsapp_recovery.log` for detailed error messages and debugging information.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚖️ Legal Disclaimer

This tool is for educational and personal use only. Users are responsible for complying with WhatsApp's terms of service and applicable laws. The developers are not responsible for any misuse of this software.

## 📞 Support

If you encounter issues or have questions:

1. Check the troubleshooting section above
2. Review the logs in `whatsapp_recovery.log`
3. Open an issue on GitHub with detailed information

## 🙏 Acknowledgments

- WhatsApp for providing WhatsApp Web
- Selenium WebDriver team
- ChromeDriver team
- Python community

---

**Made with ❤️ for privacy-conscious WhatsApp users**