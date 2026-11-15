# Industry Case Studies: Intelligent Document Processing in Freight & 3PL Logistics

**Case Studies Analyzed:** Rossum (NFI Industries & Fugro), Klippa (FIATA Bill of Lading), and Flexport (Automated Customs & Manifest Ingestion)  
**Target Enterprise Application:** DahNAY Logistics (Chennai & Tuticorin EXIM Operations)  

---

## 1. Case Study 1: Rossum & Enterprise 3PL Invoicing (NFI Industries)

### A. The Operational Bottleneck
* **Company Profile:** NFI Industries (Top-10 North American 3PL and global freight forwarder managing over 50,000 active carrier contracts).
* **The Problem:** 
  - Processing hundreds of thousands of inbound freight invoices and shipping documents per year across thousands of independent transport operators.
  - Invoices arrived in unpredictable email attachments (single PDFs containing 5 invoices, multi-page manifests with mixed packing lists).
  - Manual processing took **3 to 8 minutes per invoice**, creating a multi-week payment lag, demurrage penalties, and carrier billing disputes.

### B. The AI Solution
1. **Document Package Splitting:** Implemented deep-learning page-splitter models that inspect visual headers to partition a 20-page bulk attachment into discrete jobs.
2. **Cognitive Contextual Extraction:** Replaced rigid coordinate-based OCR templates with transformer-based cognitive extractors capable of parsing variable freight surcharges (BAF, CAF, THC, detention).
3. **Automated Two-Way / Three-Way ERP Matching:** Matched extracted line-item amounts against internal rate agreements and purchase orders in SAP/Coupa.

### C. Measurable Business Outcomes
* **Cycle Time Reduction:** Document turnaround collapsed from **4.5 minutes down to 32 seconds** per file.
* **Straight-Through Processing (STP):** Over 75% of clean documents routed directly into ERP without any manual intervention.
* **Error Elimination:** Overbilled surcharges and duplicate invoice submissions were auto-flagged, saving over $1.2M annually in erroneous freight disbursements.

---

## 2. Case Study 2: Klippa DocHorizon for Maritime Bills of Lading & FIATA FBL

### A. The Operational Bottleneck
* **Industry Segment:** Maritime freight forwarders and customs house agents (CHAs).
* **The Problem:** 
  - Bills of Lading (BOLs) act as negotiable titles of goods. Inaccuracies in consignee names, notify parties, or container marks trigger carrier amendment fees ($50–$150 USD per BL) and port customs holds.
  - Documents arrive as scanned physical paper with watermarks, rubber validation stamps, and handwritten weight adjustments.

### B. The AI Solution
1. **Visual Pre-Processing:** Automatic perspective skew correction, contrast normalization, and stamp removal to ensure high-fidelity text recognition.
2. **Hierarchical Container Extraction:** Dedicated table-parsing neural networks that associate each container number with its corresponding seal, package count, tare weight, and gross weight.
3. **Automated Export Payload:** Output converted directly into UN/EDIFACT (IFTMIN, IFTSTA) and CargoWise Universal XML.

### C. Measurable Business Outcomes
* **Discrepancy Elimination:** Prevented >92% of BL amendments by cross-checking customer shipping instructions against booking confirmations before carrier filing.
* **Turnaround Acceleration:** Enabled same-day customs pre-filing for expedited ocean freight.

---

## 3. Case Study 3: Flexport's Automated Customs & Tariff Classification Engine

### A. The Operational Bottleneck
* **Company Profile:** Flexport (Digital freight forwarder managing billions in transpacific and transatlantic cargo).
* **The Problem:**
  - Matching commercial invoice descriptions (e.g., *"Men's 100% woven cotton sports jerseys"*) to correct 6–10 digit Harmonized Tariff Schedule (HTS) codes.
  - Misclassification leads to customs audits, duty penalties, and border impoundments.

### B. The Solution & Architecture
* Developed an LLM-assisted classification engine with embedding similarity search over historical customs rulings (CROSS database).
* Built a reconciliation gatekeeper: when a shipper's packing list total weight conflicts with the bill of lading, the system flags the exact difference with a calculated risk score.

---

## 4. Key Takeaways for DahNAY Logistics Implementation

From these global successes, the blueprint for DahNAY is clear:
1. **Never build a generic OCR tool:** Build an **EXIM-specific reconciliation gatekeeper** that speaks the language of shipping lines (VGM, TEU, POL/POD, UN/LOCODE, ISO 6346).
2. **Solve the Invoice Pre-Fill directly:** Freight forwarders don't just want data extracted; they want the **Commercial Invoice pre-calculated** (Ocean Freight in USD converted to INR at live exchange rates, Terminal Handling Charges, BL documentation fees, and GST).
3. **Seamless ERP Integration:** The system must spit out standard CargoWise One XML and Logisys-ready CSV formats so DahNAY staff never touch manual entry.
