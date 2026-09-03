# WhatsApp Deleted Message Recovery

An Android-first Flutter application that captures WhatsApp notification previews and stores them locally so they remain available if the corresponding message is later deleted.

> This is an independent educational project. It is not affiliated with, endorsed by, or sponsored by WhatsApp Inc.

## Features

- Captures WhatsApp notification title, content, conversation, and timestamp.
- Stores captured data locally in an on-device Room database.
- Marks the latest saved message when a deletion notification is detected.
- Displays messages grouped by contact or conversation.
- Provides controls for notification access, refresh, and deleting local data.

## Requirements

- Flutter SDK with Dart 3.8.1 or later.
- Android SDK and Java 21.
- An Android device or emulator with WhatsApp installed.

## Installation

Download the latest APK from the repository's [Releases](../../releases) page and install it on an Android device. Android may require permission to install applications from the browser or file manager used to download the APK.

## Run locally

From the repository root:

```powershell
flutter pub get
flutter run
```

Build a debug APK:

```powershell
flutter build apk --debug
```

Run tests:

```powershell
flutter test
```

## Initial setup

1. Install and launch the application.
2. Select the lock icon to open Android Notification Access settings.
3. Enable access for WhatsApp Recovery.
4. Receive WhatsApp messages after access has been enabled.
5. Open the application to view captured messages.

## Privacy and security

Captured notification data is stored in the application's private local storage. The application does not send captured messages to a server and does not require contacts or general storage access.

Notification Listener access is sensitive. Grant it only on devices where you are authorized to monitor notifications, and comply with applicable privacy laws and WhatsApp's terms.

## Limitations

- Recovery begins only after Notification Listener access is enabled.
- Recovery depends on notification content provided by WhatsApp and the device manufacturer.
- Group summaries, media, disabled previews, and some OEM restrictions may prevent recovery.
- This application cannot access WhatsApp's internal database or bypass encryption.

## Development and contribution

To build the project locally, follow the [Run locally](#run-locally) instructions. Contributions and bug reports are welcome.

Do not include real message content, screenshots, databases, keystores, or credentials in issues and pull requests.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE).
