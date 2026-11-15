"""
Comprehensive Test Suite for DahNAY FreightFlow Engine
Verifies multi-format parsing (.xlsx, .txt, .json), ISO 6346 validation,
reconciliation, and CargoWise XML output.
"""

import sys
import os
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from dahnay_logistics.engine.models import MasterBookingRecord
from dahnay_logistics.engine.checksum import ContainerValidator, PortLocationValidator
from dahnay_logistics.engine.normalizer import MultiFormatSINormalizer
from dahnay_logistics.engine.reconciliation import DahNAYReconciliationEngine
from dahnay_logistics.engine.invoice_generator import CommercialInvoiceGenerator
from dahnay_logistics.engine.cargowise_exporter import CargoWiseUniversalExporter

with open("dahnay_logistics/datasets/sample_cargowise_booking.json", "r", encoding="utf-8") as f:
    BOOKING_DATA = json.load(f)

MASTER_BOOKING = MasterBookingRecord(
    job_id=BOOKING_DATA["job_id"],
    booking_reference=BOOKING_DATA["booking_reference"],
    customer_account=BOOKING_DATA["client_name"],
    carrier_line=BOOKING_DATA["carrier_line"],
    pol=BOOKING_DATA["pol"],
    pod=BOOKING_DATA["pod"],
    vessel_scheduled=BOOKING_DATA["vessel_scheduled"],
    voyage_scheduled=BOOKING_DATA["voyage_scheduled"],
    approved_weight_limit_kg=BOOKING_DATA["approved_weight_limit_kg"],
    approved_containers_count=BOOKING_DATA["approved_containers_count"],
    container_type=BOOKING_DATA["container_size_type"],
    ocean_freight_usd=BOOKING_DATA["commercial_rates"]["ocean_freight_rate_usd_per_teu"],
    terminal_handling_charges_inr=BOOKING_DATA["commercial_rates"]["terminal_handling_charges_inr_per_cntr"],
    documentation_fee_inr=BOOKING_DATA["commercial_rates"]["documentation_fee_inr"],
    baf_fuel_surcharge_usd=BOOKING_DATA["commercial_rates"]["baf_fuel_surcharge_usd_per_cntr"],
    gst_rate=BOOKING_DATA["commercial_rates"]["gst_percentage"]
)


def test_iso6346_checksum():
    # Valid container: MSCU9081247 -> check digit 7
    is_valid, digit = ContainerValidator.validate_container_number("MSCU9081247")
    assert is_valid is True
    assert digit == 7

    # Invalid container (wrong check digit: 5 instead of 7)
    is_invalid, digit2 = ContainerValidator.validate_container_number("MSCU9081245")
    assert is_invalid is False
    assert digit2 == 7
    print("✔ ISO 6346 container checksum validation passed!")


def test_excel_ingestion():
    excel_file = "dahnay_logistics/datasets/sample_dahnay_si.xlsx"
    si, confidence = MultiFormatSINormalizer.parse_file(excel_file)
    assert si.booking_reference == "BKG-MAA-992104"
    assert len(si.containers) == 2
    assert si.total_gross_weight_kg == 26800.0
    assert confidence >= 0.90
    print("✔ Excel (.xlsx) ingestion & tabular extraction passed!")


def test_reconciliation_audit():
    excel_file = "dahnay_logistics/datasets/sample_dahnay_si.xlsx"
    si, _ = MultiFormatSINormalizer.parse_file(excel_file)
    audit = DahNAYReconciliationEngine.audit(si, MASTER_BOOKING)

    assert audit.match_status == "CRITICAL_REJECT"
    overweight_flag = next((f for f in audit.flags if f.field_name == "total_gross_weight_kg"), None)
    assert overweight_flag is not None
    assert "Overweight Alert" in overweight_flag.issue_description
    print("✔ Reconciliation audit passed! Detected overweight:", overweight_flag.issue_description)


def test_invoice_and_cargowise_xml():
    excel_file = "dahnay_logistics/datasets/sample_dahnay_si.xlsx"
    si, _ = MultiFormatSINormalizer.parse_file(excel_file)
    audit = DahNAYReconciliationEngine.audit(si, MASTER_BOOKING)
    invoice = CommercialInvoiceGenerator.generate(si, MASTER_BOOKING, audit)

    assert invoice.grand_total_inr > 0
    assert len(invoice.line_items) == 4

    xml_output = CargoWiseUniversalExporter.generate_universal_xml(si, invoice, MASTER_BOOKING)
    assert "<UniversalShipment" in xml_output
    assert "<Company>DAHNAY_LOGISTICS_CHENNAI</Company>" in xml_output
    assert "<OrderNumber>BKG-MAA-992104</OrderNumber>" in xml_output
    print("✔ CargoWise One Universal XML export generated successfully!")


def test_carrier_templates():
    from dahnay_logistics.engine.template_engine import CarrierTemplateEngine
    templates = CarrierTemplateEngine.load_templates()
    assert len(templates) >= 3
    issuers = [t["issuer"] for t in templates]
    assert "DahNAY Logistics Chennai" in issuers
    assert "Maersk Line A/S" in issuers

    raw_text = open("dahnay_logistics/datasets/sample_dahnay_si.txt", "r", encoding="utf-8").read()
    si, meta = CarrierTemplateEngine.extract_with_template(raw_text)
    assert si.booking_reference == "BKG-MAA-992104"
    assert "Tirupur" in si.shipper_name
    print(f"✔ Carrier YAML template pipeline passed! Matched: {meta['template_issuer']}")


def test_dcsa_ebl_export():
    from dahnay_logistics.engine.dcsa_pipeline import DCSAElectronicBillOfLadingExporter
    excel_file = "dahnay_logistics/datasets/sample_dahnay_si.xlsx"
    si, _ = MultiFormatSINormalizer.parse_file(excel_file)
    audit = DahNAYReconciliationEngine.audit(si, MASTER_BOOKING)
    invoice = CommercialInvoiceGenerator.generate(si, MASTER_BOOKING, audit)

    dcsa = DCSAElectronicBillOfLadingExporter.export_to_dcsa_json(si, MASTER_BOOKING, invoice)
    assert "transportDocumentReference" in dcsa
    assert dcsa["transportDocumentStatus"] == "ISSUED"
    assert "shipper" in dcsa["documentParties"]
    assert len(dcsa["utilizedTransportEquipments"]) == 2
    print("✔ DCSA eBL v3.0 standard JSON export passed!")


if __name__ == "__main__":
    test_iso6346_checksum()
    test_excel_ingestion()
    test_reconciliation_audit()
    test_invoice_and_cargowise_xml()
    test_carrier_templates()
    test_dcsa_ebl_export()
    print("\n🎉 ALL DAHNAY FREIGHTFLOW ENGINE & PIPELINE TESTS PASSED 100%!")
