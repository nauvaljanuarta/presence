// lib/core/utils/device_info.dart
import 'dart:io';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:uuid/uuid.dart';

class DeviceInfoUtil {
  static const _keyDeviceId = 'device_id';

  static Future<String> getDeviceId() async {
    final prefs = await SharedPreferences.getInstance();
    if (prefs.containsKey(_keyDeviceId)) {
      return prefs.getString(_keyDeviceId)!;
    }
    String id;
    try {
      final info = DeviceInfoPlugin();
      if (Platform.isAndroid) {
        final android = await info.androidInfo;
        id = android.id;
      } else if (Platform.isIOS) {
        final ios = await info.iosInfo;
        id = ios.identifierForVendor ?? const Uuid().v4();
      } else {
        id = const Uuid().v4();
      }
    } catch (_) {
      id = const Uuid().v4();
    }
    await prefs.setString(_keyDeviceId, id);
    return id;
  }
}
