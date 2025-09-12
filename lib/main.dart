import 'dart:async';
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
      theme: ThemeData(colorScheme: ColorScheme.fromSeed(seedColor: Colors.green)),
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
  static const _channel = MethodChannel('com.example.whatsapp_recovery/notifications');
  List<Map<String, dynamic>> _messages = [];
  bool _showOnlyDeleted = false;
  bool _loading = false;

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
    setState(() => _loading = true);
    try {
      final List<dynamic> res = await _channel.invokeMethod('getMessages');
      _messages = res.cast<Map>().map((e) => e.map((k, v) => MapEntry(k.toString(), v))).toList();
    } catch (e) {
      // ignore
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final filtered = _showOnlyDeleted
        ? _messages.where((m) => (m['isDeleted'] ?? false) == true).toList()
        : _messages;

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
            tooltip: _showOnlyDeleted ? 'Show All' : 'Show Deleted Only',
            onPressed: () => setState(() => _showOnlyDeleted = !_showOnlyDeleted),
            icon: Icon(_showOnlyDeleted ? Icons.inbox : Icons.delete),
          ),
          IconButton(
            tooltip: 'Refresh',
            onPressed: _refresh,
            icon: const Icon(Icons.refresh),
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : filtered.isEmpty
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(24.0),
                    child: Column(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        Icon(Icons.chat, size: 56, color: Colors.green),
                        const SizedBox(height: 12),
                        const Text('No messages yet. Enable notification access to start capturing.'),
                      ],
                    ),
                  ),
                )
              : ListView.separated(
                  itemCount: filtered.length,
                  separatorBuilder: (_, __) => const Divider(height: 1),
                  itemBuilder: (context, i) {
                    final m = filtered[i];
                    final dt = DateTime.fromMillisecondsSinceEpoch((m['timestamp'] ?? 0) as int);
                    final ts = DateFormat('MMM d, HH:mm').format(dt);
                    final deleted = (m['isDeleted'] ?? false) == true;
                    return ListTile(
                      leading: CircleAvatar(
                        backgroundColor: deleted ? Colors.red.shade100 : Colors.green.shade100,
                        child: Icon(deleted ? Icons.delete : Icons.message, color: Colors.black87),
                      ),
                      title: Text(m['sender']?.toString() ?? 'Unknown'),
                      subtitle: Text(m['content']?.toString() ?? ''),
                      trailing: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [Text(ts, style: const TextStyle(fontSize: 12))],
                      ),
                    );
                  },
                ),
    );
  }
}
