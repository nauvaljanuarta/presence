# Cloud Praktikum — Flutter Client

Aplikasi mobile Flutter untuk Praktikum Komputasi Awan.
Terhubung ke backend Google Apps Script (GAS) via REST API.

## Struktur Folder

```
lib/
├── main.dart
├── core/
│   ├── api/
│   │   ├── api_client.dart        # Dio HTTP client
│   │   ├── api_response.dart      # Model response standar { ok, data, error }
│   │   └── api_provider.dart      # Riverpod provider
│   └── utils/
│       ├── device_info.dart       # Ambil device_id stabil
│       └── timestamp.dart         # Format ISO-8601
└── features/
    ├── presence/                  # Modul Presensi QR
    │   ├── data/
    │   │   ├── models/            # JSON parsing models
    │   │   └── repositories/      # Implementasi repository
    │   ├── domain/
    │   │   ├── entities/          # Data class murni
    │   │   └── repositories/      # Interface/abstract
    │   └── presentation/
    │       ├── providers/         # Riverpod StateNotifier
    │       └── screens/           # QrScanScreen, CheckInScreen
    ├── accel/                     # Modul Accelerometer
    │   └── ...
    └── gps/                       # Modul GPS + Map
        └── ...
```

## Setup

### 1. Ganti BASE_URL

Edit `lib/core/api/api_client.dart`:
```dart
static const String _baseUrl =
    'https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec';
```

### 2. Google Maps API Key

**Android** — `android/app/src/main/AndroidManifest.xml`:
```xml
<meta-data
  android:name="com.google.android.geo.API_KEY"
  android:value="YOUR_GOOGLE_MAPS_API_KEY"/>
```

**iOS** — `ios/Runner/AppDelegate.swift`:
```swift
GMSServices.provideAPIKey("YOUR_GOOGLE_MAPS_API_KEY")
```

### 3. Install dependencies

```bash
flutter pub get
```

### 4. Jalankan

```bash
flutter run
```

## API Endpoints

| Modul       | Method | Path                          |
|-------------|--------|-------------------------------|
| Presensi    | POST   | /presence/qr/generate         |
| Presensi    | POST   | /presence/checkin             |
| Presensi    | GET    | /presence/status              |
| Accelerometer | POST | /telemetry/accel              |
| Accelerometer | GET  | /telemetry/accel/latest       |
| GPS         | POST   | /telemetry/gps                |
| GPS         | GET    | /telemetry/gps/latest         |
| GPS         | GET    | /telemetry/gps/history        |

## Flow Presensi QR

```
1. QrScanScreen
   └── Scan QR Code (mobile_scanner)
         ↓ qr_token string
2. presenceProvider.setScannedToken(token)
         ↓
3. Navigasi ke CheckInScreen
   └── User isi user_id, course_id, session_id
         ↓
4. presenceProvider.checkIn(...)
   └── DeviceInfoUtil.getDeviceId()
   └── POST /presence/checkin { user_id, device_id, course_id, session_id, qr_token, ts }
         ↓ { "ok": true, "data": { "presence_id": "PR-001", "status": "checked_in" } }
5. Tampilkan status checked_in di UI
```

## Permissions Required

**Android** (`android/app/src/main/AndroidManifest.xml`):
```xml
<uses-permission android:name="android.permission.CAMERA"/>
<uses-permission android:name="android.permission.ACCESS_FINE_LOCATION"/>
<uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION"/>
<uses-permission android:name="android.permission.INTERNET"/>
```

**iOS** (`ios/Runner/Info.plist`):
```xml
<key>NSCameraUsageDescription</key>
<string>Diperlukan untuk scan QR presensi</string>
<key>NSLocationWhenInUseUsageDescription</key>
<string>Diperlukan untuk GPS tracking</string>
```
