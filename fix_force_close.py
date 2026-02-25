"""
Script untuk memperbaiki FORCE CLOSE.

Jalankan di root project:
  cd C:\\Users\\surya\\AndroidStudioProjects\\presence
  python fix_force_close.py

Lalu:
  flutter clean
  flutter pub get
  flutter run
"""

import os

files = {}

# ── 1. main.dart - tambah WidgetsFlutterBinding.ensureInitialized() ──────────
files["lib/main.dart"] = '''\
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
'''

# ── 2. AndroidManifest.xml - semua permission ─────────────────────────────────
files["android/app/src/main/AndroidManifest.xml"] = '''\
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <!-- INTERNET: wajib untuk API call ke GAS -->
    <uses-permission android:name="android.permission.INTERNET"/>

    <!-- KAMERA: wajib untuk QR scan -->
    <uses-permission android:name="android.permission.CAMERA"/>
    <uses-feature android:name="android.hardware.camera" android:required="false"/>

    <!-- LOKASI: wajib untuk GPS -->
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION"/>

    <application
        android:label="Cloud Praktikum"
        android:name="${applicationName}"
        android:icon="@mipmap/ic_launcher"
        android:usesCleartextTraffic="true">

        <!-- GANTI dengan Google Maps API Key milik Anda -->
        <!-- Jika belum punya API key, isi: AIzaSyDUMMYKEYxxxxxxxxxxxxxxxxxxxxxxxxxxx -->
        <meta-data
            android:name="com.google.android.geo.API_KEY"
            android:value="YOUR_GOOGLE_MAPS_API_KEY"/>

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:launchMode="singleTop"
            android:taskAffinity=""
            android:theme="@style/LaunchTheme"
            android:configChanges="orientation|keyboardHidden|keyboard|screenSize|smallestScreenSize|locale|layoutDirection|fontScale|screenLayout|density|uiMode"
            android:hardwareAccelerated="true"
            android:windowSoftInputMode="adjustResize">
            <meta-data
                android:name="io.flutter.embedding.android.NormalTheme"
                android:resource="@style/NormalTheme"/>
            <intent-filter>
                <action android:name="android.intent.action.MAIN"/>
                <category android:name="android.intent.category.LAUNCHER"/>
            </intent-filter>
        </activity>
        <meta-data android:name="flutterEmbedding" android:value="2"/>
    </application>

    <queries>
        <intent>
            <action android:name="android.intent.action.PROCESS_TEXT"/>
            <data android:mimeType="text/plain"/>
        </intent>
    </queries>
</manifest>
'''

# ── 3. build.gradle - minSdk 21 ───────────────────────────────────────────────
files["android/app/build.gradle"] = '''\
plugins {
    id "com.android.application"
    id "kotlin-android"
    id "dev.flutter.flutter-gradle-plugin"
}

android {
    namespace "com.example.presence"
    compileSdk flutter.compileSdkVersion
    ndkVersion flutter.ndkVersion

    compileOptions {
        sourceCompatibility JavaVersion.VERSION_1_8
        targetCompatibility JavaVersion.VERSION_1_8
    }

    kotlinOptions {
        jvmTarget = "1.8"
    }

    defaultConfig {
        applicationId "com.example.presence"
        minSdkVersion 21
        targetSdkVersion flutter.targetSdkVersion
        versionCode flutter.versionCode
        versionName flutter.versionName
        multiDexEnabled true
    }

    buildTypes {
        release {
            signingConfig signingConfigs.debug
            minifyEnabled false
            shrinkResources false
        }
    }
}

flutter {
    source "../.."
}

dependencies {
    implementation "androidx.multidex:multidex:2.0.1"
}
'''

# ── 4. map_screen.dart - handle Maps crash jika API key belum diset ───────────
files["lib/features/gps/presentation/screens/map_screen.dart"] = '''\
// lib/features/gps/presentation/screens/map_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:presence/features/gps/presentation/providers/gps_provider.dart';

class MapScreen extends ConsumerStatefulWidget {
  const MapScreen({super.key});

  @override
  ConsumerState<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends ConsumerState<MapScreen> {
  GoogleMapController? _mapController;
  static const _defaultPosition = LatLng(-7.2575, 112.7521);
  bool _mapError = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        ref.read(gpsProvider.notifier).loadMapData();
      }
    });
  }

  @override
  void dispose() {
    _mapController?.dispose();
    ref.read(gpsProvider.notifier).stopTracking();
    super.dispose();
  }

  Set<Marker> _buildMarkers(GpsState state) {
    final markers = <Marker>{};
    if (state.latest != null) {
      markers.add(Marker(
        markerId: const MarkerId('latest'),
        position: LatLng(state.latest!.lat, state.latest!.lng),
        infoWindow: InfoWindow(title: 'Posisi Terbaru', snippet: state.latest!.ts),
        icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueAzure),
      ));
    }
    if (state.lat != null && state.lng != null) {
      markers.add(Marker(
        markerId: const MarkerId('live'),
        position: LatLng(state.lat!, state.lng!),
        infoWindow: const InfoWindow(title: 'Lokasi Saya (Live)'),
      ));
    }
    return markers;
  }

  Set<Polyline> _buildPolylines(GpsState state) {
    if (state.history.length < 2) return {};
    return {
      Polyline(
        polylineId: const PolylineId('track'),
        points: state.history.map((p) => LatLng(p.lat, p.lng)).toList(),
        color: Colors.blue,
        width: 4,
      ),
    };
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(gpsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('GPS Tracking'),
        actions: [
          if (state.isSyncing)
            const Padding(
              padding: EdgeInsets.all(12),
              child: SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
              ),
            ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.read(gpsProvider.notifier).loadMapData(),
          ),
        ],
      ),
      body: Stack(
        children: [
          // Tampilkan error jika Maps gagal load
          if (_mapError)
            Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.map_outlined, size: 64, color: Colors.grey),
                  const SizedBox(height: 16),
                  const Text('Google Maps gagal dimuat.',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  const Padding(
                    padding: EdgeInsets.symmetric(horizontal: 32),
                    child: Text(
                      'Pastikan Google Maps API Key sudah diisi di AndroidManifest.xml',
                      textAlign: TextAlign.center,
                      style: TextStyle(color: Colors.grey),
                    ),
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () => setState(() => _mapError = false),
                    child: const Text('Coba Lagi'),
                  ),
                ],
              ),
            )
          else
            // Google Map dengan error handling
            _buildMap(state),

          // Info koordinat GPS
          Positioned(
            top: 10, left: 10, right: 10,
            child: Card(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                child: Row(
                  children: [
                    Icon(
                      state.isTracking ? Icons.location_on : Icons.location_off,
                      color: state.isTracking ? Colors.green : Colors.grey,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        state.lat != null
                            ? '\${state.lat!.toStringAsFixed(5)}, \${state.lng!.toStringAsFixed(5)}'
                                ' \\u00b1\${state.accuracy?.toStringAsFixed(0) ?? "?"}m'
                            : 'GPS belum aktif',
                        style: const TextStyle(fontSize: 13),
                      ),
                    ),
                    Text('\${state.history.length} titik',
                        style: TextStyle(color: Colors.grey.shade600, fontSize: 12)),
                  ],
                ),
              ),
            ),
          ),

          if (state.error != null)
            Positioned(
              bottom: 80, left: 10, right: 10,
              child: Card(
                color: Colors.red.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(10),
                  child: Text('\\u26a0 \${state.error}',
                      style: const TextStyle(color: Colors.red)),
                ),
              ),
            ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          if (state.isTracking) {
            ref.read(gpsProvider.notifier).stopTracking();
          } else {
            ref.read(gpsProvider.notifier).startTracking();
          }
        },
        icon: Icon(state.isTracking ? Icons.stop : Icons.play_arrow),
        label: Text(state.isTracking ? 'Stop' : 'Start Tracking'),
        backgroundColor: state.isTracking ? Colors.red : Colors.blue,
      ),
    );
  }

  Widget _buildMap(GpsState state) {
    try {
      return GoogleMap(
        onMapCreated: (ctrl) => _mapController = ctrl,
        initialCameraPosition: const CameraPosition(target: _defaultPosition, zoom: 15),
        markers: _buildMarkers(state),
        polylines: _buildPolylines(state),
        myLocationEnabled: true,
        myLocationButtonEnabled: true,
        onCameraIdle: () {},
      );
    } catch (e) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) setState(() => _mapError = true);
      });
      return const SizedBox.shrink();
    }
  }
}
'''

# ── 5. qr_scan_screen.dart - tambah error handling kamera ────────────────────
files["lib/features/presence/presentation/screens/qr_scan_screen.dart"] = '''\
// lib/features/presence/presentation/screens/qr_scan_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:presence/features/presence/presentation/providers/presence_provider.dart';
import 'package:presence/features/presence/presentation/screens/checkin_screen.dart';

class QrScanScreen extends ConsumerStatefulWidget {
  const QrScanScreen({super.key});

  @override
  ConsumerState<QrScanScreen> createState() => _QrScanScreenState();
}

class _QrScanScreenState extends ConsumerState<QrScanScreen> {
  MobileScannerController? _controller;
  bool _scanned = false;
  bool _cameraError = false;

  @override
  void initState() {
    super.initState();
    _initCamera();
  }

  void _initCamera() {
    try {
      _controller = MobileScannerController(
        detectionSpeed: DetectionSpeed.normal,
        facing: CameraFacing.back,
      );
    } catch (e) {
      if (mounted) setState(() => _cameraError = true);
    }
  }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }

  void _onDetect(BarcodeCapture capture) {
    if (_scanned) return;
    final barcode = capture.barcodes.firstOrNull;
    final value = barcode?.rawValue;
    if (value == null || value.isEmpty) return;

    _scanned = true;
    _controller?.stop();

    ref.read(presenceProvider.notifier).setScannedToken(value);
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(builder: (_) => const CheckInScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_cameraError) {
      return Scaffold(
        appBar: AppBar(title: const Text('Scan QR Presensi')),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.camera_alt_outlined, size: 64, color: Colors.grey),
              const SizedBox(height: 16),
              const Text('Kamera tidak tersedia', style: TextStyle(fontSize: 16)),
              const SizedBox(height: 8),
              const Text('Izinkan akses kamera di pengaturan HP',
                  style: TextStyle(color: Colors.grey)),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () {
                  setState(() {
                    _cameraError = false;
                    _scanned = false;
                  });
                  _initCamera();
                },
                child: const Text('Coba Lagi'),
              ),
              const SizedBox(height: 12),
              // Input manual token jika kamera gagal
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 32),
                child: _ManualTokenInput(),
              ),
            ],
          ),
        ),
      );
    }

    if (_controller == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Scan QR Presensi'),
        actions: [
          IconButton(
            icon: const Icon(Icons.flash_on),
            onPressed: _controller!.toggleTorch,
          ),
          IconButton(
            icon: const Icon(Icons.cameraswitch),
            onPressed: _controller!.switchCamera,
          ),
        ],
      ),
      body: Stack(
        children: [
          MobileScanner(
            controller: _controller!,
            onDetect: _onDetect,
            errorBuilder: (context, error, child) {
              return Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.error_outline, size: 64, color: Colors.red),
                    const SizedBox(height: 16),
                    Text('Error kamera: \${error.errorCode}',
                        style: const TextStyle(color: Colors.red)),
                  ],
                ),
              );
            },
          ),
          Center(
            child: Container(
              width: 250,
              height: 250,
              decoration: BoxDecoration(
                border: Border.all(color: Colors.greenAccent, width: 3),
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
          const Positioned(
            bottom: 40, left: 0, right: 0,
            child: Text(
              'Arahkan kamera ke QR Code di kelas',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.white, fontSize: 16,
                  shadows: [Shadow(blurRadius: 4, color: Colors.black)]),
            ),
          ),
        ],
      ),
    );
  }
}

// Widget input manual token jika kamera tidak bisa digunakan
class _ManualTokenInput extends ConsumerStatefulWidget {
  @override
  ConsumerState<_ManualTokenInput> createState() => _ManualTokenInputState();
}

class _ManualTokenInputState extends ConsumerState<_ManualTokenInput> {
  final _ctrl = TextEditingController();

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const Divider(),
        const Text('Atau masukkan token manual:',
            style: TextStyle(color: Colors.grey, fontSize: 12)),
        const SizedBox(height: 8),
        TextField(
          controller: _ctrl,
          decoration: const InputDecoration(
            labelText: 'QR Token',
            border: OutlineInputBorder(),
            isDense: true,
          ),
        ),
        const SizedBox(height: 8),
        ElevatedButton(
          onPressed: () {
            final token = _ctrl.text.trim();
            if (token.isEmpty) return;
            ref.read(presenceProvider.notifier).setScannedToken(token);
            Navigator.of(context).pushReplacement(
              MaterialPageRoute(builder: (_) => const CheckInScreen()),
            );
          },
          child: const Text('Gunakan Token Ini'),
        ),
      ],
    );
  }
}
'''

# ─── Write files ───────────────────────────────────────────────────────────────
success = 0
failed = 0
for path, content in files.items():
    full_path = os.path.join(os.getcwd(), path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  ✅ {path}")
        success += 1
    except Exception as e:
        print(f"  ❌ {path}: {e}")
        failed += 1

print(f"\nSelesai! {success} file diperbarui, {failed} gagal.")
print("\nJalankan perintah berikut:")
print("  flutter clean")
print("  flutter pub get")
print("  flutter run")
