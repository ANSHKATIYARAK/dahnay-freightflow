"""
DahNAY FreightFlow: Enterprise SQLite Relational Database Layer
Handles persistence for Master Bookings, Inbound Documents, Container Units,
Discrepancy Records, Commercial Invoices, and Immutable Audit Trails.
"""

import sqlite3
import os
import sys
import json
from datetime import datetime
from typing import Dict, Any, List, Optional

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))
DB_PATH = os.path.join(DB_DIR, "freightflow.db")


def get_db_connection() -> sqlite3.Connection:
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """Initializes tables, indices, and default seed data."""
    conn = get_db_connection()
    cur = conn.cursor()

    # 1. Master Bookings (Source of Truth from Carrier)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS master_bookings (
        booking_reference TEXT PRIMARY KEY,
        job_id TEXT NOT NULL,
        customer_account TEXT NOT NULL,
        carrier_line TEXT NOT NULL,
        pol_code TEXT NOT NULL,
        pod_code TEXT NOT NULL,
        vessel_scheduled TEXT NOT NULL,
        voyage_scheduled TEXT NOT NULL,
        approved_weight_limit_kg REAL NOT NULL,
        approved_containers_count INTEGER NOT NULL,
        container_type TEXT NOT NULL,
        ocean_freight_usd REAL NOT NULL,
        thc_rate_inr REAL NOT NULL,
        documentation_fee_inr REAL NOT NULL,
        baf_fuel_usd REAL NOT NULL,
        gst_rate REAL NOT NULL,
        status TEXT DEFAULT 'ACTIVE',
        created_at TEXT NOT NULL
    );
    """)

    # 2. Inbound Shipping Documents
    cur.execute("""
    CREATE TABLE IF NOT EXISTS shipping_documents (
        id TEXT PRIMARY KEY,
        booking_reference TEXT NOT NULL,
        original_filename TEXT NOT NULL,
        file_format TEXT NOT NULL,
        shipper_name TEXT NOT NULL,
        shipper_address TEXT,
        shipper_iec TEXT,
        shipper_gstin TEXT,
        consignee_name TEXT NOT NULL,
        consignee_address TEXT,
        consignee_tax_id TEXT,
        vessel_name TEXT NOT NULL,
        voyage_number TEXT NOT NULL,
        port_of_loading TEXT NOT NULL,
        port_of_discharge TEXT NOT NULL,
        cargo_description TEXT,
        hs_code TEXT,
        total_packages INTEGER,
        package_type TEXT,
        total_gross_weight_kg REAL NOT NULL,
        total_cbm REAL,
        lifecycle_state TEXT NOT NULL, -- 'INGESTED', 'EXCEPTION_HOLD', 'APPROVED', 'CARGOWISE_SYNCED'
        parsing_confidence REAL NOT NULL,
        raw_text_content TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY (booking_reference) REFERENCES master_bookings (booking_reference)
    );
    """)

    # 3. Document Containers
    cur.execute("""
    CREATE TABLE IF NOT EXISTS document_containers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        document_id TEXT NOT NULL,
        container_number TEXT NOT NULL,
        seal_number TEXT NOT NULL,
        container_type TEXT NOT NULL,
        gross_weight_kg REAL NOT NULL,
        cbm REAL NOT NULL,
        packages_count INTEGER NOT NULL,
        is_checksum_valid INTEGER NOT NULL,
        expected_check_digit INTEGER,
        FOREIGN KEY (document_id) REFERENCES shipping_documents (id) ON DELETE CASCADE
    );
    """)

    # 4. Discrepancy Records
    cur.execute("""
    CREATE TABLE IF NOT EXISTS discrepancy_records (
        id TEXT PRIMARY KEY,
        document_id TEXT NOT NULL,
        field_name TEXT NOT NULL,
        severity TEXT NOT NULL, -- 'CRITICAL', 'WARNING', 'INFO'
        si_value TEXT,
        master_value TEXT,
        issue_description TEXT NOT NULL,
        remedy_suggestion TEXT NOT NULL,
        is_resolved INTEGER DEFAULT 0,
        resolution_type TEXT, -- 'AUTO_FIX', 'MANAGER_WAIVER', 'MANUAL_EDIT'
        resolution_notes TEXT,
        resolved_at TEXT,
        FOREIGN KEY (document_id) REFERENCES shipping_documents (id) ON DELETE CASCADE
    );
    """)

    # 5. Commercial Invoices
    cur.execute("""
    CREATE TABLE IF NOT EXISTS commercial_invoices (
        invoice_number TEXT PRIMARY KEY,
        document_id TEXT NOT NULL,
        booking_reference TEXT NOT NULL,
        bill_to_party TEXT NOT NULL,
        gstin TEXT,
        total_usd REAL NOT NULL,
        total_inr_base REAL NOT NULL,
        gst_amount_inr REAL NOT NULL,
        grand_total_inr REAL NOT NULL,
        usd_to_inr_rate REAL NOT NULL,
        status TEXT NOT NULL, -- 'DRAFT', 'APPROVED', 'EXPORTED'
        cargowise_trx_id TEXT,
        line_items_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (document_id) REFERENCES shipping_documents (id)
    );
    """)

    # 6. Audit Trail Events (Immutable Compliance Log)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS audit_trail_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entity_id TEXT NOT NULL,
        actor TEXT NOT NULL,
        action TEXT NOT NULL,
        details TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    """)

    conn.commit()
    conn.close()


def seed_default_bookings():
    """Seeds master booking records for DahNAY Logistics."""
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("SELECT COUNT(*) FROM master_bookings WHERE booking_reference = 'BKG-MAA-992104';")
    if cur.fetchone()[0] == 0:
        cur.execute("""
        INSERT INTO master_bookings (
            booking_reference, job_id, customer_account, carrier_line,
            pol_code, pod_code, vessel_scheduled, voyage_scheduled,
            approved_weight_limit_kg, approved_containers_count, container_type,
            ocean_freight_usd, thc_rate_inr, documentation_fee_inr, baf_fuel_usd,
            gst_rate, status, created_at
        ) VALUES (
            'BKG-MAA-992104', 'JOB-2026-CHN-048', 'Tirupur Garments Export Ltd', 'Mediterranean Shipping Company (MSC)',
            'INMAA', 'AEJEA', 'MSC EMANUELA', '2408W',
            24000.0, 2, '40HC',
            1650.0, 11500.0, 4500.0, 120.0,
            18.0, 'ACTIVE', datetime('now')
        );
        """)

    # Seed an additional active job to demonstrate multi-shipment queue
    cur.execute("SELECT COUNT(*) FROM master_bookings WHERE booking_reference = 'BKG-TUT-448190';")
    if cur.fetchone()[0] == 0:
        cur.execute("""
        INSERT INTO master_bookings (
            booking_reference, job_id, customer_account, carrier_line,
            pol_code, pod_code, vessel_scheduled, voyage_scheduled,
            approved_weight_limit_kg, approved_containers_count, container_type,
            ocean_freight_usd, thc_rate_inr, documentation_fee_inr, baf_fuel_usd,
            gst_rate, status, created_at
        ) VALUES (
            'BKG-TUT-448190', 'JOB-2026-TUT-112', 'Tuticorin Salt & Marine Chemicals Ltd', 'Maersk Line',
            'INTUT', 'SGSIN', 'MAERSK MC-KINNEY MOLLER', '2411E',
            28000.0, 1, '20GP',
            950.0, 9500.0, 4500.0, 80.0,
            18.0, 'ACTIVE', datetime('now')
        );
        """)

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    seed_default_bookings()
    print("✔ DahNAY FreightFlow database initialized and seeded successfully.")
