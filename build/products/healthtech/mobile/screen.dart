import 'package:flutter/material.dart';

class HealthTechClinicOpsMobileScreen extends StatelessWidget {
  const HealthTechClinicOpsMobileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        title: const Text('HealthTech / ClinicOps Mobile Sentinel'),
        backgroundColor: const Color(0xFF1E293B),
      ),
      body: const Center(
        child: Text('Offline Sync Active for HealthTech / ClinicOps', style: TextStyle(color: Colors.white)),
      ),
    );
  }
}
