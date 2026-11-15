"""
End-to-End Real-Time Backend & API Integration Test Suite for DahNAY FreightFlow
Verifies SQLite persistence, file ingestion, reconciliation, discrepancy resolution,
CargoWise One EDI dispatch, DCSA eBL 3.0 generation, and clean enterprise UI delivery.
"""

import os
import sys
import json

# Ensure root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from fastapi.testclient import TestClient
from app import app
from dahnay_logistics.db.database import init_db, seed_default_bookings, get_db_connection
from dahnay_logistics.backend.service import FreightFlowService


def test_sqlite_persistence_and_seed():
    """Verify Master Bookings are properly seeded in SQLite database."""
    init_db()
    seed_default_bookings()

    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT booking_reference, carrier_line, approved_weight_limit_kg FROM master_bookings")
    rows = c.fetchall()
    conn.close()

    assert len(rows) >= 2, f"Expected at least 2 bookings, got {len(rows)}"
    refs = [r["booking_reference"] for r in rows]
    assert "BKG-MAA-992104" in refs, "BKG-MAA-992104 not found in DB"
    assert "BKG-TUT-448190" in refs, "BKG-TUT-448190 not found in DB"
    print("✔ SQLite DB persistence and seed verification passed!")


def test_excel_ingestion_and_audit():
    """Test real Excel parsing, container checksumming, and discrepancy generation."""
    sample_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dahnay_logistics", "datasets", "sample_dahnay_si.xlsx"))
    assert os.path.exists(sample_file), f"File {sample_file} must exist"

    detail = FreightFlowService.ingest_document(sample_file, "sample_dahnay_si.xlsx")
    assert detail is not None
    assert detail["document"]["booking_reference"] == "BKG-MAA-992104"
    assert detail["document"]["total_gross_weight_kg"] == 26800.0

    # Containers should be saved
    containers = detail["containers"]
    assert len(containers) == 2
    cntr_map = {c["container_number"]: c for c in containers}
    assert "MSCU9081245" in cntr_map
    assert cntr_map["MSCU9081245"]["is_checksum_valid"] == 0
    assert cntr_map["MSCU9081245"]["expected_check_digit"] == 7

    # Discrepancies should be detected (Weight over slot, invalid container check-digit)
    discrepancies = detail["discrepancies"]
    assert len(discrepancies) >= 2
    fields = [d["field_name"].upper() for d in discrepancies]
    assert any("GROSS_WEIGHT" in f or "WEIGHT" in f for f in fields)
    assert any("CONTAINER" in f for f in fields)

    # Commercial Invoice pre-filled
    invoice = detail["invoice"]
    assert invoice is not None
    assert invoice["grand_total_inr"] > 0
    assert invoice["gst_amount_inr"] > 0
    print(f"✔ Real file ingestion, container checksumming, and pre-filled invoice (INR {invoice['grand_total_inr']:,.2f}) passed!")


def test_discrepancy_resolution_and_state_transition():
    """Test 1-click auto-fix for ISO 6346 typo and manager waiver."""
    detail = FreightFlowService.get_shipment_detail("BKG-MAA-992104")
    discrepancies = detail["discrepancies"]

    for d in discrepancies:
        fn = d["field_name"].upper()
        if "CONTAINER" in fn:
            res = FreightFlowService.resolve_discrepancy(d["id"], "AUTO_FIX", "Auto-corrected via Modulo 11 check digit")
            assert res["success"] is True
        elif "WEIGHT" in fn:
            res = FreightFlowService.resolve_discrepancy(d["id"], "MANAGER_WAIVER", "Certified weighbridge waiver approved by Ops Manager")
            assert res["success"] is True

    # Refresh detail
    updated = FreightFlowService.get_shipment_detail("BKG-MAA-992104")
    assert updated["document"]["lifecycle_state"] in ("APPROVED", "APPROVED_FOR_EDI")
    
    # Check that container number was corrected in DB
    cntr_numbers = [c["container_number"] for c in updated["containers"]]
    assert "MSCU9081247" in cntr_numbers
    print("✔ 1-click Auto-Fix and Manager Waiver resolution passed (State transitioned to APPROVED)!")


def test_cargowise_dispatch():
    """Test generating UniversalShipment XML and simulated eAdaptor transmission."""
    res = FreightFlowService.dispatch_cargowise("BKG-MAA-992104")
    assert res["success"] is True
    assert res["status"] == "CARGOWISE_SYNCED"
    assert "transaction_id" in res
    assert res["transaction_id"].startswith("CW-SHIP-")

    # Verify lifecycle state is locked as CARGOWISE_SYNCED
    detail = FreightFlowService.get_shipment_detail("BKG-MAA-992104")
    assert detail["document"]["lifecycle_state"] == "CARGOWISE_SYNCED"
    print(f"✔ CargoWise One eAdaptor EDI transmission passed (Trx: {res['transaction_id']})!")
    print(f"✔ CargoWise One eAdaptor EDI transmission passed (Trx: {res['transaction_id']})!")


def test_fastapi_rest_endpoints():
    """Verify live HTTP endpoints with FastAPI TestClient."""
    client = TestClient(app)

    # 1. Shipments list
    resp = client.get("/api/v1/shipments")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "success"
    assert len(data["data"]) >= 2

    # 2. Shipment detail
    resp = client.get("/api/v1/shipments/BKG-MAA-992104")
    assert resp.status_code == 200
    assert resp.json()["data"]["booking"]["booking_reference"] == "BKG-MAA-992104"

    # 3. CargoWise XML export
    resp = client.get("/api/v1/shipments/BKG-MAA-992104/cargowise-xml")
    assert resp.status_code == 200
    assert "UniversalShipment" in resp.text
    assert resp.headers["content-type"].startswith("application/xml")

    # 4. DCSA eBL JSON export
    resp = client.get("/api/v1/shipments/BKG-MAA-992104/dcsa-json")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("application/json")
    dcsa_data = resp.json()
    assert "transportDocument" in dcsa_data or "transportDocumentReference" in dcsa_data

    # 5. UI Portal contains zero design token junk
    resp = client.get("/dahnay")
    assert resp.status_code == 200
    assert "DahNAY FreightFlow" in resp.text
    assert "Enterprise Design Tokens" not in resp.text
    assert "Component Storybook" not in resp.text
    assert "Figma & Horizon UI" not in resp.text
    assert "Active EXIM Shipments Queue" in resp.text
    print("✔ All FastAPI REST endpoints and clean operations UI verified!")


if __name__ == "__main__":
    print("\n=======================================================")
    print("RUNNING DAHNAY FREIGHTFLOW REAL BACKEND INTEGRATION TESTS")
    print("=======================================================\n")
    test_sqlite_persistence_and_seed()
    test_excel_ingestion_and_audit()
    test_discrepancy_resolution_and_state_transition()
    test_cargowise_dispatch()
    test_fastapi_rest_endpoints()
    print("\n🎉 ALL REAL BACKEND & REST API INTEGRATION TESTS PASSED 100%!\n")
