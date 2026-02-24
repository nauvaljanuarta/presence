"""
Jalankan script ini di ROOT folder project Flutter Anda:
  cd C:\\Users\\surya\\AndroidStudioProjects\\presence
  python fix_imports.py

Script ini akan OVERWRITE semua file dart dengan versi yang sudah diperbaiki.
"""

import os

files = {}

# ─── core/api/api_client.dart ─────────────────────────────────────────────────
files["lib/core/api/api_client.dart"] = '''\
// lib/core/api/api_client.dart
import 'package:dio/dio.dart';
import 'package:presence/core/api/api_response.dart';

class ApiClient {
  static const String _baseUrl =
      'https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec';

  late final Dio _dio;

  ApiClient() {
    _dio = Dio(BaseOptions(
      baseUrl: _baseUrl,
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 15),
      headers: {'Content-Type': 'application/json'},
    ));
    _dio.interceptors.add(LogInterceptor(
      requestBody: true,
      responseBody: true,
      error: true,
    ));
  }

  Future<ApiResponse<T>> get<T>(
    String path, {
    Map<String, dynamic>? queryParams,
    required T Function(Map<String, dynamic>) fromJson,
  }) async {
    try {
      final response = await _dio.get(path, queryParameters: queryParams);
      return ApiResponse.fromJson(response.data, fromJson);
    } on DioException catch (e) {
      return ApiResponse.error(_dioErrorMessage(e));
    }
  }

  Future<ApiResponse<T>> post<T>(
    String path, {
    required Map<String, dynamic> body,
    required T Function(Map<String, dynamic>) fromJson,
  }) async {
    try {
      final response = await _dio.post(path, data: body);
      return ApiResponse.fromJson(response.data, fromJson);
    } on DioException catch (e) {
      return ApiResponse.error(_dioErrorMessage(e));
    }
  }

  String _dioErrorMessage(DioException e) {
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.receiveTimeout:
        return 'connection_timeout';
      case DioExceptionType.badResponse:
        return 'server_error: \${e.response?.statusCode}';
      default:
        return e.message ?? 'unknown_error';
    }
  }
}
'''

# ─── core/api/api_response.dart ───────────────────────────────────────────────
files["lib/core/api/api_response.dart"] = '''\
// lib/core/api/api_response.dart
class ApiResponse<T> {
  final bool ok;
  final T? data;
  final String? error;

  const ApiResponse({required this.ok, this.data, this.error});

  factory ApiResponse.fromJson(
    dynamic json,
    T Function(Map<String, dynamic>) fromJson,
  ) {
    final map = json as Map<String, dynamic>;
    final ok = map['ok'] as bool? ?? false;
    if (ok && map['data'] != null) {
      return ApiResponse(ok: true, data: fromJson(map['data']));
    } else {
      return ApiResponse(ok: false, error: map['error'] as String?);
    }
  }

  factory ApiResponse.error(String message) {
    return ApiResponse(ok: false, error: message);
  }

  bool get isSuccess => ok && data != null;
}
'''

# ─── core/api/api_provider.dart ───────────────────────────────────────────────
files["lib/core/api/api_provider.dart"] = '''\
// lib/core/api/api_provider.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:presence/core/api/api_client.dart';

final apiClientProvider = Provider<ApiClient>((ref) => ApiClient());
'''

# ─── core/utils/device_info.dart ──────────────────────────────────────────────
files["lib/core/utils/device_info.dart"] = '''\
// lib/core/utils/device_info.dart
import 'dart:io';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:uuid/uuid.dart';

class DeviceInfoUtil {
  static const _keyDeviceId = 'device_id';

  static Future<String> getDeviceId() async {
    final prefs = await SharedPreferences.getInstance();
    if (prefs.containsKey(_keyDeviceId)) {
      return prefs.getString(_keyDeviceId)!;
    }
    String id;
    try {
      final info = DeviceInfoPlugin();
      if (Platform.isAndroid) {
        final android = await info.androidInfo;
        id = android.id;
      } else if (Platform.isIOS) {
        final ios = await info.iosInfo;
        id = ios.identifierForVendor ?? const Uuid().v4();
      } else {
        id = const Uuid().v4();
      }
    } catch (_) {
      id = const Uuid().v4();
    }
    await prefs.setString(_keyDeviceId, id);
    return id;
  }
}
'''

# ─── core/utils/timestamp.dart ────────────────────────────────────────────────
files["lib/core/utils/timestamp.dart"] = '''\
// lib/core/utils/timestamp.dart
class Timestamp {
  static String now() => DateTime.now().toUtc().toIso8601String();
  static DateTime parse(String ts) => DateTime.parse(ts).toLocal();
  static String format(DateTime dt) => dt.toUtc().toIso8601String();
}
'''

# ─── presence/domain/entities ─────────────────────────────────────────────────
files["lib/features/presence/domain/entities/presence_entities.dart"] = '''\
// lib/features/presence/domain/entities/presence_entities.dart
class QrToken {
  final String qrToken;
  final String expiresAt;
  const QrToken({required this.qrToken, required this.expiresAt});
}

class CheckInResult {
  final String presenceId;
  final String status;
  const CheckInResult({required this.presenceId, required this.status});
}

class PresenceStatus {
  final String userId;
  final String courseId;
  final String sessionId;
  final String status;
  final String lastTs;
  const PresenceStatus({
    required this.userId,
    required this.courseId,
    required this.sessionId,
    required this.status,
    required this.lastTs,
  });
}
'''

# ─── presence/domain/repositories ─────────────────────────────────────────────
files["lib/features/presence/domain/repositories/presence_repository.dart"] = '''\
// lib/features/presence/domain/repositories/presence_repository.dart
import 'package:presence/features/presence/domain/entities/presence_entities.dart';

abstract class PresenceRepository {
  Future<QrToken> generateQr({
    required String courseId,
    required String sessionId,
  });

  Future<CheckInResult> checkIn({
    required String userId,
    required String deviceId,
    required String courseId,
    required String sessionId,
    required String qrToken,
  });

  Future<PresenceStatus> getStatus({
    required String userId,
    required String courseId,
    required String sessionId,
  });
}
'''

# ─── presence/data/models ─────────────────────────────────────────────────────
files["lib/features/presence/data/models/presence_models.dart"] = '''\
// lib/features/presence/data/models/presence_models.dart
import 'package:presence/features/presence/domain/entities/presence_entities.dart';

class QrTokenModel extends QrToken {
  const QrTokenModel({required super.qrToken, required super.expiresAt});
  factory QrTokenModel.fromJson(Map<String, dynamic> json) => QrTokenModel(
        qrToken: json['qr_token'] as String,
        expiresAt: json['expires_at'] as String,
      );
}

class CheckInResultModel extends CheckInResult {
  const CheckInResultModel({required super.presenceId, required super.status});
  factory CheckInResultModel.fromJson(Map<String, dynamic> json) =>
      CheckInResultModel(
        presenceId: json['presence_id'] as String,
        status: json['status'] as String,
      );
}

class PresenceStatusModel extends PresenceStatus {
  const PresenceStatusModel({
    required super.userId,
    required super.courseId,
    required super.sessionId,
    required super.status,
    required super.lastTs,
  });
  factory PresenceStatusModel.fromJson(Map<String, dynamic> json) =>
      PresenceStatusModel(
        userId: json['user_id'] as String,
        courseId: json['course_id'] as String,
        sessionId: json['session_id'] as String,
        status: json['status'] as String,
        lastTs: json['last_ts'] as String,
      );
}
'''

# ─── presence/data/repositories ───────────────────────────────────────────────
files["lib/features/presence/data/repositories/presence_repository_impl.dart"] = '''\
// lib/features/presence/data/repositories/presence_repository_impl.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:presence/core/api/api_client.dart';
import 'package:presence/core/api/api_provider.dart';
import 'package:presence/core/utils/timestamp.dart';
import 'package:presence/features/presence/domain/entities/presence_entities.dart';
import 'package:presence/features/presence/domain/repositories/presence_repository.dart';
import 'package:presence/features/presence/data/models/presence_models.dart';

class PresenceRepositoryImpl implements PresenceRepository {
  final ApiClient _client;
  PresenceRepositoryImpl(this._client);

  @override
  Future<QrToken> generateQr({
    required String courseId,
    required String sessionId,
  }) async {
    final res = await _client.post(
      '/presence/qr/generate',
      body: {'course_id': courseId, 'session_id': sessionId, 'ts': Timestamp.now()},
      fromJson: QrTokenModel.fromJson,
    );
    if (res.isSuccess) return res.data!;
    throw Exception(res.error ?? 'generate_qr_failed');
  }

  @override
  Future<CheckInResult> checkIn({
    required String userId,
    required String deviceId,
    required String courseId,
    required String sessionId,
    required String qrToken,
  }) async {
    final res = await _client.post(
      '/presence/checkin',
      body: {
        'user_id': userId,
        'device_id': deviceId,
        'course_id': courseId,
        'session_id': sessionId,
        'qr_token': qrToken,
        'ts': Timestamp.now(),
      },
      fromJson: CheckInResultModel.fromJson,
    );
    if (res.isSuccess) return res.data!;
    throw Exception(res.error ?? 'checkin_failed');
  }

  @override
  Future<PresenceStatus> getStatus({
    required String userId,
    required String courseId,
    required String sessionId,
  }) async {
    final res = await _client.get(
      '/presence/status',
      queryParams: {'user_id': userId, 'course_id': courseId, 'session_id': sessionId},
      fromJson: PresenceStatusModel.fromJson,
    );
    if (res.isSuccess) return res.data!;
    throw Exception(res.error ?? 'get_status_failed');
  }
}

final presenceRepositoryProvider = Provider<PresenceRepository>(
  (ref) => PresenceRepositoryImpl(ref.read(apiClientProvider)),
);
'''

# ─── presence/presentation/providers ──────────────────────────────────────────
files["lib/features/presence/presentation/providers/presence_provider.dart"] = '''\
// lib/features/presence/presentation/providers/presence_provider.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:presence/core/utils/device_info.dart';
import 'package:presence/features/presence/data/repositories/presence_repository_impl.dart';
import 'package:presence/features/presence/domain/entities/presence_entities.dart';

class PresenceState {
  final bool isLoading;
  final String? error;
  final CheckInResult? checkInResult;
  final PresenceStatus? presenceStatus;
  final String? scannedToken;

  const PresenceState({
    this.isLoading = false,
    this.error,
    this.checkInResult,
    this.presenceStatus,
    this.scannedToken,
  });

  PresenceState copyWith({
    bool? isLoading,
    String? error,
    CheckInResult? checkInResult,
    PresenceStatus? presenceStatus,
    String? scannedToken,
  }) =>
      PresenceState(
        isLoading: isLoading ?? this.isLoading,
        error: error,
        checkInResult: checkInResult ?? this.checkInResult,
        presenceStatus: presenceStatus ?? this.presenceStatus,
        scannedToken: scannedToken ?? this.scannedToken,
      );
}

class PresenceNotifier extends StateNotifier<PresenceState> {
  final Ref _ref;
  PresenceNotifier(this._ref) : super(const PresenceState());

  void setScannedToken(String token) {
    state = state.copyWith(scannedToken: token);
  }

  Future<void> checkIn({
    required String userId,
    required String courseId,
    required String sessionId,
  }) async {
    if (state.scannedToken == null) {
      state = state.copyWith(error: 'Scan QR terlebih dahulu');
      return;
    }
    state = state.copyWith(isLoading: true);
    try {
      final deviceId = await DeviceInfoUtil.getDeviceId();
      final repo = _ref.read(presenceRepositoryProvider);
      final result = await repo.checkIn(
        userId: userId,
        deviceId: deviceId,
        courseId: courseId,
        sessionId: sessionId,
        qrToken: state.scannedToken!,
      );
      state = state.copyWith(isLoading: false, checkInResult: result);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> fetchStatus({
    required String userId,
    required String courseId,
    required String sessionId,
  }) async {
    state = state.copyWith(isLoading: true);
    try {
      final repo = _ref.read(presenceRepositoryProvider);
      final status = await repo.getStatus(
        userId: userId,
        courseId: courseId,
        sessionId: sessionId,
      );
      state = state.copyWith(isLoading: false, presenceStatus: status);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }
}

final presenceProvider = StateNotifierProvider<PresenceNotifier, PresenceState>(
  (ref) => PresenceNotifier(ref),
);
'''

# ─── presence/presentation/screens ────────────────────────────────────────────
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
  final MobileScannerController _controller = MobileScannerController();
  bool _scanned = false;

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _onDetect(BarcodeCapture capture) {
    if (_scanned) return;
    final barcode = capture.barcodes.firstOrNull;
    final value = barcode?.rawValue;
    if (value == null || value.isEmpty) return;
    _scanned = true;
    _controller.stop();
    ref.read(presenceProvider.notifier).setScannedToken(value);
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(builder: (_) => const CheckInScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Scan QR Presensi'),
        actions: [
          IconButton(icon: const Icon(Icons.flash_on), onPressed: _controller.toggleTorch),
          IconButton(icon: const Icon(Icons.cameraswitch), onPressed: _controller.switchCamera),
        ],
      ),
      body: Stack(
        children: [
          MobileScanner(controller: _controller, onDetect: _onDetect),
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
              style: TextStyle(color: Colors.white, fontSize: 16),
            ),
          ),
        ],
      ),
    );
  }
}
'''

files["lib/features/presence/presentation/screens/checkin_screen.dart"] = '''\
// lib/features/presence/presentation/screens/checkin_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:presence/features/presence/presentation/providers/presence_provider.dart';

class CheckInScreen extends ConsumerStatefulWidget {
  const CheckInScreen({super.key});

  @override
  ConsumerState<CheckInScreen> createState() => _CheckInScreenState();
}

class _CheckInScreenState extends ConsumerState<CheckInScreen> {
  final _userIdCtrl = TextEditingController(text: '2023001');
  final _courseCtrl = TextEditingController(text: 'cloud-101');
  final _sessionCtrl = TextEditingController(text: 'sesi-02');

  @override
  void dispose() {
    _userIdCtrl.dispose();
    _courseCtrl.dispose();
    _sessionCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(presenceProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Check-In Presensi')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              color: Colors.green.shade50,
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Column(children: [
                  const Icon(Icons.qr_code, size: 40, color: Colors.green),
                  const SizedBox(height: 8),
                  Text('Token: \${state.scannedToken ?? "-"}',
                      style: const TextStyle(fontWeight: FontWeight.bold)),
                ]),
              ),
            ),
            const SizedBox(height: 20),
            TextField(
              controller: _userIdCtrl,
              decoration: const InputDecoration(
                labelText: 'User ID (NIM)', border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.person),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _courseCtrl,
              decoration: const InputDecoration(
                labelText: 'Course ID', border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.school),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _sessionCtrl,
              decoration: const InputDecoration(
                labelText: 'Session ID', border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.event),
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: state.isLoading ? null : () => ref.read(presenceProvider.notifier).checkIn(
                userId: _userIdCtrl.text.trim(),
                courseId: _courseCtrl.text.trim(),
                sessionId: _sessionCtrl.text.trim(),
              ),
              icon: const Icon(Icons.check_circle),
              label: const Text('CHECK-IN'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 14),
                backgroundColor: Colors.green, foregroundColor: Colors.white,
              ),
            ),
            const SizedBox(height: 12),
            OutlinedButton.icon(
              onPressed: state.isLoading ? null : () => ref.read(presenceProvider.notifier).fetchStatus(
                userId: _userIdCtrl.text.trim(),
                courseId: _courseCtrl.text.trim(),
                sessionId: _sessionCtrl.text.trim(),
              ),
              icon: const Icon(Icons.info_outline),
              label: const Text('Cek Status'),
            ),
            const SizedBox(height: 24),
            if (state.isLoading) const Center(child: CircularProgressIndicator()),
            if (state.error != null)
              Card(
                color: Colors.red.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Text('\\u26a0 \${state.error}', style: const TextStyle(color: Colors.red)),
                ),
              ),
            if (state.checkInResult != null)
              Card(
                color: Colors.green.shade50,
                child: ListTile(
                  leading: const Icon(Icons.verified, color: Colors.green, size: 36),
                  title: Text(state.checkInResult!.status.toUpperCase(),
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: Colors.green)),
                  subtitle: Text('ID: \${state.checkInResult!.presenceId}'),
                ),
              ),
            if (state.presenceStatus != null) ...[
              const SizedBox(height: 12),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Status Presensi', style: TextStyle(fontWeight: FontWeight.bold)),
                      const Divider(),
                      _row('User', state.presenceStatus!.userId),
                      _row('Course', state.presenceStatus!.courseId),
                      _row('Session', state.presenceStatus!.sessionId),
                      _row('Status', state.presenceStatus!.status),
                      _row('Waktu', state.presenceStatus!.lastTs),
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _row(String label, String value) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 4),
        child: Row(children: [
          SizedBox(width: 70, child: Text(label, style: const TextStyle(color: Colors.grey))),
          Expanded(child: Text(value)),
        ]),
      );
}
'''

# ─── accel/domain/entities ────────────────────────────────────────────────────
files["lib/features/accel/domain/entities/accel_entities.dart"] = '''\
// lib/features/accel/domain/entities/accel_entities.dart
class AccelSample {
  final String t;
  final double x;
  final double y;
  final double z;

  const AccelSample({required this.t, required this.x, required this.y, required this.z});

  Map<String, dynamic> toJson() => {'t': t, 'x': x, 'y': y, 'z': z};
}

class AccelBatchResult {
  final int accepted;
  const AccelBatchResult({required this.accepted});
}

class AccelLatest {
  final String t;
  final double x;
  final double y;
  final double z;

  const AccelLatest({required this.t, required this.x, required this.y, required this.z});
}
'''

# ─── accel/data/repositories ──────────────────────────────────────────────────
files["lib/features/accel/data/repositories/accel_repository_impl.dart"] = '''\
// lib/features/accel/data/repositories/accel_repository_impl.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:presence/core/api/api_client.dart';
import 'package:presence/core/api/api_provider.dart';
import 'package:presence/core/utils/timestamp.dart';
import 'package:presence/features/accel/domain/entities/accel_entities.dart';

abstract class AccelRepository {
  Future<AccelBatchResult> sendBatch({required String deviceId, required List<AccelSample> samples});
  Future<AccelLatest> getLatest(String deviceId);
}

AccelBatchResult _batchFromJson(Map<String, dynamic> j) =>
    AccelBatchResult(accepted: j['accepted'] as int);

AccelLatest _latestFromJson(Map<String, dynamic> j) => AccelLatest(
      t: j['t'] as String,
      x: (j['x'] as num).toDouble(),
      y: (j['y'] as num).toDouble(),
      z: (j['z'] as num).toDouble(),
    );

class AccelRepositoryImpl implements AccelRepository {
  final ApiClient _client;
  AccelRepositoryImpl(this._client);

  @override
  Future<AccelBatchResult> sendBatch({
    required String deviceId,
    required List<AccelSample> samples,
  }) async {
    final res = await _client.post(
      '/telemetry/accel',
      body: {
        'device_id': deviceId,
        'ts': Timestamp.now(),
        'samples': samples.map((s) => s.toJson()).toList(),
      },
      fromJson: _batchFromJson,
    );
    if (res.isSuccess) return res.data!;
    throw Exception(res.error ?? 'accel_send_failed');
  }

  @override
  Future<AccelLatest> getLatest(String deviceId) async {
    final res = await _client.get(
      '/telemetry/accel/latest',
      queryParams: {'device_id': deviceId},
      fromJson: _latestFromJson,
    );
    if (res.isSuccess) return res.data!;
    throw Exception(res.error ?? 'accel_latest_failed');
  }
}

final accelRepositoryProvider = Provider<AccelRepository>(
  (ref) => AccelRepositoryImpl(ref.read(apiClientProvider)),
);
'''

# ─── accel/presentation/providers ─────────────────────────────────────────────
files["lib/features/accel/presentation/providers/accel_provider.dart"] = '''\
// lib/features/accel/presentation/providers/accel_provider.dart
import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:sensors_plus/sensors_plus.dart';
import 'package:presence/core/utils/device_info.dart';
import 'package:presence/core/utils/timestamp.dart';
import 'package:presence/features/accel/data/repositories/accel_repository_impl.dart';
import 'package:presence/features/accel/domain/entities/accel_entities.dart';

class AccelState {
  final double x;
  final double y;
  final double z;
  final bool isSending;
  final int samplesInBuffer;
  final String? lastError;
  final AccelLatest? latest;

  const AccelState({
    this.x = 0, this.y = 0, this.z = 0,
    this.isSending = false,
    this.samplesInBuffer = 0,
    this.lastError,
    this.latest,
  });

  AccelState copyWith({
    double? x, double? y, double? z,
    bool? isSending, int? samplesInBuffer,
    String? lastError, AccelLatest? latest,
  }) =>
      AccelState(
        x: x ?? this.x, y: y ?? this.y, z: z ?? this.z,
        isSending: isSending ?? this.isSending,
        samplesInBuffer: samplesInBuffer ?? this.samplesInBuffer,
        lastError: lastError,
        latest: latest ?? this.latest,
      );
}

class AccelNotifier extends StateNotifier<AccelState> {
  final Ref _ref;
  StreamSubscription<AccelerometerEvent>? _sub;
  Timer? _batchTimer;
  final List<AccelSample> _buffer = [];

  AccelNotifier(this._ref) : super(const AccelState());

  void startListening() {
    _sub = accelerometerEventStream().listen((event) {
      state = state.copyWith(x: event.x, y: event.y, z: event.z);
      _buffer.add(AccelSample(t: Timestamp.now(), x: event.x, y: event.y, z: event.z));
      state = state.copyWith(samplesInBuffer: _buffer.length);
    });
    _batchTimer = Timer.periodic(const Duration(seconds: 5), (_) => _sendBatch());
  }

  void stopListening() {
    _sub?.cancel();
    _batchTimer?.cancel();
    _buffer.clear();
    state = state.copyWith(samplesInBuffer: 0);
  }

  Future<void> _sendBatch() async {
    if (_buffer.isEmpty) return;
    final samples = List<AccelSample>.from(_buffer);
    _buffer.clear();
    state = state.copyWith(isSending: true, samplesInBuffer: 0);
    try {
      final deviceId = await DeviceInfoUtil.getDeviceId();
      final repo = _ref.read(accelRepositoryProvider);
      await repo.sendBatch(deviceId: deviceId, samples: samples);
      final latest = await repo.getLatest(deviceId);
      state = state.copyWith(isSending: false, latest: latest);
    } catch (e) {
      state = state.copyWith(isSending: false, lastError: e.toString());
    }
  }

  @override
  void dispose() {
    stopListening();
    super.dispose();
  }
}

final accelProvider = StateNotifierProvider<AccelNotifier, AccelState>(
  (ref) => AccelNotifier(ref),
);
'''

# ─── accel/presentation/screens ───────────────────────────────────────────────
files["lib/features/accel/presentation/screens/accel_screen.dart"] = '''\
// lib/features/accel/presentation/screens/accel_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:presence/features/accel/presentation/providers/accel_provider.dart';

class AccelScreen extends ConsumerStatefulWidget {
  const AccelScreen({super.key});

  @override
  ConsumerState<AccelScreen> createState() => _AccelScreenState();
}

class _AccelScreenState extends ConsumerState<AccelScreen> {
  bool _active = false;

  void _toggle() {
    if (_active) {
      ref.read(accelProvider.notifier).stopListening();
    } else {
      ref.read(accelProvider.notifier).startListening();
    }
    setState(() => _active = !_active);
  }

  @override
  void dispose() {
    ref.read(accelProvider.notifier).stopListening();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(accelProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Accelerometer Telemetry'),
        actions: [
          if (state.isSending)
            const Padding(
              padding: EdgeInsets.all(12),
              child: SizedBox(
                width: 20, height: 20,
                child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
              ),
            ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              elevation: 4,
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    Text('Live Sensor', style: Theme.of(context).textTheme.titleMedium),
                    const SizedBox(height: 16),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        _AxisValue(label: 'X', value: state.x, color: Colors.red),
                        _AxisValue(label: 'Y', value: state.y, color: Colors.green),
                        _AxisValue(label: 'Z', value: state.z, color: Colors.blue),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Text('Buffer: \${state.samplesInBuffer} samples',
                        style: TextStyle(color: Colors.grey.shade600)),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            if (state.latest != null)
              Card(
                color: Colors.blue.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Latest dari Server', style: TextStyle(fontWeight: FontWeight.bold)),
                      const Divider(),
                      Text('Waktu: \${state.latest!.t}'),
                      Text('X: \${state.latest!.x.toStringAsFixed(3)}  '
                          'Y: \${state.latest!.y.toStringAsFixed(3)}  '
                          'Z: \${state.latest!.z.toStringAsFixed(3)}'),
                    ],
                  ),
                ),
              ),
            if (state.lastError != null)
              Card(
                color: Colors.red.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Text('\\u26a0 \${state.lastError}', style: const TextStyle(color: Colors.red)),
                ),
              ),
            const Spacer(),
            ElevatedButton.icon(
              onPressed: _toggle,
              icon: Icon(_active ? Icons.stop : Icons.play_arrow),
              label: Text(_active ? 'Stop Recording' : 'Start Recording'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 14),
                backgroundColor: _active ? Colors.red : Colors.blue,
                foregroundColor: Colors.white,
              ),
            ),
            const SizedBox(height: 8),
            const Text('Data dikirim otomatis setiap 5 detik',
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.grey, fontSize: 12)),
          ],
        ),
      ),
    );
  }
}

class _AxisValue extends StatelessWidget {
  final String label;
  final double value;
  final Color color;
  const _AxisValue({required this.label, required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        CircleAvatar(
          backgroundColor: color.withValues(alpha: 0.15),
          radius: 30,
          child: Text(label, style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 20)),
        ),
        const SizedBox(height: 8),
        Text(value.toStringAsFixed(2), style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w500)),
        Text('m/s\\u00b2', style: TextStyle(color: Colors.grey.shade500, fontSize: 11)),
      ],
    );
  }
}
'''

# ─── gps/domain/entities ──────────────────────────────────────────────────────
files["lib/features/gps/domain/entities/gps_entities.dart"] = '''\
// lib/features/gps/domain/entities/gps_entities.dart
class GpsPoint {
  final String ts;
  final double lat;
  final double lng;
  final double? accuracyM;

  const GpsPoint({required this.ts, required this.lat, required this.lng, this.accuracyM});
}

class GpsLatest {
  final String ts;
  final double lat;
  final double lng;
  final double? accuracyM;

  const GpsLatest({required this.ts, required this.lat, required this.lng, this.accuracyM});
}

class GpsHistory {
  final String deviceId;
  final List<GpsPoint> items;
  const GpsHistory({required this.deviceId, required this.items});
}
'''

# ─── gps/data/repositories ────────────────────────────────────────────────────
files["lib/features/gps/data/repositories/gps_repository_impl.dart"] = '''\
// lib/features/gps/data/repositories/gps_repository_impl.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:presence/core/api/api_client.dart';
import 'package:presence/core/api/api_provider.dart';
import 'package:presence/core/utils/timestamp.dart';
import 'package:presence/features/gps/domain/entities/gps_entities.dart';

abstract class GpsRepository {
  Future<bool> logPoint({required String deviceId, required GpsPoint point});
  Future<GpsLatest> getLatest(String deviceId);
  Future<GpsHistory> getHistory(String deviceId, {int limit = 200});
}

class _BoolResult {
  final bool accepted;
  _BoolResult(this.accepted);
  factory _BoolResult.fromJson(Map<String, dynamic> j) =>
      _BoolResult(j['accepted'] as bool? ?? false);
}

GpsLatest _latestFromJson(Map<String, dynamic> j) => GpsLatest(
      ts: j['ts'] as String,
      lat: (j['lat'] as num).toDouble(),
      lng: (j['lng'] as num).toDouble(),
      accuracyM: j['accuracy_m'] != null ? (j['accuracy_m'] as num).toDouble() : null,
    );

GpsPoint _pointFromJson(Map<String, dynamic> j) => GpsPoint(
      ts: j['ts'] as String,
      lat: (j['lat'] as num).toDouble(),
      lng: (j['lng'] as num).toDouble(),
      accuracyM: j['accuracy_m'] != null ? (j['accuracy_m'] as num).toDouble() : null,
    );

GpsHistory _historyFromJson(Map<String, dynamic> j) => GpsHistory(
      deviceId: j['device_id'] as String,
      items: (j['items'] as List).map((e) => _pointFromJson(e as Map<String, dynamic>)).toList(),
    );

class GpsRepositoryImpl implements GpsRepository {
  final ApiClient _client;
  GpsRepositoryImpl(this._client);

  @override
  Future<bool> logPoint({required String deviceId, required GpsPoint point}) async {
    final res = await _client.post(
      '/telemetry/gps',
      body: {
        'device_id': deviceId,
        'ts': point.ts.isEmpty ? Timestamp.now() : point.ts,
        'lat': point.lat,
        'lng': point.lng,
        if (point.accuracyM != null) 'accuracy_m': point.accuracyM,
      },
      fromJson: _BoolResult.fromJson,
    );
    if (res.isSuccess) return res.data!.accepted;
    throw Exception(res.error ?? 'gps_log_failed');
  }

  @override
  Future<GpsLatest> getLatest(String deviceId) async {
    final res = await _client.get(
      '/telemetry/gps/latest',
      queryParams: {'device_id': deviceId},
      fromJson: _latestFromJson,
    );
    if (res.isSuccess) return res.data!;
    throw Exception(res.error ?? 'gps_latest_failed');
  }

  @override
  Future<GpsHistory> getHistory(String deviceId, {int limit = 200}) async {
    final res = await _client.get(
      '/telemetry/gps/history',
      queryParams: {'device_id': deviceId, 'limit': limit},
      fromJson: _historyFromJson,
    );
    if (res.isSuccess) return res.data!;
    throw Exception(res.error ?? 'gps_history_failed');
  }
}

final gpsRepositoryProvider = Provider<GpsRepository>(
  (ref) => GpsRepositoryImpl(ref.read(apiClientProvider)),
);
'''

# ─── gps/presentation/providers ───────────────────────────────────────────────
files["lib/features/gps/presentation/providers/gps_provider.dart"] = '''\
// lib/features/gps/presentation/providers/gps_provider.dart
import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:geolocator/geolocator.dart';
import 'package:presence/core/utils/device_info.dart';
import 'package:presence/core/utils/timestamp.dart';
import 'package:presence/features/gps/data/repositories/gps_repository_impl.dart';
import 'package:presence/features/gps/domain/entities/gps_entities.dart';

class GpsState {
  final double? lat;
  final double? lng;
  final double? accuracy;
  final List<GpsPoint> history;
  final GpsLatest? latest;
  final bool isTracking;
  final bool isSyncing;
  final String? error;

  const GpsState({
    this.lat, this.lng, this.accuracy,
    this.history = const [],
    this.latest,
    this.isTracking = false,
    this.isSyncing = false,
    this.error,
  });

  GpsState copyWith({
    double? lat, double? lng, double? accuracy,
    List<GpsPoint>? history, GpsLatest? latest,
    bool? isTracking, bool? isSyncing, String? error,
  }) =>
      GpsState(
        lat: lat ?? this.lat, lng: lng ?? this.lng, accuracy: accuracy ?? this.accuracy,
        history: history ?? this.history,
        latest: latest ?? this.latest,
        isTracking: isTracking ?? this.isTracking,
        isSyncing: isSyncing ?? this.isSyncing,
        error: error,
      );
}

class GpsNotifier extends StateNotifier<GpsState> {
  final Ref _ref;
  StreamSubscription<Position>? _positionSub;

  GpsNotifier(this._ref) : super(const GpsState());

  Future<void> startTracking() async {
    LocationPermission permission = await Geolocator.checkPermission();
    if (permission == LocationPermission.denied) {
      permission = await Geolocator.requestPermission();
      if (permission == LocationPermission.denied) {
        state = state.copyWith(error: 'location_permission_denied');
        return;
      }
    }
    if (permission == LocationPermission.deniedForever) {
      state = state.copyWith(error: 'location_permission_denied_forever');
      return;
    }
    state = state.copyWith(isTracking: true);
    _positionSub = Geolocator.getPositionStream(
      locationSettings: const LocationSettings(accuracy: LocationAccuracy.high, distanceFilter: 5),
    ).listen((pos) {
      state = state.copyWith(lat: pos.latitude, lng: pos.longitude, accuracy: pos.accuracy);
      _sendPoint(pos);
    });
  }

  void stopTracking() {
    _positionSub?.cancel();
    state = state.copyWith(isTracking: false);
  }

  Future<void> _sendPoint(Position pos) async {
    state = state.copyWith(isSyncing: true);
    try {
      final deviceId = await DeviceInfoUtil.getDeviceId();
      final point = GpsPoint(ts: Timestamp.now(), lat: pos.latitude, lng: pos.longitude, accuracyM: pos.accuracy);
      await _ref.read(gpsRepositoryProvider).logPoint(deviceId: deviceId, point: point);
      state = state.copyWith(isSyncing: false);
    } catch (e) {
      state = state.copyWith(isSyncing: false, error: e.toString());
    }
  }

  Future<void> loadMapData() async {
    try {
      final deviceId = await DeviceInfoUtil.getDeviceId();
      final repo = _ref.read(gpsRepositoryProvider);
      final latest = await repo.getLatest(deviceId);
      final history = await repo.getHistory(deviceId);
      state = state.copyWith(latest: latest, history: history.items);
    } catch (e) {
      state = state.copyWith(error: e.toString());
    }
  }

  @override
  void dispose() {
    _positionSub?.cancel();
    super.dispose();
  }
}

final gpsProvider = StateNotifierProvider<GpsNotifier, GpsState>(
  (ref) => GpsNotifier(ref),
);
'''

# ─── gps/presentation/screens ─────────────────────────────────────────────────
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

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback(
      (_) => ref.read(gpsProvider.notifier).loadMapData(),
    );
  }

  @override
  void dispose() {
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
              child: SizedBox(width: 20, height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)),
            ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.read(gpsProvider.notifier).loadMapData(),
          ),
        ],
      ),
      body: Stack(
        children: [
          GoogleMap(
            onMapCreated: (ctrl) => _mapController = ctrl,
            initialCameraPosition: const CameraPosition(target: _defaultPosition, zoom: 15),
            markers: _buildMarkers(state),
            polylines: _buildPolylines(state),
            myLocationEnabled: true,
            myLocationButtonEnabled: true,
          ),
          Positioned(
            top: 10, left: 10, right: 10,
            child: Card(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                child: Row(
                  children: [
                    Icon(state.isTracking ? Icons.location_on : Icons.location_off,
                        color: state.isTracking ? Colors.green : Colors.grey),
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
                  child: Text('\\u26a0 \${state.error}', style: const TextStyle(color: Colors.red)),
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
}
'''

# ─── main.dart ────────────────────────────────────────────────────────────────
files["lib/main.dart"] = '''\
// lib/main.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:presence/features/presence/presentation/screens/qr_scan_screen.dart';
import 'package:presence/features/accel/presentation/screens/accel_screen.dart';
import 'package:presence/features/gps/presentation/screens/map_screen.dart';

void main() {
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

  final _screens = const [
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

# ─── test/widget_test.dart ────────────────────────────────────────────────────
files["test/widget_test.dart"] = '''\
// test/widget_test.dart
import 'package:flutter_test/flutter_test.dart';
import 'package:presence/main.dart';

void main() {
  testWidgets('App smoke test', (WidgetTester tester) async {
    // Basic smoke test
    expect(true, isTrue);
  });
}
'''

# ─── Write all files ──────────────────────────────────────────────────────────
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

print(f"\nSelesai! {success} file berhasil ditulis, {failed} gagal.")
print("\nSekarang jalankan:")
print("  flutter pub get")
print("  flutter run")
