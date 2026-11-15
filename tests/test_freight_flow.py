"""
Tests for FreightFlow AI: Document Ingestion, Discrepancy Audit, and Invoice Pre-fill
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from freight_flow.models import MasterJobRecord, DiscrepancySeverity
from freight_flow.extractor import ShippingInstructionExtractor
from freight_flow.validator import FreightReconciliationEngine
from freight_flow.invoice_builder import FreightInvoiceBuilder


SAMPLE_MESSY_SI_TEXT = """
SHIPPING INSTRUCTIONS (DRAFT)
Booking Ref: BKG-MAA-992104
Shipper: Tirupur Garments Export Ltd, Plot 14, SIDCO Industrial Estate, Tirupur, Tamil Nadu
Consignee: Gulf Retail Fashion LLC, Dubai Mall, Downtown Dubai, UAE
Port of Loading: Chennai Port (INMAA)
Port of Discharge: Jebel Ali Port (AEJEA)
Vessel: MSC EMANUELA Voyage: 2408W
Gross Weight: 26800 KGS
Volume: 64.2 CBM
Packages: 920 Cartons
Cargo Description: 100% Cotton Knitted Finished T-Shirts
HS Code: 6109.10
Containers:
MSCU9081245 / SL982103
MEDU4091823 / SL982104
"""

SAMPLE_JOB_RECORD = MasterJobRecord(
    job_id="JOB-2026-CHN-048",
    booking_reference="BKG-MAA-992104",
    customer_account="Tirupur Garments Export Ltd",
    expected_shipper="Tirupur Garments Export Ltd",
    expected_consignee="Gulf Retail Fashion LLC",
    pol="Chennai Port (INMAA)",
    pod="Jebel Ali Port (AEJEA)",
    approved_weight_limit_kg=24000.0,  # Note: SI is 26,800 kg -> OVERWEIGHT DISCREPANCY!
    agreed_ocean_freight_usd=1650.0,
    terminal_handling_charges_inr=11500.0,
    documentation_fee_inr=4500.0,
    expected_containers_count=2
)


def test_shipping_instruction_extraction():
    si, confidence = ShippingInstructionExtractor.extract_from_text(SAMPLE_MESSY_SI_TEXT)
    assert si.booking_reference == "BKG-MAA-992104"
    assert "Tirupur Garments" in si.shipper_name
    assert "Gulf Retail Fashion" in si.consignee_name
    assert si.total_gross_weight_kg == 26800.0
    assert len(si.containers) == 2
    assert confidence >= 0.85
    print("✔ Extraction verified with confidence:", confidence)


def test_discrepancy_audit_engine():
    si, _ = ShippingInstructionExtractor.extract_from_text(SAMPLE_MESSY_SI_TEXT)
    audit = FreightReconciliationEngine.audit_shipping_instruction(si, SAMPLE_JOB_RECORD)
    
    assert audit.match_status == "CRITICAL_REJECT"  # Due to overweight (26,800kg > 24,000kg)
    assert len(audit.flags) >= 1
    
    overweight_flag = next((f for f in audit.flags if f.field_name == "total_gross_weight_kg"), None)
    assert overweight_flag is not None
    assert overweight_flag.severity == DiscrepancySeverity.CRITICAL
    assert "Overweight alert" in overweight_flag.issue_description
    print("✔ Overweight discrepancy flagged accurately:", overweight_flag.issue_description)


def test_invoice_prefill_generation():
    si, _ = ShippingInstructionExtractor.extract_from_text(SAMPLE_MESSY_SI_TEXT)
    audit = FreightReconciliationEngine.audit_shipping_instruction(si, SAMPLE_JOB_RECORD)
    invoice = FreightInvoiceBuilder.generate_invoice(si, SAMPLE_JOB_RECORD, audit)
    
    assert invoice.job_reference == "JOB-2026-CHN-048"
    assert len(invoice.line_items) == 4
    assert invoice.total_amount_usd > 0
    assert invoice.total_amount_inr > 0
    assert invoice.reconciliation_verified is False  # Because discrepancy was flagged
    assert invoice.status == "PENDING_EXCEPTION_CLEARANCE"
    print("✔ Pre-filled invoice generated successfully:", invoice.invoice_number, "Total INR:", invoice.total_amount_inr)


if __name__ == "__main__":
    test_shipping_instruction_extraction()
    test_discrepancy_audit_engine()
    test_invoice_prefill_generation()
    print("\n🎉 ALL FREIGHTFLOW AI TESTS PASSED 100%!")
