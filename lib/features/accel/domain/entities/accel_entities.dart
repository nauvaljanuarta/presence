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
