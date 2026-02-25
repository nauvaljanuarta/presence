// lib/features/gps/presentation/screens/map_screen.dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_maps_flutter/google_maps_flutter.dart';
import 'package:presence/features/gps/presentation/providers/gps_provider.dart';

class MapScreen extends ConsumerStatefulWidget {
  const MapScreen({super.key});

  @override
  ConsumerState<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends ConsumerState<MapScreen> {
  GoogleMapController? _mapController;
  static const _defaultPosition = LatLng(-7.2575, 112.7521);
  bool _mapError = false;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (mounted) {
        ref.read(gpsProvider.notifier).loadMapData();
      }
    });
  }

  @override
  void dispose() {
    _mapController?.dispose();
    ref.read(gpsProvider.notifier).stopTracking();
    super.dispose();
  }

  Set<Marker> _buildMarkers(GpsState state) {
    final markers = <Marker>{};
    if (state.latest != null) {
      markers.add(Marker(
        markerId: const MarkerId('latest'),
        position: LatLng(state.latest!.lat, state.latest!.lng),
        infoWindow: InfoWindow(title: 'Posisi Terbaru', snippet: state.latest!.ts),
        icon: BitmapDescriptor.defaultMarkerWithHue(BitmapDescriptor.hueAzure),
      ));
    }
    if (state.lat != null && state.lng != null) {
      markers.add(Marker(
        markerId: const MarkerId('live'),
        position: LatLng(state.lat!, state.lng!),
        infoWindow: const InfoWindow(title: 'Lokasi Saya (Live)'),
      ));
    }
    return markers;
  }

  Set<Polyline> _buildPolylines(GpsState state) {
    if (state.history.length < 2) return {};
    return {
      Polyline(
        polylineId: const PolylineId('track'),
        points: state.history.map((p) => LatLng(p.lat, p.lng)).toList(),
        color: Colors.blue,
        width: 4,
      ),
    };
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(gpsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('GPS Tracking'),
        actions: [
          if (state.isSyncing)
            const Padding(
              padding: EdgeInsets.all(12),
              child: SizedBox(
                width: 20,
                height: 20,
                child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
              ),
            ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => ref.read(gpsProvider.notifier).loadMapData(),
          ),
        ],
      ),
      body: Stack(
        children: [
          // Tampilkan error jika Maps gagal load
          if (_mapError)
            Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.map_outlined, size: 64, color: Colors.grey),
                  const SizedBox(height: 16),
                  const Text('Google Maps gagal dimuat.',
                      style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  const Padding(
                    padding: EdgeInsets.symmetric(horizontal: 32),
                    child: Text(
                      'Pastikan Google Maps API Key sudah diisi di AndroidManifest.xml',
                      textAlign: TextAlign.center,
                      style: TextStyle(color: Colors.grey),
                    ),
                  ),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () => setState(() => _mapError = false),
                    child: const Text('Coba Lagi'),
                  ),
                ],
              ),
            )
          else
            // Google Map dengan error handling
            _buildMap(state),

          // Info koordinat GPS
          Positioned(
            top: 10, left: 10, right: 10,
            child: Card(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                child: Row(
                  children: [
                    Icon(
                      state.isTracking ? Icons.location_on : Icons.location_off,
                      color: state.isTracking ? Colors.green : Colors.grey,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        state.lat != null
                            ? '\${state.lat!.toStringAsFixed(5)}, \${state.lng!.toStringAsFixed(5)}'
                                ' \u00b1\${state.accuracy?.toStringAsFixed(0) ?? "?"}m'
                            : 'GPS belum aktif',
                        style: const TextStyle(fontSize: 13),
                      ),
                    ),
                    Text('\${state.history.length} titik',
                        style: TextStyle(color: Colors.grey.shade600, fontSize: 12)),
                  ],
                ),
              ),
            ),
          ),

          if (state.error != null)
            Positioned(
              bottom: 80, left: 10, right: 10,
              child: Card(
                color: Colors.red.shade50,
                child: Padding(
                  padding: const EdgeInsets.all(10),
                  child: Text('\u26a0 \${state.error}',
                      style: const TextStyle(color: Colors.red)),
                ),
              ),
            ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: () {
          if (state.isTracking) {
            ref.read(gpsProvider.notifier).stopTracking();
          } else {
            ref.read(gpsProvider.notifier).startTracking();
          }
        },
        icon: Icon(state.isTracking ? Icons.stop : Icons.play_arrow),
        label: Text(state.isTracking ? 'Stop' : 'Start Tracking'),
        backgroundColor: state.isTracking ? Colors.red : Colors.blue,
      ),
    );
  }

  Widget _buildMap(GpsState state) {
    try {
      return GoogleMap(
        onMapCreated: (ctrl) => _mapController = ctrl,
        initialCameraPosition: const CameraPosition(target: _defaultPosition, zoom: 15),
        markers: _buildMarkers(state),
        polylines: _buildPolylines(state),
        myLocationEnabled: true,
        myLocationButtonEnabled: true,
        onCameraIdle: () {},
      );
    } catch (e) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (mounted) setState(() => _mapError = true);
      });
      return const SizedBox.shrink();
    }
  }
}
