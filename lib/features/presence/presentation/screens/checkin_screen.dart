// lib/features/presence/presentation/screens/checkin_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:presence/features/presence/presentation/providers/presence_provider.dart';

class CheckInScreen extends ConsumerStatefulWidget {
  const CheckInScreen({super.key});

  @override
  ConsumerState<CheckInScreen> createState() => _CheckInScreenState();
}

class _CheckInScreenState extends ConsumerState<CheckInScreen> {
  final _userIdCtrl = TextEditingController(text: '2023001');
  final _courseCtrl = TextEditingController(text: 'cloud-101');
  final _sessionCtrl = TextEditingController(text: 'sesi-02');

  @override
  void dispose() {
    _userIdCtrl.dispose();
    _courseCtrl.dispose();
    _sessionCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(presenceProvider);

    return Scaffold(
      appBar: AppBar(title: const Text('Check-In Presensi')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              color: Colors.green.shade50,
              child: Padding(
                padding: const EdgeInsets.all(12),
                child: Column(children: [
                  const Icon(Icons.qr_code, size: 40, color: Colors.green),
                  const SizedBox(height: 8),
                  Text('Token: \${state.scannedToken ?? "-"}',
                      style: const TextStyle(fontWeight: FontWeight.bold)),
                ]),
              ),
            ),
            const SizedBox(height: 20),
            TextField(
              controller: _userIdCtrl,
              decoration: const InputDecoration(
                labelText: 'User ID (NIM)', border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.person),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _courseCtrl,
              decoration: const InputDecoration(
                labelText: 'Course ID', border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.school),
              ),
            ),
            const SizedBox(height: 12),
            TextField(
              controller: _sessionCtrl,
              decoration: const InputDecoration(
                labelText: 'Session ID', border: OutlineInputBorder(),
                prefixIcon: Icon(Icons.event),
              ),
            ),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              onPressed: state.isLoading ? null : () => ref.read(presenceProvider.notifier).checkIn(
                userId: _userIdCtrl.text.trim(),
                courseId: _courseCtrl.text.trim(),
                sessionId: _sessionCtrl.text.trim(),
              ),
              icon: const Icon(Icons.check_circle),
              label: const Text('CHECK-IN'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 14),
                backgroundColor: Colors.green, foregroundColor: Colors.white,
              ),
            ),
            const SizedBox(height: 12),
            OutlinedButton.icon(
              onPressed: state.isLoading ? null : () => ref.read(presenceProvider.notifier).fetchStatus(
                userId: _userIdCtrl.text.trim(),
                courseId: _courseCtrl.text.trim(),
                sessionId: _sessionCtrl.text.trim(),
              ),
              icon: const Icon(Icons.info_outline),
              label: const Text('Cek Status'),
            ),
            const SizedBox(height: 24),
            if (state.isLoading) const Center(child: CircularProgressIndicator()),
            if (state.error != null)
              Card(
                color: Colors.red.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Text('\u26a0 \${state.error}', style: const TextStyle(color: Colors.red)),
                ),
              ),
            if (state.checkInResult != null)
              Card(
                color: Colors.green.shade50,
                child: ListTile(
                  leading: const Icon(Icons.verified, color: Colors.green, size: 36),
                  title: Text(state.checkInResult!.status.toUpperCase(),
                      style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 18, color: Colors.green)),
                  subtitle: Text('ID: \${state.checkInResult!.presenceId}'),
                ),
              ),
            if (state.presenceStatus != null) ...[
              const SizedBox(height: 12),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Status Presensi', style: TextStyle(fontWeight: FontWeight.bold)),
                      const Divider(),
                      _row('User', state.presenceStatus!.userId),
                      _row('Course', state.presenceStatus!.courseId),
                      _row('Session', state.presenceStatus!.sessionId),
                      _row('Status', state.presenceStatus!.status),
                      _row('Waktu', state.presenceStatus!.lastTs),
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _row(String label, String value) => Padding(
        padding: const EdgeInsets.symmetric(vertical: 4),
        child: Row(children: [
          SizedBox(width: 70, child: Text(label, style: const TextStyle(color: Colors.grey))),
          Expanded(child: Text(value)),
        ]),
      );
}
