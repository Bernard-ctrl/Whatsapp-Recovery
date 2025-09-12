// This is a basic Flutter widget test.
//
// To perform an interaction with a widget in your test, use the WidgetTester
// utility in the flutter_test package. For example, you can send tap and scroll
// gestures. You can also use WidgetTester to find child widgets in the widget
// tree, read text, and verify that the values of widget properties are correct.

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:whatsapp_recovery/main.dart';

void main() {
  testWidgets('Home screen renders basic actions', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const App());
    await tester.pump(const Duration(milliseconds: 100));

    // Verify AppBar title exists.
    expect(find.text('Recovered Messages'), findsOneWidget);

    // Verify action icons exist.
    expect(find.byIcon(Icons.lock_open), findsOneWidget); // open notification access
    expect(find.byIcon(Icons.delete), findsOneWidget); // toggle deleted-only (initial state)
    expect(find.byIcon(Icons.refresh), findsOneWidget); // refresh
  });
}
