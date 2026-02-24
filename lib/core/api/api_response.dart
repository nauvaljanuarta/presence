// lib/core/api/api_response.dart
class ApiResponse<T> {
  final bool ok;
  final T? data;
  final String? error;

  const ApiResponse({required this.ok, this.data, this.error});

  factory ApiResponse.fromJson(
    dynamic json,
    T Function(Map<String, dynamic>) fromJson,
  ) {
    final map = json as Map<String, dynamic>;
    final ok = map['ok'] as bool? ?? false;
    if (ok && map['data'] != null) {
      return ApiResponse(ok: true, data: fromJson(map['data']));
    } else {
      return ApiResponse(ok: false, error: map['error'] as String?);
    }
  }

  factory ApiResponse.error(String message) {
    return ApiResponse(ok: false, error: message);
  }

  bool get isSuccess => ok && data != null;
}
