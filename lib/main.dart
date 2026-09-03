// ignore_for_file: deprecated_member_use

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:intl/intl.dart';

void main() {
  runApp(const App());
}

class App extends StatelessWidget {
  const App({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'WhatsApp Recovery',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.green),
      ),
      home: const HomeScreen(),
    );
  }
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  static const _channel = MethodChannel(
    'com.example.whatsapp_recovery/notifications',
  );
  List<Map<String, dynamic>> _messages = [];
  bool _loading = false;
  String? _selectedChatId;

  @override
  void initState() {
    super.initState();
    _refresh();
  }

  Future<void> _openAccess() async {
    try {
      await _channel.invokeMethod('openNotificationAccess');
    } catch (_) {}
  }

  Future<void> _refresh() async {
    if (!mounted) return;
    setState(() => _loading = true);
    try {
      final result = await _channel.invokeMethod<List<dynamic>>('getMessages');
      final res = result ?? const <dynamic>[];
      final messages = res
          .cast<Map>()
          .map((e) => e.map((k, v) => MapEntry(k.toString(), v)))
          .toList();
      if (mounted) {
        final chatIds = _buildSections(messages).map((section) => section.id).toSet();
        setState(() {
          _messages = messages;
          if (_selectedChatId != null && !chatIds.contains(_selectedChatId)) {
            _selectedChatId = null;
          }
        });
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Could not load recovered messages')),
        );
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  Future<void> _deleteAll() async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete All Messages'),
        content: const Text(
          'Are you sure you want to delete all recovered messages? This action cannot be undone.',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            style: TextButton.styleFrom(
              foregroundColor: Theme.of(context).colorScheme.error,
            ),
            child: const Text('Delete All'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      try {
        await _channel.invokeMethod('deleteAllMessages');
        if (!mounted) return;
        setState(() {
          _messages = [];
          _selectedChatId = null;
        });
        if (mounted) {
          ScaffoldMessenger.of(
            context,
          ).showSnackBar(const SnackBar(content: Text('All messages deleted')));
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Failed to delete messages')),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final sections = _buildSections(_messages);
    final chatOptions = sections.map((s) => MapEntry(s.id, s.title)).toList()
      ..sort((a, b) => a.value.compareTo(b.value));
    final visibleSections = _selectedChatId == null
        ? <_ChatSection>[]
        : sections.where((s) => s.id == _selectedChatId).toList();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Recovered Messages'),
        actions: [
          IconButton(
            tooltip: 'Open Notification Access',
            onPressed: _openAccess,
            icon: const Icon(Icons.lock_open),
          ),
          IconButton(
            tooltip: 'Refresh',
            onPressed: _refresh,
            icon: const Icon(Icons.refresh),
          ),
          IconButton(
            tooltip: 'Delete All Messages',
            onPressed: _messages.isEmpty ? null : _deleteAll,
            icon: const Icon(Icons.delete_forever),
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : sections.isEmpty
          ? Center(
              child: Padding(
                padding: const EdgeInsets.all(24.0),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(Icons.chat, size: 56, color: Colors.green.shade400),
                    const SizedBox(height: 12),
                    const Text(
                      'No messages yet. Enable notification access to start capturing.',
                    ),
                  ],
                ),
              ),
            )
          : RefreshIndicator(
              onRefresh: _refresh,
              child: ListView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.fromLTRB(16, 16, 16, 32),
                children: [
                  _SelectorCard(
                    chats: chatOptions,
                    selectedChatId: _selectedChatId,
                    onChatChanged: (value) =>
                        setState(() => _selectedChatId = value),
                    totalMessages: _messages.length,
                  ),
                  if (_selectedChatId == null)
                    const _EmptyHint(
                      title: 'Pick a chat',
                      subtitle:
                          'Choose whose messages you want to inspect. The list stays hidden until you select a contact.',
                    )
                  else if (visibleSections.isEmpty)
                    _EmptyHint(
                      title: 'No messages for this chat',
                      subtitle:
                          'Try switching the filter or refreshing to capture new messages.',
                    )
                  else
                    ...visibleSections.map(
                      (section) => _SectionCard(section: section),
                    ),
                ],
              ),
            ),
    );
  }

  List<_ChatSection> _buildSections(List<Map<String, dynamic>> source) {
    if (source.isEmpty) return const [];
    final sortedByTime = [...source]
      ..sort((a, b) {
        final aTs = a['timestamp'] is int ? a['timestamp'] as int : 0;
        final bTs = b['timestamp'] is int ? b['timestamp'] as int : 0;
        return bTs.compareTo(aTs);
      });

    final grouped = <String, List<Map<String, dynamic>>>{};
    for (final msg in sortedByTime) {
      final key = _chatKey(msg);
      grouped.putIfAbsent(key, () => []).add(msg);
    }

    final sections = grouped.entries.map((entry) {
      final latestTs = entry.value.first['timestamp'] is int
          ? entry.value.first['timestamp'] as int
          : 0;
      return _ChatSection(
        id: entry.key,
        title: _chatTitle(entry.value),
        latestTimestamp: latestTs,
        messages: entry.value,
      );
    }).toList();

    sections.sort((a, b) => b.latestTimestamp.compareTo(a.latestTimestamp));
    return sections;
  }

  String _chatKey(Map<String, dynamic> msg) {
    final conv = msg['conversationId']?.toString().trim();
    if (conv != null && conv.isNotEmpty) return 'conv:$conv';
    final sender = _safeSender(msg['sender']);
    return 'sender:$sender';
  }

  String _chatTitle(List<Map<String, dynamic>> messages) {
    for (final msg in messages) {
      final conv = msg['conversationId']?.toString().trim();
      if (conv != null && conv.isNotEmpty) return conv;
    }
    for (final msg in messages) {
      final sender = _safeSender(msg['sender']);
      if (sender != 'Unknown') return sender;
    }
    return 'Unknown chat';
  }

  String _safeSender(dynamic sender) {
    final trimmed = sender?.toString().trim();
    return (trimmed == null || trimmed.isEmpty) ? 'Unknown' : trimmed;
  }
}

class _ChatSection {
  const _ChatSection({
    required this.id,
    required this.title,
    required this.latestTimestamp,
    required this.messages,
  });
  final String id;
  final String title;
  final int latestTimestamp;
  final List<Map<String, dynamic>> messages;
}

class _SelectorCard extends StatelessWidget {
  const _SelectorCard({
    required this.chats,
    required this.selectedChatId,
    required this.onChatChanged,
    required this.totalMessages,
  });
  final List<MapEntry<String, String>> chats;
  final String? selectedChatId;
  final ValueChanged<String?> onChatChanged;
  final int totalMessages;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final hasChats = chats.isNotEmpty;
    final chatIds = chats.map((e) => e.key).toSet();
    final effectiveValue = hasChats && chatIds.contains(selectedChatId)
        ? selectedChatId
        : null;

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      elevation: 3,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(10),
                  decoration: BoxDecoration(
                    color: theme.colorScheme.primaryContainer,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Icon(
                    Icons.search,
                    color: theme.colorScheme.onPrimaryContainer,
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        'Choose whose messages to view',
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        hasChats
                            ? 'Select a contact to reveal their recovered messages.'
                            : 'No contacts yet. Pull to refresh after enabling access.',
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: theme.colorScheme.onSurfaceVariant,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              value: effectiveValue,
              isExpanded: true,
              decoration: InputDecoration(
                labelText: 'Select contact',
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                contentPadding: const EdgeInsets.symmetric(
                  horizontal: 12,
                  vertical: 12,
                ),
              ),
              items: chats
                  .map(
                    (entry) => DropdownMenuItem<String>(
                      value: entry.key,
                      child: Text(entry.value, overflow: TextOverflow.ellipsis),
                    ),
                  )
                  .toList(),
              onChanged: hasChats ? onChatChanged : null,
              hint: const Text('Tap to choose'),
              icon: const Icon(Icons.keyboard_arrow_down),
            ),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                _StatPill(
                  label: 'Total',
                  value: totalMessages.toString(),
                  color: theme.colorScheme.primary,
                ),
                TextButton.icon(
                  onPressed: selectedChatId == null
                      ? null
                      : () => onChatChanged(null),
                  icon: const Icon(Icons.clear),
                  label: const Text('Reset'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _StatPill extends StatelessWidget {
  const _StatPill({
    required this.label,
    required this.value,
    required this.color,
  });
  final String label;
  final String value;
  final Color color;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: color.withOpacity(0.12),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        children: [
          Container(
            width: 10,
            height: 10,
            decoration: BoxDecoration(color: color, shape: BoxShape.circle),
          ),
          const SizedBox(width: 6),
          Text(label, style: theme.textTheme.labelMedium),
          const SizedBox(width: 6),
          Text(
            value,
            style: theme.textTheme.labelMedium?.copyWith(
              fontWeight: FontWeight.bold,
            ),
          ),
        ],
      ),
    );
  }
}

class _EmptyHint extends StatelessWidget {
  const _EmptyHint({required this.title, required this.subtitle});
  final String title;
  final String subtitle;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.only(top: 12),
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: theme.colorScheme.surfaceVariant.withOpacity(.4),
          borderRadius: BorderRadius.circular(12),
        ),
        child: Row(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Icon(Icons.lightbulb, color: theme.colorScheme.primary),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    title,
                    style: theme.textTheme.titleSmall?.copyWith(
                      fontWeight: FontWeight.w700,
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    subtitle,
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: theme.colorScheme.onSurfaceVariant,
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SectionCard extends StatelessWidget {
  const _SectionCard({required this.section});
  final _ChatSection section;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final titleStyle = theme.textTheme.titleMedium?.copyWith(
      fontWeight: FontWeight.w600,
    );
    final metaStyle = theme.textTheme.bodySmall?.copyWith(
      color: theme.colorScheme.onSurfaceVariant,
    );

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      elevation: 2,
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                CircleAvatar(
                  radius: 22,
                  backgroundColor: theme.colorScheme.primaryContainer,
                  child: Text(section.title.characters.first.toUpperCase()),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(section.title, style: titleStyle),
                      Text(
                        '${section.messages.length} message${section.messages.length == 1 ? '' : 's'}',
                        style: metaStyle,
                      ),
                    ],
                  ),
                ),
                Text(
                  _formatTimestamp(section.latestTimestamp),
                  style: metaStyle,
                ),
              ],
            ),
            const SizedBox(height: 12),
            ...section.messages.map((msg) => _MessageTile(message: msg)),
          ],
        ),
      ),
    );
  }

  String _formatTimestamp(int? millis) {
    if (millis == null || millis <= 0) return '--';
    final dt = DateTime.fromMillisecondsSinceEpoch(millis);
    return DateFormat('MMM d, HH:mm').format(dt);
  }
}

class _MessageTile extends StatelessWidget {
  const _MessageTile({required this.message});
  final Map<String, dynamic> message;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final deleted = (message['isDeleted'] ?? false) == true;
    final content = message['content']?.toString() ?? '';
    final timestamp = message['timestamp'] is int
        ? message['timestamp'] as int
        : null;
    final bubbleColor = deleted
        ? theme.colorScheme.errorContainer
        : theme.colorScheme.surfaceContainerHighest;
    final icon = deleted ? Icons.delete_outline : Icons.message;

    return Container(
      margin: const EdgeInsets.only(bottom: 10),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: bubbleColor,
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, size: 20, color: theme.colorScheme.onSurfaceVariant),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  content.isEmpty ? 'No preview available' : content,
                  style: theme.textTheme.bodyMedium?.copyWith(
                    fontWeight: deleted ? FontWeight.w600 : FontWeight.normal,
                  ),
                ),
                const SizedBox(height: 4),
                Row(
                  children: [
                    if (deleted)
                      Container(
                        padding: const EdgeInsets.symmetric(
                          horizontal: 8,
                          vertical: 2,
                        ),
                        decoration: BoxDecoration(
                          color: theme.colorScheme.error.withOpacity(.15),
                          borderRadius: BorderRadius.circular(20),
                        ),
                        child: Text(
                          'Deleted',
                          style: theme.textTheme.labelSmall?.copyWith(
                            color: theme.colorScheme.error,
                          ),
                        ),
                      ),
                    if (deleted) const SizedBox(width: 8),
                    Text(
                      _formatTimestamp(timestamp),
                      style: theme.textTheme.labelSmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  String _formatTimestamp(int? millis) {
    if (millis == null || millis <= 0) return '--';
    final dt = DateTime.fromMillisecondsSinceEpoch(millis);
    return DateFormat('MMM d, HH:mm').format(dt);
  }
}
