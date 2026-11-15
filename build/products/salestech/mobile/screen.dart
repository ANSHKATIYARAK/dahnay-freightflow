import 'package:flutter/material.dart';

class SalesTechB2BGrowthMobileScreen extends StatelessWidget {
  const SalesTechB2BGrowthMobileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        title: const Text('SalesTech / B2B Growth Mobile Sentinel'),
        backgroundColor: const Color(0xFF1E293B),
      ),
      body: const Center(
        child: Text('Offline Sync Active for SalesTech / B2B Growth', style: TextStyle(color: Colors.white)),
      ),
    );
  }
}
