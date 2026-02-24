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
