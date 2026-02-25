// lib/main.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:presence/features/presence/presentation/screens/qr_scan_screen.dart';
import 'package:presence/features/accel/presentation/screens/accel_screen.dart';
import 'package:presence/features/gps/presentation/screens/map_screen.dart';

void main() async {
  // WAJIB sebelum pakai plugin (Maps, GPS, Camera, SharedPreferences)
  WidgetsFlutterBinding.ensureInitialized();

  runApp(const ProviderScope(child: CloudPraktikumApp()));
}

class CloudPraktikumApp extends StatelessWidget {
  const CloudPraktikumApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Cloud Praktikum',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(colorSchemeSeed: Colors.blue, useMaterial3: true),
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
  int _currentIndex = 0;

  List<Widget> get _screens => const [
        QrScanScreen(),
        AccelScreen(),
        MapScreen(),
      ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: IndexedStack(index: _currentIndex, children: _screens),
      bottomNavigationBar: NavigationBar(
        selectedIndex: _currentIndex,
        onDestinationSelected: (i) => setState(() => _currentIndex = i),
        destinations: const [
          NavigationDestination(icon: Icon(Icons.qr_code_scanner), label: 'Presensi'),
          NavigationDestination(icon: Icon(Icons.sensors), label: 'Sensor'),
          NavigationDestination(icon: Icon(Icons.map), label: 'GPS Map'),
        ],
      ),
    );
  }
}
