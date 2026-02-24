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
