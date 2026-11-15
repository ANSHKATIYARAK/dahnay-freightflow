"""
DahNAY Logistics: Automated Freight Document-to-Invoice CLI Runner
Executes end-to-end extraction, reconciliation, and invoice pre-fill in < 1 second.
"""

import sys
import os
import json

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dahnay_logistics.engine.models import MasterBookingRecord
from dahnay_logistics.engine.normalizer import MultiFormatSINormalizer
from dahnay_logistics.engine.reconciliation import DahNAYReconciliationEngine
from dahnay_logistics.engine.invoice_generator import CommercialInvoiceGenerator
from dahnay_logistics.engine.cargowise_exporter import CargoWiseUniversalExporter
from dahnay_logistics.backend.service import FreightFlowService


def get_default_booking() -> MasterBookingRecord:
    booking_file = os.path.join(os.path.dirname(__file__), "datasets", "sample_cargowise_booking.json")
    with open(booking_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    return MasterBookingRecord(
        job_id=data["job_id"],
        booking_reference=data["booking_reference"],
        customer_account=data["client_name"],
        carrier_line=data["carrier_line"],
        pol=data["pol"],
        pod=data["pod"],
        vessel_scheduled=data["vessel_scheduled"],
        voyage_scheduled=data["voyage_scheduled"],
        approved_weight_limit_kg=data["approved_weight_limit_kg"],
        approved_containers_count=data["approved_containers_count"],
        container_type=data["container_size_type"],
        ocean_freight_usd=data["commercial_rates"]["ocean_freight_rate_usd_per_teu"],
        terminal_handling_charges_inr=data["commercial_rates"]["terminal_handling_charges_inr_per_cntr"],
        documentation_fee_inr=data["commercial_rates"]["documentation_fee_inr"],
        baf_fuel_surcharge_usd=data["commercial_rates"]["baf_fuel_surcharge_usd_per_cntr"],
        gst_rate=data["commercial_rates"]["gst_percentage"]
    )


def run_pipeline(input_file: str = "dahnay_logistics/datasets/sample_dahnay_si.xlsx"):
    print("\n" + "="*75)
    print(f" 🚢 DAHNAY LOGISTICS: PROCESSING INBOUND SHIPPING INSTRUCTION")
    print(f" 📄 File: {input_file}")
    print("="*75)

    # 1. Multi-format Ingestion & Normalization
    si, confidence = MultiFormatSINormalizer.parse_file(input_file)
    print(f"\n[1] DOCUMENT EXTRACTION (Confidence: {confidence*100:.1f}%)")
    print(f"    • Booking Reference : {si.booking_reference}")
    print(f"    • Shipper (Exporter): {si.shipper_name}")
    print(f"    • Consignee         : {si.consignee_name}")
    print(f"    • Vessel & Voyage   : {si.vessel_name} / {si.voyage_number}")
    print(f"    • Routing (POL->POD): {si.port_of_loading}  -->  {si.port_of_discharge}")
    print(f"    • Cargo Particulars : {si.total_packages} {si.package_type} | {si.cargo_description}")
    print(f"    • Total Gross Weight: {si.total_gross_weight_kg:,.1f} KGS")
    print(f"    • Containers Count  : {len(si.containers)} Units")

    # 2. Reconciliation against CargoWise Master Booking
    booking = get_default_booking()
    audit = DahNAYReconciliationEngine.audit(si, booking)
    print(f"\n[2] DISCREPANCY AUDIT AGAINST CARGOWISE BOOKING")
    print(f"    • Status: {audit.match_status}")
    print(f"    • Carrier Approved Weight Limit: {booking.approved_weight_limit_kg:,.1f} KGS")
    print(f"    • Weight Discrepancy           : +{si.total_gross_weight_kg - booking.approved_weight_limit_kg:,.1f} KGS")
    
    if audit.flags:
        print(f"\n    ⚠️  MISMATCHES FLAGGED FOR HUMAN REVIEW ({len(audit.flags)}):")
        for idx, f in enumerate(audit.flags, 1):
            print(f"       {idx}. [{f.severity}] {f.field_name.upper()}")
            print(f"          Issue : {f.issue_description}")
            print(f"          Remedy: {f.remedy_suggestion}")
    else:
        print("    ✔ Zero discrepancies found. Clean pass.")

    # 3. Commercial Freight Invoice Pre-Fill
    invoice = CommercialInvoiceGenerator.generate(si, booking, audit)
    print(f"\n[3] PRE-FILLED COMMERCIAL FREIGHT INVOICE ({invoice.invoice_number})")
    print(f"    • Billed To      : {invoice.bill_to_party}")
    print(f"    • Base Freight   : ₹{invoice.total_inr:,.2f}")
    print(f"    • CGST (9%)      : ₹{invoice.gst_amount_inr / 2.0:,.2f}")
    print(f"    • SGST (9%)      : ₹{invoice.gst_amount_inr / 2.0:,.2f}")
    print(f"    • Grand Total INR: ₹{invoice.grand_total_inr:,.2f}")

    # 4. CargoWise One UniversalShipment XML Export
    xml_data = CargoWiseUniversalExporter.generate_universal_xml(si, invoice, booking)
    xml_path = "dahnay_logistics/datasets/output_cargowise_shipment.xml"
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write(xml_data)
    print(f"\n[4] CARGOWISE ONE ERP INTEGRATION")
    print(f"    • Exported: {xml_path}")
    print(f"    • Status  : READY FOR SFTP/EDI TRANSMIT TO DAHNAY_MAA (PROD_IN)")
    print("="*75 + "\n")


if __name__ == "__main__":
    file_arg = sys.argv[1] if len(sys.argv) > 1 else "dahnay_logistics/datasets/sample_dahnay_si.xlsx"
    run_pipeline(file_arg)
