import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:provider/provider.dart';
import 'package:firebase_analytics/firebase_analytics.dart';
import 'theme/app_theme.dart';
import 'pages/dashboard_page.dart';
import 'services/auth_service.dart';
import 'firebase_options.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  await Firebase.initializeApp(options: DefaultFirebaseOptions.currentPlatform);
  await FirebaseAnalytics.instance.logEvent(name: 'test_event');

  runApp(IntelliviewApp());
}

class IntelliviewApp extends StatelessWidget {
  final FirebaseAnalytics analytics = FirebaseAnalytics.instance;
  IntelliviewApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [ChangeNotifierProvider(create: (_) => AuthService())],
      child: MaterialApp(
        title: 'Intelliview interview preparation',
        theme: AppTheme.lightTheme,
        home: const DashboardPage(),
        navigatorObservers: [
          FirebaseAnalyticsObserver(analytics: analytics), // screen changes
        ],
      ),
    );
  }
}
