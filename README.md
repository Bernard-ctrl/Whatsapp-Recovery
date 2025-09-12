# WhatsApp Deleted Message Recovery (Flutter · Android)

Recover and view deleted WhatsApp messages by capturing notifications and storing message content locally before deletion.

> Status: MVP (Android-first). Educational purposes only. Not affiliated with WhatsApp.

## What it does

- Listens to WhatsApp notifications (sender, content, time)
- Stores messages locally on-device
- When a message is deleted in WhatsApp ("This message was deleted"), the app still shows the original content
- Simple UI to browse messages and filter to deleted-only

## How it works

1. Android Notification Listener Service monitors notifications from `com.whatsapp`.
2. On new message notifications, the app saves the sender/content/timestamp to a local Room database.
3. If a deletion notification appears (contains the text "This message was deleted"), the previously saved message is marked as deleted.
4. The Flutter UI queries the local database via a MethodChannel and shows all captured messages.

No network calls. All data stays local on your device.

## Project layout

```
Whatsapp-Recovery/
├─ INSTRUCTIONS.md                   # MVP brief
├─ README.md                         # You are here
└─ whatsapp_recovery/                # Flutter app (Android-first)
	├─ lib/main.dart                  # Flutter UI (recovered messages list)
	├─ android/app/src/main/AndroidManifest.xml
	├─ android/app/src/main/kotlin/com/example/whatsapp_recovery/
	│  ├─ MainActivity.kt             # MethodChannel to DB + settings intent
	│  ├─ AppDatabase.kt              # Room DB singleton
	│  ├─ data/MessageEntity.kt       # Room entity
	│  ├─ data/MessageDao.kt          # Room DAO
	│  └─ notifications/WhatsAppNotificationListenerService.kt
	│                                 # Notification capture + deletion detection
	└─ test/widget_test.dart          # Basic widget test for current UI
```

## Requirements

- Flutter SDK installed and on PATH
- Android toolchain (Android Studio SDK / platform tools)
- Android device or emulator with WhatsApp installed

## Run it (Windows PowerShell)

```powershell
cd .\whatsapp_recovery
flutter pub get
flutter run
```

Build a debug APK:

```powershell
cd .\whatsapp_recovery
flutter build apk --debug
```

Run tests:

```powershell
cd .\whatsapp_recovery
flutter test
```

## First-time setup in the app

1. Launch the app on your device
2. Tap the lock icon in the top-right to open “Notification access” settings
3. Enable access for this app
4. Receive a few WhatsApp messages (the app will capture them going forward)
5. If someone deletes a message, toggle the trash icon to view only deleted messages

## Permissions

- Notification Listener access (required to read WhatsApp notifications)

You can revoke this at any time in system settings. The app does not request any storage, contacts, or internet permissions.

## Limitations (MVP)

- Works only from the moment you grant notification access (cannot recover past messages)
- Based on notifications; if WhatsApp or OEM skins change the notification content/format, capture or deletion detection may be incomplete
- Group or multi-message notifications may be summarized; parsing is heuristic
- Media (images, videos, voice notes) not supported in MVP

## Privacy & Security

- All captured messages are stored locally in an on-device Room database (`whatsapp_recovery.db`) within app private storage
- No data leaves your device; no analytics or external network calls
- Uninstalling the app removes its local database

## Roadmap

- Search and filters (by sender/contact/group)
- Dedicated “Deleted” tab
- Per-contact/group enable/disable
- Optional backup/restore (local or cloud)
- Media notifications parsing (where possible)

## Legal

This project is for educational purposes. Use responsibly and respect privacy laws and all applicable Terms of Service. “WhatsApp” and any related marks are trademarks of their respective owners. This project is not affiliated with, endorsed, or sponsored by WhatsApp Inc.

## Troubleshooting

- Not seeing messages? Ensure notification access is enabled for this app
- Battery optimizations (Doze/app standby) may delay background capture; consider disabling “battery optimization” for this app on some devices
- Some custom Android ROMs/OEMs restrict notification listener behavior; results may vary

## Contributing

Issues and PRs are welcome. Please avoid including any personal message content or private data in bug reports.

## License

TBD. If you plan to distribute, add a LICENSE file and update this section.
