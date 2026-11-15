import 'package:flutter/material.dart';

class DevOpsCloudInfraMobileScreen extends StatelessWidget {
  const DevOpsCloudInfraMobileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        title: const Text('DevOps / Cloud Infra Mobile Sentinel'),
        backgroundColor: const Color(0xFF1E293B),
      ),
      body: const Center(
        child: Text('Offline Sync Active for DevOps / Cloud Infra', style: TextStyle(color: Colors.white)),
      ),
    );
  }
}
