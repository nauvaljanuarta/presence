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
