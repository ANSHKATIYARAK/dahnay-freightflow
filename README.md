# DahNAY FreightFlow: Enterprise EXIM Document-to-Invoice & CargoWise One EDI Bridge

**DahNAY FreightFlow** is an enterprise-grade logistics automation platform built to resolve critical documentation-to-invoice pre-fill bottlenecks for DahNAY Logistics and Indian EXIM freight forwarders (Chennai & Tuticorin ports).

It automates the ingestion of unstructured and semi-structured shipping instructions (Excel, PDF, JSON, Plain Text), runs deterministic ISO 6346 Modulo 11 check-digit audits, reconciles declared gross weights against carrier slot limits (IMO SOLAS VGM compliance), pre-fills GST-compliant commercial freight invoices, and formats production-ready **CargoWise One `UniversalShipment` XML** and **DCSA eBL v3.0 standard JSON**.

---

## ⚡ Key Capabilities

1. **Multi-Format Shipping Instruction Parsing:**
   - Ingests `.xlsx`, `.xls`, `.pdf`, `.json`, and `.txt` shipping instructions.
   - Extracts Shipper IEC/GSTIN, Consignee Tax ID, Carrier Line, Vessel, Voyage, POL (e.g. `INMAA`), POD (e.g. `AEJEA`), cargo particulars, containers, and gross weights.

2. **Deterministic Checksum & Integrity Gate:**
   - **ISO 6346 Modulo 11 Algorithm:** Mathematical validation of container equipment serials. Auto-detects single-character typographical errors and suggests valid check digits.
   - **SOLAS VGM Slot Reconciliation:** Compares declaration weight against carrier master booking limits, flagging overweight allocations (+2,800 kg shut-out risks).

3. **Commercial Freight Invoice Pre-Fill:**
   - Multi-currency rate calculation (USD ocean freight converted to INR at live exchange rates).
   - Automated breakdown of THC, documentation fees, and BAF fuel surcharges.
   - Statutory Indian GST computation (CGST @ 9% + SGST @ 9%).

4. **Native CargoWise One & DCSA Standards Bridge:**
   - **CargoWise One eAdaptor:** Emits validated `UniversalShipment` XML adhering to the UniversalInterchange 1.1 schema.
   - **DCSA eBL v3.0 Standard:** Emits electronic Bill of Lading JSON for carrier-neutral interoperability.

5. **Mission-Critical Operations Platform:**
   - High-density dark slate UI designed for logistics operations teams.
   - Real-time communication with SQLite backend (`freightflow.db`).
   - 1-click ISO check-digit auto-correction and operations manager exception waiver logging.
   - Complete immutable audit trail tracking all document lifecycle events.

---

## 🏗️ Architecture

```
[ Inbound Shipping Instructions ]
 (.xlsx / .pdf / .json / .txt)
                │
                ▼
┌─────────────────────────────────┐
│ MultiFormatSINormalizer         │ ── Regex & Tabular Entity Extraction
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│ ContainerValidator (ISO 6346)   │ ── Modulo 11 Check-Digit Verification
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│ DahNAYReconciliationEngine      │ ── Audits vs CargoWise Master Booking (SOLAS VGM)
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│ CommercialInvoiceGenerator      │ ── GST & Currency Conversion Engine
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│ CargoWiseUniversalExporter      │ ── Generates UniversalShipment XML & DCSA eBL 3.0
└───────────────┬─────────────────┘
                ▼
┌─────────────────────────────────┐
│ SQLite Persistence Layer        │ ── freightflow.db (Dossier, Containers, Audit Logs)
└─────────────────────────────────┘
```

---

## 🚀 Quick Start Guide

### 1. Installation
Clone the repository and install dependencies:
```bash
git clone https://github.com/ANSHKATIYARAK/dahnay-freightflow.git
cd dahnay-freightflow
python -m venv .venv
.venv\Scripts\activate  # On Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Run the Operations CLI
Execute an end-to-end document extraction, audit, and CargoWise XML export in < 1 second:
```bash
python dahnay_logistics/run.py
```

### 3. Launch the Web Operations Platform & API
Start the FastAPI server:
```bash
python run_studio.py
```
- **Web UI:** [http://localhost:8000/dahnay](http://localhost:8000/dahnay)
- **Active Shipments API:** [http://localhost:8000/api/v1/shipments](http://localhost:8000/api/v1/shipments)
- **Portfolio Hub:** [http://localhost:8000/portfolio](http://localhost:8000/portfolio)

---

## 🧪 Test Suite

Run the automated test suites:
```bash
# 1. DahNAY Engine, Checksums, and Standards Pipeline Tests
python tests/test_dahnay_engine.py

# 2. Real Backend SQLite Persistence & REST API Integration Tests
python tests/test_real_backend.py
```

---

## 📂 Repository Structure

```
├── dahnay_logistics/
│   ├── api/                 # FastAPI REST API routes (/api/v1/shipments)
│   ├── backend/             # Service layer & business logic
│   ├── data/                # SQLite database (freightflow.db)
│   ├── datasets/            # Sample SI files (.xlsx, .json, .txt) & booking specs
│   ├── db/                  # Relational schema & database initializers
│   ├── engine/              # ISO 6346 validator, reconciliation, invoice, CargoWise XML
│   ├── templates/           # Carrier-specific YAML parsing templates (MSC, Maersk, DahNAY)
│   ├── web/                 # High-density enterprise operations interface
│   └── run.py               # Direct CLI pipeline runner
├── studio_engine/           # Multi-agent dispatch server & web control center
├── tests/                   # End-to-end unit and integration test suites
├── build/portfolio/         # Enterprise portfolio presentation
├── Dockerfile               # Containerized production runtime
├── docker-compose.yml       # Production deployment orchestration
└── requirements.txt         # Project dependencies
```

---

## 📜 License
MIT License. Built for DahNAY Logistics operational evaluation and EXIM digital transformation.
