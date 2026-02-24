// lib/features/accel/presentation/screens/accel_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:presence/features/accel/presentation/providers/accel_provider.dart';

class AccelScreen extends ConsumerStatefulWidget {
  const AccelScreen({super.key});

  @override
  ConsumerState<AccelScreen> createState() => _AccelScreenState();
}

class _AccelScreenState extends ConsumerState<AccelScreen> {
  bool _active = false;

  void _toggle() {
    if (_active) {
      ref.read(accelProvider.notifier).stopListening();
    } else {
      ref.read(accelProvider.notifier).startListening();
    }
    setState(() => _active = !_active);
  }

  @override
  void dispose() {
    ref.read(accelProvider.notifier).stopListening();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(accelProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Accelerometer Telemetry'),
        actions: [
          if (state.isSending)
            const Padding(
              padding: EdgeInsets.all(12),
              child: SizedBox(
                width: 20, height: 20,
                child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
              ),
            ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              elevation: 4,
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  children: [
                    Text('Live Sensor', style: Theme.of(context).textTheme.titleMedium),
                    const SizedBox(height: 16),
                    Row(
                      mainAxisAlignment: MainAxisAlignment.spaceAround,
                      children: [
                        _AxisValue(label: 'X', value: state.x, color: Colors.red),
                        _AxisValue(label: 'Y', value: state.y, color: Colors.green),
                        _AxisValue(label: 'Z', value: state.z, color: Colors.blue),
                      ],
                    ),
                    const SizedBox(height: 12),
                    Text('Buffer: \${state.samplesInBuffer} samples',
                        style: TextStyle(color: Colors.grey.shade600)),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            if (state.latest != null)
              Card(
                color: Colors.blue.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text('Latest dari Server', style: TextStyle(fontWeight: FontWeight.bold)),
                      const Divider(),
                      Text('Waktu: \${state.latest!.t}'),
                      Text('X: \${state.latest!.x.toStringAsFixed(3)}  '
                          'Y: \${state.latest!.y.toStringAsFixed(3)}  '
                          'Z: \${state.latest!.z.toStringAsFixed(3)}'),
                    ],
                  ),
                ),
              ),
            if (state.lastError != null)
              Card(
                color: Colors.red.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(12),
                  child: Text('\u26a0 \${state.lastError}', style: const TextStyle(color: Colors.red)),
                ),
              ),
            const Spacer(),
            ElevatedButton.icon(
              onPressed: _toggle,
              icon: Icon(_active ? Icons.stop : Icons.play_arrow),
              label: Text(_active ? 'Stop Recording' : 'Start Recording'),
              style: ElevatedButton.styleFrom(
                padding: const EdgeInsets.symmetric(vertical: 14),
                backgroundColor: _active ? Colors.red : Colors.blue,
                foregroundColor: Colors.white,
              ),
            ),
            const SizedBox(height: 8),
            const Text('Data dikirim otomatis setiap 5 detik',
                textAlign: TextAlign.center,
                style: TextStyle(color: Colors.grey, fontSize: 12)),
          ],
        ),
      ),
    );
  }
}

class _AxisValue extends StatelessWidget {
  final String label;
  final double value;
  final Color color;
  const _AxisValue({required this.label, required this.value, required this.color});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        CircleAvatar(
          backgroundColor: color.withValues(alpha: 0.15),
          radius: 30,
          child: Text(label, style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 20)),
        ),
        const SizedBox(height: 8),
        Text(value.toStringAsFixed(2), style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w500)),
        Text('m/s\u00b2', style: TextStyle(color: Colors.grey.shade500, fontSize: 11)),
      ],
    );
  }
}
