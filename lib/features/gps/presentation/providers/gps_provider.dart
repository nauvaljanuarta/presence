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
