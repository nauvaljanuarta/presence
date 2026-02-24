// lib/core/api/api_client.dart
import 'package:dio/dio.dart';
import 'package:presence/core/api/api_response.dart';

class ApiClient {
  static const String _baseUrl =
      'https://script.google.com/macros/s/YOUR_DEPLOYMENT_ID/exec';

  late final Dio _dio;

  ApiClient() {
    _dio = Dio(BaseOptions(
      baseUrl: _baseUrl,
      connectTimeout: const Duration(seconds: 15),
      receiveTimeout: const Duration(seconds: 15),
      headers: {'Content-Type': 'application/json'},
    ));
    _dio.interceptors.add(LogInterceptor(
      requestBody: true,
      responseBody: true,
      error: true,
    ));
  }

  Future<ApiResponse<T>> get<T>(
    String path, {
    Map<String, dynamic>? queryParams,
    required T Function(Map<String, dynamic>) fromJson,
  }) async {
    try {
      final response = await _dio.get(path, queryParameters: queryParams);
      return ApiResponse.fromJson(response.data, fromJson);
    } on DioException catch (e) {
      return ApiResponse.error(_dioErrorMessage(e));
    }
  }

  Future<ApiResponse<T>> post<T>(
    String path, {
    required Map<String, dynamic> body,
    required T Function(Map<String, dynamic>) fromJson,
  }) async {
    try {
      final response = await _dio.post(path, data: body);
      return ApiResponse.fromJson(response.data, fromJson);
    } on DioException catch (e) {
      return ApiResponse.error(_dioErrorMessage(e));
    }
  }

  String _dioErrorMessage(DioException e) {
    switch (e.type) {
      case DioExceptionType.connectionTimeout:
      case DioExceptionType.receiveTimeout:
        return 'connection_timeout';
      case DioExceptionType.badResponse:
        return 'server_error: \${e.response?.statusCode}';
      default:
        return e.message ?? 'unknown_error';
    }
  }
}
