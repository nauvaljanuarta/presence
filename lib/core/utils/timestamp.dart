// lib/core/utils/timestamp.dart
class Timestamp {
  static String now() => DateTime.now().toUtc().toIso8601String();
  static DateTime parse(String ts) => DateTime.parse(ts).toLocal();
  static String format(DateTime dt) => dt.toUtc().toIso8601String();
}
