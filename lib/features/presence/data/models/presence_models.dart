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
