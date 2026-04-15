# 📱 Presence QR API & Telemetry System

![Version](https://img.shields.io/badge/version-1.2.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Platform](https://img.shields.io/badge/platform-GAS%20%7C%20Firebase-orange.svg)

Sistem absensi modern berbasis QR Code dengan fitur pelacakan telemetri (GPS & Accelerometer) yang terintegrasi dengan Google Sheets dan Firebase. Dikembangkan untuk praktikum **Cloud Computing (CC)** Semester 6.

---

## 🚀 Fitur Utama

- **QR Attendance**: Generate token QR dinamis (berlaku 30 detik) dan aman untuk absensi kelas. Auto-refresh setelah kadaluarsa.
- **Telemetry Tracking**:
  - **GPS**: Melacak koordinat lokasi perangkat secara real-time dengan visualisasi peta (Leaflet.js) dan riwayat jejak (polyline).
  - **Accelerometer**: Memantau data sensor gerak perangkat (X, Y, Z axis) dengan grafik real-time (Chart.js).
- **Hybrid Backend**:
  - **Google Apps Script (GAS)**: Integrasi langsung dengan Google Sheets sebagai database. Mendukung semua fitur (QR, Telemetry, UI).
  - **Firebase Cloud Functions**: Backend alternatif menggunakan Firestore. Saat ini mendukung fitur Presence (QR).
- **Web UI**: Antarmuka responsif untuk dashboard presensi, scanner QR, pelacakan GPS, dan monitor akselerometer. Mendukung dual-mode (Mahasiswa & Admin).

---

## 📂 Struktur Proyek

```text
presence/
├── GAS Presence App/           # Implementasi Google Apps Script (fitur lengkap)
│   ├── Code.js                 # Logika backend utama (routing, CRUD)
│   ├── index.html              # Dashboard utama — generate QR code
│   ├── scan.html               # Halaman scanner QR untuk mahasiswa
│   ├── gps.html                # Dashboard GPS — kirim & pantau lokasi (Leaflet.js)
│   ├── accelerometer.html      # Dashboard Telemetri — sensor gerak & grafik (Chart.js)
│   ├── appsscript.json         # Manifest Apps Script (timezone, runtime V8)
│   └── .clasp.json             # Konfigurasi CLASP untuk deployment via CLI
│
├── Firebase Presence App/      # Implementasi Firebase (Presence only)
│   ├── functions/
│   │   ├── index.js            # Cloud Functions — Express.js API (QR & Presence)
│   │   └── package.json        # Dependencies (firebase-admin, express, cors)
│   ├── public/
│   │   ├── index.html          # Dashboard presensi (Firebase version)
│   │   └── scan.html           # Halaman scanner QR (Firebase version)
│   ├── firebase.json           # Konfigurasi hosting & rewrites
│   └── .firebaserc             # Project ID Firebase (presence-qrcode)
│
├── swagger.yaml                # Dokumentasi API lengkap (OpenAPI 3.0)
└── README.md                   # Dokumentasi proyek ini
```

---

## 🛠️ Instalasi & Setup

### Prasyarat

- Akun Google (untuk GAS & Google Sheets)
- Node.js v18+ (untuk Firebase)
- Firebase CLI (`npm i -g firebase-tools`)
- CLASP CLI (`npm i -g @google/clasp`) — opsional, untuk deploy GAS via terminal

### Google Apps Script (GAS)

1. Buat spreadsheet baru di [Google Sheets](https://sheets.new).
2. Buat 4 sheet dengan nama: `tokens`, `presence`, `accelerometer`, `gps`.
3. Pergi ke **Extensions > Apps Script**.
4. Salin `GAS Presence App/Code.js` ke editor, ganti `spreadsheet_id` dengan ID spreadsheet Anda.
5. Buat file HTML baru (`index`, `scan`, `gps`, `accelerometer`) dan salin isinya masing-masing.
6. Deploy sebagai **Web App**:
   - Execute as: **Me**
   - Who has access: **Anyone**
7. Salin URL deployment (`/exec`) dan perbarui `API_URL` di file `gps.html` dan `accelerometer.html`.

### Firebase

1. Login Firebase CLI: `firebase login`.
2. Inisialisasi project: `firebase init` (pilih Functions + Hosting).
3. Install dependencies: `cd functions && npm install`.
4. Deploy:
   ```bash
   firebase deploy --only functions,hosting
   ```

---

## 📖 Dokumentasi API

Seluruh detail API dapat dilihat pada file [swagger.yaml](./swagger.yaml) (OpenAPI 3.0).

### Presence (QR)

| Method | Endpoint                | Deskripsi                                              | Backend     |
|--------|-------------------------|--------------------------------------------------------|-------------|
| `POST` | `/presence/qr/generate` | Membuat token QR baru (berlaku 30 detik).              | GAS + Firebase |
| `POST` | `/presence/checkin`      | Melakukan absensi menggunakan token QR yang valid.     | GAS + Firebase |
| `GET`  | `/presence/status`       | Mengecek status kehadiran user pada sesi tertentu.     | GAS + Firebase |

### Telemetry — Accelerometer

| Method | Endpoint                  | Deskripsi                                                    | Backend  |
|--------|---------------------------|--------------------------------------------------------------|----------|
| `POST` | `/telemetry/accel`        | Mengirim data sampel sensor akselerometer (X, Y, Z).         | GAS only |
| `GET`  | `/telemetry/accel/latest` | Mengambil data akselerometer terbaru untuk suatu perangkat.   | GAS only |

### Telemetry — GPS

| Method | Endpoint                  | Deskripsi                                                    | Backend  |
|--------|---------------------------|--------------------------------------------------------------|----------|
| `POST` | `/telemetry/gps`          | Mengirim data koordinat GPS dari perangkat.                  | GAS only |
| `GET`  | `/telemetry/gps/latest`   | Mengambil lokasi GPS terbaru untuk suatu perangkat.          | GAS only |
| `GET`  | `/telemetry/gps/history`  | Mengambil riwayat lokasi GPS (default: 200 entri terakhir).  | GAS only |

### UI Pages

| Method | Endpoint  | Deskripsi                                           | Backend        |
|--------|-----------|-----------------------------------------------------|----------------|
| `GET`  | `/`       | Dashboard utama — generate QR code untuk sesi baru. | GAS + Firebase |
| `GET`  | `?page=scan` | Halaman scanner QR untuk mahasiswa.              | GAS + Firebase |
| `GET`  | `?page=gps`  | Dashboard GPS tracker & peta (Leaflet.js).       | GAS only       |
| `GET`  | `?page=accelerometer` | Dashboard telemetri sensor & grafik (Chart.js). | GAS only |

---

## 🧰 Tech Stack

| Layer           | Teknologi                                                   |
|-----------------|-------------------------------------------------------------|
| **Backend (GAS)**  | Google Apps Script, Google Sheets (database)              |
| **Backend (Firebase)** | Firebase Cloud Functions, Firestore, Express.js, CORS |
| **Frontend**       | HTML5, Vanilla CSS, Vanilla JavaScript                   |
| **Maps**           | Leaflet.js v1.9.4 + OpenStreetMap tiles                  |
| **Charts**         | Chart.js (real-time line chart)                           |
| **QR Code**        | goqr.me API (`api.qrserver.com`)                         |
| **Deployment**     | Google Apps Script Web App, Firebase Hosting              |

---

## 📊 Google Sheets Schema

Proyek GAS menggunakan 4 sheet pada spreadsheet:

### Sheet `tokens`
| Kolom | Isi |
|-------|-----|
| A | `qr_token` — Token unik (TKN-XXXXXX) |
| B | `session_id` |
| C | `course_id` |
| D | `expires_at` — ISO datetime (30 detik dari pembuatan) |
| E | `created_at` |

### Sheet `presence`
| Kolom | Isi |
|-------|-----|
| A | `presence_id` (HDR-XXXXXXXX) |
| B | `session_id` |
| C | `user_id` |
| D | `device_id` |
| E | `course_id` |
| F | `qr_token` |
| G | `timestamp` |

### Sheet `accelerometer`
| Kolom | Isi |
|-------|-----|
| A | `device_id` |
| B | `timestamp` (sample time) |
| C | `x` |
| D | `y` |
| E | `z` |
| F | `server_ts` |

### Sheet `gps`
| Kolom | Isi |
|-------|-----|
| A | `device_id` |
| B | `timestamp` |
| C | `lat` |
| D | `lng` |
| E | `accuracy_m` |
| F | `server_ts` |

---

## 📝 Catatan Perubahan

### v1.2.0 (April 2026)
- Pembaruan dokumentasi README dengan struktur proyek lengkap.
- Menambahkan dokumentasi skema Google Sheets (tokens, presence, accelerometer, gps).
- Menambahkan tech stack & prasyarat instalasi.
- Menambahkan kolom **Backend** pada tabel API untuk kejelasan fitur per platform.
- Mencatat halaman UI Pages (`index`, `scan`, `gps`, `accelerometer`) dengan mapping backend.

### v1.1.0
- Menambahkan modul **GPS Tracking** (`POST /telemetry/gps`, `GET /telemetry/gps/latest`, `GET /telemetry/gps/history`).
- Menambahkan modul **Accelerometer Telemetry** (`POST /telemetry/accel`, `GET /telemetry/accel/latest`).
- Menambahkan endpoint **Presence Status** (`GET /presence/status`).
- Menambahkan halaman **QR Scanner** (`?page=scan`).
- Halaman GPS dengan peta Leaflet.js (mode Mahasiswa & Admin).
- Halaman Accelerometer dengan grafik Chart.js real-time.
- Pembaruan dokumentasi Swagger (OpenAPI 3.0) dengan skema lengkap.
- Optimalisasi respon JSON di Google Apps Script.

### v1.0.0
- Fitur dasar QR Presence: generate token & check-in.
- Implementasi GAS + Firebase (dual backend).
- Dashboard web untuk generate QR code.

---

> Dikembangkan untuk praktikum **CC (Cloud Computing)** Semester 6.
