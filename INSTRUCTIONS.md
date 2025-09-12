MVP Description for WhatsApp Deleted Message Recovery App
1. Problem Statement

When someone deletes a WhatsApp message ("This message was deleted"), users often feel curious about what was sent. Currently, WhatsApp does not allow viewing deleted messages.

Our app solves this by recovering and displaying deleted WhatsApp messages.

2. Core MVP Goal

Enable users to view deleted WhatsApp messages (both personal and group chats) by capturing incoming notifications and storing message content before deletion.

3. MVP Features
Must-Have (Core MVP)

Notification Listener Service

Capture WhatsApp notifications (message text, sender, time).

Store them locally before they are deleted.

Deleted Message Detection

When WhatsApp replaces a notification with "This message was deleted", show the original message stored.

Basic UI (Flutter)

Simple home screen with a list of conversations.

Show sender, timestamp, and recovered deleted messages.

Local Database

Use sqflite or hive for storing captured messages.

Should-Have (Next Iteration)

Search & filter recovered messages.

Separate section/tab showing only "Deleted Messages".

Option to enable/disable recovery per contact/group.

Could-Have (Future Expansion)

Cloud backup & restore of recovered messages.

Support for media recovery (images, videos, voice notes).

Notification alert when someone deletes a message.

Won’t-Have (for MVP)

End-to-end encryption bypass (not possible).

Reading directly from WhatsApp’s internal database (restricted).

4. MVP Architecture

Frontend: Flutter (cross-platform, Android first).

Backend/Logic:

Notification Listener → parse WhatsApp message content.

Local database (Hive / SQLite) → store all notifications.

Recovery Engine → checks if message was deleted, then shows saved version.

5. MVP User Flow

User installs and gives notification access permission.

App listens for all WhatsApp notifications.

A new message arrives → app saves it locally.

If sender deletes it → WhatsApp shows "This message was deleted", but app still shows original.

User opens app → views recovered messages in a clean UI.