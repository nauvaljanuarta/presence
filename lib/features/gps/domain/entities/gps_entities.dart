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
