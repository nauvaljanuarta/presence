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
