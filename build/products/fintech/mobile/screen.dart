import 'package:flutter/material.dart';

class FinTechTaxOpsMobileScreen extends StatelessWidget {
  const FinTechTaxOpsMobileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        title: const Text('FinTech / TaxOps Mobile Sentinel'),
        backgroundColor: const Color(0xFF1E293B),
      ),
      body: const Center(
        child: Text('Offline Sync Active for FinTech / TaxOps', style: TextStyle(color: Colors.white)),
      ),
    );
  }
}
