# FreightFlow Pilot Audit Scorecard: DahNAY Logistics
**Audit Date:** 2026-11-22 08:46:11 UTC  
**Document Ingested:** `sample_dahnay_si.xlsx` (XLSX)  
**Confidence Score:** `100.0%`  
**Booking Reference:** `BKG-MAA-992104`  
**Shipper / Account:** `Tirupur Garments Export Ltd, SIDCO Industrial Estate, Tirupur, Tamil Nadu`  
**Trade Corridor:** `Chennai Port (INMAA)` → `Jebel Ali Port (AEJEA)` via `MSC EMANUELA / MSC`  

---

## 1. Executive Summary
- **Parse & Extraction Time:** `< 0.8 seconds` (Replaces 18–25 mins of manual entry)
- **Container Checksums Validated:** `2` containers verified against ISO 6346 Modulo-11 algorithm
- **Reconciliation Status:** `HELD FOR CORRECTION (CRITICAL_REJECT)`
- **Discrepancies Caught:** `3` potential amendment or shut-out risks prevented
- **CargoWise XML Generated:** `UniversalShipment v1.1 XML` ready for direct eAdaptor mapping

---

## 2. Container Integrity & ISO 6346 Checksum Audit
| Container No. | Seal No. | Type | Weight (KG) | ISO 6346 Status | Check Digit |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `MSCU9081245` | `SL982103` | `40HC` | `13,400.0` | ❌ CHECKSUM ERROR | `7` |
| `MEDU4091823` | `SL982104` | `40HC` | `13,400.0` | ❌ CHECKSUM ERROR | `4` |

---

## 3. Discrepancy Gatekeeper Analysis
| Field | Severity | Issue Caught | Recommended Action |
| :--- | :--- | :--- | :--- |
| `container_MSCU9081245` | **CRITICAL** | Invalid Container Checksum: 'MSCU9081245' failed ISO 6346 algorithm (Expected digit: 7). | Verify physical container door photo or EIR gate ticket to correct typo. |
| `container_MEDU4091823` | **CRITICAL** | Invalid Container Checksum: 'MEDU4091823' failed ISO 6346 algorithm (Expected digit: 4). | Verify physical container door photo or EIR gate ticket to correct typo. |
| `total_gross_weight_kg` | **CRITICAL** | Overweight Alert: SI weight exceeds carrier approved slot by 2,800.0 KGS (VGM Shut-Out Risk). | Request shipper re-weighing certificate or buy additional slot weight allocation from MSC. |

---

## 4. Automated Commercial Freight Invoice
- **Total Ocean Freight:** `$3,540.00 USD`
- **Subtotal (INR):** `₹333,710.00`
- **GST (18% - CGST 9% + SGST 9%):** `₹4,950.00`
- **Grand Total (INR):** `₹338,660.00`

---

## 5. Next Steps for CargoWise Integration
The shipment payload has been validated and compiled into standard UniversalShipment XML:
- **XML File Attached:** `sample_dahnay_si_cargowise.xml`
- **Mapping:** Inbound via CargoWise eAdaptor SFTP / HTTPS service
- **Result:** Job booked and billing ledger updated with zero manual typing
