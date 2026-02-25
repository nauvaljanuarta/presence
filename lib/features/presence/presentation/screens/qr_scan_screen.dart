// lib/features/presence/presentation/screens/qr_scan_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:presence/features/presence/presentation/providers/presence_provider.dart';
import 'package:presence/features/presence/presentation/screens/checkin_screen.dart';

class QrScanScreen extends ConsumerStatefulWidget {
  const QrScanScreen({super.key});

  @override
  ConsumerState<QrScanScreen> createState() => _QrScanScreenState();
}

class _QrScanScreenState extends ConsumerState<QrScanScreen> {
  MobileScannerController? _controller;
  bool _scanned = false;
  bool _cameraError = false;

  @override
  void initState() {
    super.initState();
    _initCamera();
  }

  void _initCamera() {
    try {
      _controller = MobileScannerController(
        detectionSpeed: DetectionSpeed.normal,
        facing: CameraFacing.back,
      );
    } catch (e) {
      if (mounted) setState(() => _cameraError = true);
    }
  }

  @override
  void dispose() {
    _controller?.dispose();
    super.dispose();
  }

  void _onDetect(BarcodeCapture capture) {
    if (_scanned) return;
    final barcode = capture.barcodes.firstOrNull;
    final value = barcode?.rawValue;
    if (value == null || value.isEmpty) return;

    _scanned = true;
    _controller?.stop();

    ref.read(presenceProvider.notifier).setScannedToken(value);
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(builder: (_) => const CheckInScreen()),
    );
  }

  @override
  Widget build(BuildContext context) {
    if (_cameraError) {
      return Scaffold(
        appBar: AppBar(title: const Text('Scan QR Presensi')),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.camera_alt_outlined, size: 64, color: Colors.grey),
              const SizedBox(height: 16),
              const Text('Kamera tidak tersedia', style: TextStyle(fontSize: 16)),
              const SizedBox(height: 8),
              const Text('Izinkan akses kamera di pengaturan HP',
                  style: TextStyle(color: Colors.grey)),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () {
                  setState(() {
                    _cameraError = false;
                    _scanned = false;
                  });
                  _initCamera();
                },
                child: const Text('Coba Lagi'),
              ),
              const SizedBox(height: 12),
              // Input manual token jika kamera gagal
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 32),
                child: _ManualTokenInput(),
              ),
            ],
          ),
        ),
      );
    }

    if (_controller == null) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('Scan QR Presensi'),
        actions: [
          IconButton(
            icon: const Icon(Icons.flash_on),
            onPressed: _controller!.toggleTorch,
          ),
          IconButton(
            icon: const Icon(Icons.cameraswitch),
            onPressed: _controller!.switchCamera,
          ),
        ],
      ),
      body: Stack(
        children: [
          MobileScanner(
            controller: _controller!,
            onDetect: _onDetect,
            errorBuilder: (context, error, child) {
              return Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.error_outline, size: 64, color: Colors.red),
                    const SizedBox(height: 16),
                    Text('Error kamera: \${error.errorCode}',
                        style: const TextStyle(color: Colors.red)),
                  ],
                ),
              );
            },
          ),
          Center(
            child: Container(
              width: 250,
              height: 250,
              decoration: BoxDecoration(
                border: Border.all(color: Colors.greenAccent, width: 3),
                borderRadius: BorderRadius.circular(12),
              ),
            ),
          ),
          const Positioned(
            bottom: 40, left: 0, right: 0,
            child: Text(
              'Arahkan kamera ke QR Code di kelas',
              textAlign: TextAlign.center,
              style: TextStyle(color: Colors.white, fontSize: 16,
                  shadows: [Shadow(blurRadius: 4, color: Colors.black)]),
            ),
          ),
        ],
      ),
    );
  }
}

// Widget input manual token jika kamera tidak bisa digunakan
class _ManualTokenInput extends ConsumerStatefulWidget {
  @override
  ConsumerState<_ManualTokenInput> createState() => _ManualTokenInputState();
}

class _ManualTokenInputState extends ConsumerState<_ManualTokenInput> {
  final _ctrl = TextEditingController();

  @override
  void dispose() {
    _ctrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        const Divider(),
        const Text('Atau masukkan token manual:',
            style: TextStyle(color: Colors.grey, fontSize: 12)),
        const SizedBox(height: 8),
        TextField(
          controller: _ctrl,
          decoration: const InputDecoration(
            labelText: 'QR Token',
            border: OutlineInputBorder(),
            isDense: true,
          ),
        ),
        const SizedBox(height: 8),
        ElevatedButton(
          onPressed: () {
            final token = _ctrl.text.trim();
            if (token.isEmpty) return;
            ref.read(presenceProvider.notifier).setScannedToken(token);
            Navigator.of(context).pushReplacement(
              MaterialPageRoute(builder: (_) => const CheckInScreen()),
            );
          },
          child: const Text('Gunakan Token Ini'),
        ),
      ],
    );
  }
}
