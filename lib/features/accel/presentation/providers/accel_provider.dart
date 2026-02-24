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
