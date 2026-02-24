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
