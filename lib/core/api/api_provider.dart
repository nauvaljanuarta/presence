// lib/core/api/api_provider.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:presence/core/api/api_client.dart';

final apiClientProvider = Provider<ApiClient>((ref) => ApiClient());
