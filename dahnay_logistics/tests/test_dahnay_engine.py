"""
Comprehensive Test Suite for DahNAY FreightFlow Engine
Verifies multi-format parsing (.xlsx, .txt, .json), ISO 6346 validation,
reconciliation, and CargoWise XML output.
"""

import sys
import os
import json

test_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(test_dir, ".."))
grandparent_dir = os.path.abspath(os.path.join(test_dir, "..", ".."))

sys.path.insert(0, grandparent_dir)
sys.path.insert(0, parent_dir)

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
from dahnay_logistics.engine.template_engine import CarrierTemplateEngine
from dahnay_logistics.engine.dcsa_pipeline import DCSAElectronicBillOfLadingExporter

booking_path = os.path.join(parent_dir, "datasets", "sample_cargowise_booking.json")
if not os.path.exists(booking_path):
    booking_path = os.path.join(grandparent_dir, "dahnay_logistics", "datasets", "sample_cargowise_booking.json")

with open(booking_path, "r", encoding="utf-8") as f:
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

    # Invalid container (typo in check digit: 5 instead of 7)
    is_invalid, expected_digit = ContainerValidator.validate_container_number("MSCU9081245")
    assert is_invalid is False
    assert expected_digit == 7

    # UN/LOCODE check
    code, name = PortLocationValidator.resolve_port("Chennai Port")
    assert code == "INMAA"
    assert "Chennai" in name
    print("✔ ISO 6346 container checksum validation passed!")


def test_excel_ingestion():
    xlsx_path = os.path.join(parent_dir, "datasets", "sample_dahnay_si.xlsx")
    if not os.path.exists(xlsx_path):
        xlsx_path = os.path.join(grandparent_dir, "dahnay_logistics", "datasets", "sample_dahnay_si.xlsx")
    si, confidence = MultiFormatSINormalizer.parse_file(xlsx_path)

    assert si.booking_reference == "BKG-MAA-992104"
    assert "Tirupur Garments" in si.shipper_name
    assert len(si.containers) == 2
    assert si.total_gross_weight_kg == 26800.0
    assert confidence >= 0.95
    print("✔ Excel (.xlsx) ingestion & tabular extraction passed!")


def test_reconciliation():
    xlsx_path = os.path.join(parent_dir, "datasets", "sample_dahnay_si.xlsx")
    if not os.path.exists(xlsx_path):
        xlsx_path = os.path.join(grandparent_dir, "dahnay_logistics", "datasets", "sample_dahnay_si.xlsx")
    si, _ = MultiFormatSINormalizer.parse_file(xlsx_path)
    audit = DahNAYReconciliationEngine.audit(si, MASTER_BOOKING)

    assert audit.match_status == "CRITICAL_REJECT"
    assert len(audit.flags) >= 2
    print(f"✔ Reconciliation audit passed! Detected overweight: {audit.flags[2].issue_description}")


def test_cargowise_export():
    xlsx_path = os.path.join(parent_dir, "datasets", "sample_dahnay_si.xlsx")
    if not os.path.exists(xlsx_path):
        xlsx_path = os.path.join(grandparent_dir, "dahnay_logistics", "datasets", "sample_dahnay_si.xlsx")
    si, _ = MultiFormatSINormalizer.parse_file(xlsx_path)
    audit = DahNAYReconciliationEngine.audit(si, MASTER_BOOKING)
    invoice = CommercialInvoiceGenerator.generate(si, MASTER_BOOKING, audit)
    xml_out = CargoWiseUniversalExporter.generate_universal_xml(si, invoice, MASTER_BOOKING)

    assert "<UniversalShipment" in xml_out
    assert "BKG-MAA-992104" in xml_out
    assert "MSCU9081245" in xml_out
    print("✔ CargoWise One Universal XML export generated successfully!")


def test_carrier_templates():
    from dahnay_logistics.engine.template_engine import CarrierTemplateEngine
    templates = CarrierTemplateEngine.load_templates()
    assert len(templates) >= 3
    issuers = [t["issuer"] for t in templates]
    assert "DahNAY Logistics Chennai" in issuers
    assert "Maersk Line A/S" in issuers

    raw_text_path = os.path.join(parent_dir, "datasets", "sample_dahnay_si.txt")
    if not os.path.exists(raw_text_path):
        raw_text_path = os.path.join(grandparent_dir, "dahnay_logistics", "datasets", "sample_dahnay_si.txt")
    raw_text = open(raw_text_path, "r", encoding="utf-8").read()
    si, meta = CarrierTemplateEngine.extract_with_template(raw_text)
    assert si.booking_reference == "BKG-MAA-992104"
    assert "Tirupur" in si.shipper_name
    print(f"✔ Carrier YAML template pipeline passed! Matched: {meta['template_issuer']}")


def test_dcsa_ebl_export():
    from dahnay_logistics.engine.dcsa_pipeline import DCSAElectronicBillOfLadingExporter
    xlsx_path = os.path.join(parent_dir, "datasets", "sample_dahnay_si.xlsx")
    if not os.path.exists(xlsx_path):
        xlsx_path = os.path.join(grandparent_dir, "dahnay_logistics", "datasets", "sample_dahnay_si.xlsx")
    si, _ = MultiFormatSINormalizer.parse_file(xlsx_path)
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
    test_reconciliation()
    test_cargowise_export()
    test_carrier_templates()
    test_dcsa_ebl_export()
    print("\n🎉 ALL DAHNAY FREIGHTFLOW ENGINE & PIPELINE TESTS PASSED 100%!")
