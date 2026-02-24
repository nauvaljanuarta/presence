// lib/features/presence/presentation/providers/presence_provider.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:presence/core/utils/device_info.dart';
import 'package:presence/features/presence/data/repositories/presence_repository_impl.dart';
import 'package:presence/features/presence/domain/entities/presence_entities.dart';

class PresenceState {
  final bool isLoading;
  final String? error;
  final CheckInResult? checkInResult;
  final PresenceStatus? presenceStatus;
  final String? scannedToken;

  const PresenceState({
    this.isLoading = false,
    this.error,
    this.checkInResult,
    this.presenceStatus,
    this.scannedToken,
  });

  PresenceState copyWith({
    bool? isLoading,
    String? error,
    CheckInResult? checkInResult,
    PresenceStatus? presenceStatus,
    String? scannedToken,
  }) =>
      PresenceState(
        isLoading: isLoading ?? this.isLoading,
        error: error,
        checkInResult: checkInResult ?? this.checkInResult,
        presenceStatus: presenceStatus ?? this.presenceStatus,
        scannedToken: scannedToken ?? this.scannedToken,
      );
}

class PresenceNotifier extends StateNotifier<PresenceState> {
  final Ref _ref;
  PresenceNotifier(this._ref) : super(const PresenceState());

  void setScannedToken(String token) {
    state = state.copyWith(scannedToken: token);
  }

  Future<void> checkIn({
    required String userId,
    required String courseId,
    required String sessionId,
  }) async {
    if (state.scannedToken == null) {
      state = state.copyWith(error: 'Scan QR terlebih dahulu');
      return;
    }
    state = state.copyWith(isLoading: true);
    try {
      final deviceId = await DeviceInfoUtil.getDeviceId();
      final repo = _ref.read(presenceRepositoryProvider);
      final result = await repo.checkIn(
        userId: userId,
        deviceId: deviceId,
        courseId: courseId,
        sessionId: sessionId,
        qrToken: state.scannedToken!,
      );
      state = state.copyWith(isLoading: false, checkInResult: result);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }

  Future<void> fetchStatus({
    required String userId,
    required String courseId,
    required String sessionId,
  }) async {
    state = state.copyWith(isLoading: true);
    try {
      final repo = _ref.read(presenceRepositoryProvider);
      final status = await repo.getStatus(
        userId: userId,
        courseId: courseId,
        sessionId: sessionId,
      );
      state = state.copyWith(isLoading: false, presenceStatus: status);
    } catch (e) {
      state = state.copyWith(isLoading: false, error: e.toString());
    }
  }
}

final presenceProvider = StateNotifierProvider<PresenceNotifier, PresenceState>(
  (ref) => PresenceNotifier(ref),
);
