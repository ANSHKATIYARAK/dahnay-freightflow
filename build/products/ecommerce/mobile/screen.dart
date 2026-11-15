import 'package:flutter/material.dart';

class ECommerceRetailTechMobileScreen extends StatelessWidget {
  const ECommerceRetailTechMobileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFF0F172A),
      appBar: AppBar(
        title: const Text('E-Commerce / RetailTech Mobile Sentinel'),
        backgroundColor: const Color(0xFF1E293B),
      ),
      body: const Center(
        child: Text('Offline Sync Active for E-Commerce / RetailTech', style: TextStyle(color: Colors.white)),
      ),
    );
  }
}
