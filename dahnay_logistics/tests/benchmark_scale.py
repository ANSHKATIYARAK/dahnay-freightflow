"""
DahNAY FreightFlow: High-Volume Enterprise Scalability & Stress Benchmark
Simulates real-world EXIM freight volume across DahNAY's South India & Global trade corridors.
Measures throughput, latency (P50/P95/P99), discrepancy accuracy, and CargoWise XML generation.
"""

import os
import sys
import time
import random
import uuid
import statistics
from typing import List, Dict, Any

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure project path is accessible
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
grandparent_dir = os.path.dirname(parent_dir)
sys.path.insert(0, grandparent_dir)

from dahnay_logistics.engine.models import (
    ShippingInstruction,
    ContainerDetail,
    MasterBookingRecord,
    FreightTerms,
    ReconciliationResult,
    CommercialInvoice,
    DiscrepancySeverity
)
from dahnay_logistics.engine.checksum import ContainerValidator, PortLocationValidator
from dahnay_logistics.engine.reconciliation import DahNAYReconciliationEngine
from dahnay_logistics.engine.invoice_generator import CommercialInvoiceGenerator
from dahnay_logistics.engine.cargowise_exporter import CargoWiseUniversalExporter


# Realistic Archetypes based on DahNAY's active Indian Export Corridors
CORRIDORS = [
    {
        "shipper": "Tirupur Garments & Knitwear Export Ltd",
        "address": "42 Avinashi Road, Tirupur, Tamil Nadu 641602",
        "consignee": "Al-Futtaim Retail Logistics LLC",
        "consignee_addr": "Jebel Ali Free Zone, Dubai, UAE",
        "pol": "INMAA",
        "pod": "AEJEA",
        "carrier": "Mediterranean Shipping Company (MSC)",
        "vessel": "MSC EMANUELA",
        "cargo": "100% Cotton Knitted T-Shirts & Men's Apparel",
        "hs_code": "6109.10",
        "cntr_type": "40HC",
        "avg_tare_kg": 3800.0,
        "base_rate_usd": 1850.0
    },
    {
        "shipper": "Tuticorin Marine Chemicals & Salt Ltd",
        "address": "Harbour Estate, V.O.C. Port, Tuticorin, Tamil Nadu 628004",
        "consignee": "Jurong Aromatics Logistics Pte Ltd",
        "consignee_addr": "10 Jurong Island Highway, Singapore 627855",
        "pol": "INTUT",
        "pod": "SGSIN",
        "carrier": "Maersk Line A/S",
        "vessel": "MAERSK MC-KINNEY MOLLER",
        "cargo": "Refined Industrial Grade Solar Evaporated Salt",
        "hs_code": "2501.00",
        "cntr_type": "20GP",
        "avg_tare_kg": 2200.0,
        "base_rate_usd": 1200.0
    },
    {
        "shipper": "Coimbatore Precision Castings & Pumps Ltd",
        "address": "Peelamedu Industrial Estate, Coimbatore, Tamil Nadu 641004",
        "consignee": "Kirloskar Brothers Europe B.V.",
        "consignee_addr": "Waalhaven Z.z. 19, 3089 JH Rotterdam, Netherlands",
        "pol": "INMAA",
        "pod": "NLRTM",
        "carrier": "Hapag-Lloyd AG",
        "vessel": "AL DAHNA EXPRESS",
        "cargo": "Submersible Cast Iron Pump Assemblies & Impellers",
        "hs_code": "8413.70",
        "cntr_type": "40HC",
        "avg_tare_kg": 3800.0,
        "base_rate_usd": 2450.0
    },
    {
        "shipper": "Morbi Vitrified Ceramics Exports LLP",
        "address": "National Highway 8A, Trajpar, Morbi, Gujarat 363642",
        "consignee": "Saudi Ceramics Distribution Co",
        "consignee_addr": "Second Industrial City, Riyadh, Saudi Arabia",
        "pol": "INNSA",
        "pod": "AEJEA",
        "carrier": "CMA CGM SA",
        "vessel": "CMA CGM ANTOINE DE SAINT EXUPERY",
        "cargo": "Glazed Vitrified Floor Tiles (600x1200mm)",
        "hs_code": "6907.21",
        "cntr_type": "20GP",
        "avg_tare_kg": 2200.0,
        "base_rate_usd": 1150.0
    },
    {
        "shipper": "Ambattur Precision Auto Components Ltd",
        "address": "Ambattur Industrial Estate, Chennai, Tamil Nadu 600058",
        "consignee": "American Axle & Manufacturing Inc",
        "consignee_addr": "One Dauch Drive, Detroit, MI 48211, USA",
        "pol": "INMAA",
        "pod": "USNYC",
        "carrier": "Ocean Network Express (ONE)",
        "vessel": "ONE APUS",
        "cargo": "Machined Automotive Drive Shafts & Flanges",
        "hs_code": "8708.29",
        "cntr_type": "40HC",
        "avg_tare_kg": 3800.0,
        "base_rate_usd": 3200.0
    }
]

BIC_PREFIXES = ["MSCU", "MAEU", "CMAU", "HLXU", "ONEU", "TGHU", "COSU", "EGLV"]


def generate_valid_container(prefix: str, cntr_type: str, tare_kg: float) -> ContainerDetail:
    """Generates an authentic ISO 6346 compliant container number with verified check digit."""
    serial = f"{random.randint(100000, 999999)}"
    candidate = f"{prefix}{serial}0"
    _, check_digit = ContainerValidator.validate_container_number(candidate)
    valid_number = f"{prefix}{serial}{check_digit}"

    payload_weight = random.uniform(14000.0, 24000.0) if cntr_type == "40HC" else random.uniform(16000.0, 26000.0)
    return ContainerDetail(
        container_number=valid_number,
        seal_number=f"SL-{random.randint(100000, 999999)}",
        container_type=cntr_type,
        gross_weight_kg=round(payload_weight, 1),
        cbm=round(random.uniform(25.0, 65.0), 1),
        packages_count=random.randint(200, 1500),
        is_valid_iso6346=True,
        iso_check_digit=check_digit
    )


def generate_benchmark_dataset(num_shipments: int = 1000) -> List[Dict[str, Any]]:
    """
    Synthesizes a realistic high-volume batch of shipments with realistic error profiles:
    - ~8% ISO 6346 Check Digit Transposition/Typo errors
    - ~10% SOLAS VGM Overweight Violations (>5% carrier booking limit)
    - ~5% Booking Slot Mismatches (SI containers > booking quota)
    - ~77% Clean Match straight-through processing
    """
    dataset = []
    random.seed(42)  # Deterministic repeatability

    for i in range(1, num_shipments + 1):
        corr = random.choice(CORRIDORS)
        booking_ref = f"BKG-{corr['pol'][2:]}-{100000 + i}"
        job_id = f"JOB-2026-{corr['pol'][2:]}-{i:04d}"
        voyage = f"24{random.randint(10, 50)}{random.choice(['E', 'W', 'N', 'S'])}"

        # 1 to 3 containers per shipment
        cntr_count = random.choices([1, 2, 3], weights=[0.45, 0.45, 0.10])[0]
        approved_slot_weight = round(cntr_count * (22000.0 if corr['cntr_type'] == "40HC" else 24000.0), 1)

        booking = MasterBookingRecord(
            job_id=job_id,
            booking_reference=booking_ref,
            customer_account=corr["shipper"].split("&")[0].strip(),
            carrier_line=corr["carrier"],
            pol=corr["pol"],
            pod=corr["pod"],
            vessel_scheduled=corr["vessel"],
            voyage_scheduled=voyage,
            approved_weight_limit_kg=approved_slot_weight,
            approved_containers_count=cntr_count,
            container_type=corr["cntr_type"],
            ocean_freight_usd=corr["base_rate_usd"],
            terminal_handling_charges_inr=round(cntr_count * 9500.0, 2),
            documentation_fee_inr=4500.0,
            baf_fuel_surcharge_usd=round(cntr_count * 120.0, 2),
            gst_rate=18.0
        )

        # Decide error injection
        inject_checksum_err = (random.random() < 0.08)
        inject_overweight = (random.random() < 0.10)
        inject_slot_mismatch = (random.random() < 0.05)

        containers = []
        si_cntr_count = cntr_count + (1 if inject_slot_mismatch else 0)

        for c_idx in range(si_cntr_count):
            prefix = random.choice(BIC_PREFIXES)
            cntr = generate_valid_container(prefix, corr["cntr_type"], corr["avg_tare_kg"])
            if inject_checksum_err and c_idx == 0:
                # Corrupt check digit (off by 1)
                corrupted_digit = (cntr.iso_check_digit + 1) % 10
                corrupted_no = cntr.container_number[:10] + str(corrupted_digit)
                is_valid, exp_digit = ContainerValidator.validate_container_number(corrupted_no)
                cntr.container_number = corrupted_no
                cntr.is_valid_iso6346 = is_valid
                cntr.iso_check_digit = exp_digit
            containers.append(cntr)

        total_gross = sum(c.gross_weight_kg for c in containers)
        if inject_overweight:
            # Overweight by 1,500 to 3,500 kg (violating carrier slot & SOLAS VGM threshold)
            extra_weight = random.uniform(1500.0, 3500.0)
            approved_slot_weight = round(total_gross, 1)
            total_gross = approved_slot_weight + extra_weight
            containers[0].gross_weight_kg += extra_weight
        else:
            # Clean match: booking approved slot accommodates the gross weight
            approved_slot_weight = round(total_gross + random.uniform(0.0, 20.0), 1)

        booking.approved_weight_limit_kg = approved_slot_weight

        total_cbm = sum(c.cbm for c in containers)
        total_pkgs = sum(c.packages_count for c in containers)

        si = ShippingInstruction(
            si_number=f"SI-{20260000 + i}",
            booking_reference=booking_ref,
            shipper_name=corr["shipper"],
            shipper_address=corr["address"],
            shipper_iec="0419082103",
            shipper_gstin="33AABCT9981Q1Z4",
            consignee_name=corr["consignee"],
            consignee_address=corr["consignee_addr"],
            notify_party="SAME AS CONSIGNEE",
            vessel_name=corr["vessel"],
            voyage_number=voyage,
            port_of_loading=corr["pol"],
            port_of_discharge=corr["pod"],
            freight_terms=FreightTerms.PREPAID,
            cargo_description=corr["cargo"],
            hs_code=corr["hs_code"],
            total_packages=total_pkgs,
            package_type="Cartons / Pallets",
            total_gross_weight_kg=round(total_gross, 1),
            total_cbm=round(total_cbm, 1),
            containers=containers,
            raw_document_source="Simulated Benchmark Engine v3.5"
        )

        dataset.append({
            "index": i,
            "booking": booking,
            "si": si,
            "expected_checksum_err": inject_checksum_err,
            "expected_overweight": inject_overweight,
            "expected_slot_mismatch": inject_slot_mismatch
        })

    return dataset


def run_scalability_benchmark(num_shipments: int = 1000):
    print("=" * 75)
    print(f"  DAHNAY FREIGHTFLOW ENTERPRISE SCALABILITY & STRESS BENCHMARK")
    print(f"  Target Scale: {num_shipments:,} Shipments (~2,400 TEUs)")
    print(f"  Corridors: Chennai (INMAA), Tuticorin (INTUT), Nhava Sheva (INNSA)")
    print("=" * 75)

    print(f"\n[1/3] Generating synthetic benchmark batch ({num_shipments:,} real-world shipments)...")
    gen_start = time.perf_counter()
    dataset = generate_benchmark_dataset(num_shipments)
    gen_time = time.perf_counter() - gen_start
    print(f"  ✔ Dataset synthesized in {gen_time:.2f}s.")

    # Injected ground truth counts
    total_injected_checksum = sum(1 for d in dataset if d["expected_checksum_err"])
    total_injected_overweight = sum(1 for d in dataset if d["expected_overweight"])
    total_injected_slot = sum(1 for d in dataset if d["expected_slot_mismatch"])
    total_clean = sum(1 for d in dataset if not (d["expected_checksum_err"] or d["expected_overweight"] or d["expected_slot_mismatch"]))

    print(f"  Ground Truth Injected Errors:")
    print(f"    • ISO 6346 Container Checksum Typos : {total_injected_checksum} ({total_injected_checksum/num_shipments*100:.1f}%)")
    print(f"    • SOLAS VGM Overweight Violations   : {total_injected_overweight} ({total_injected_overweight/num_shipments*100:.1f}%)")
    print(f"    • Booking Slot Over-Allocations     : {total_injected_slot} ({total_injected_slot/num_shipments*100:.1f}%)")
    print(f"    • Clean Straight-Through Shipments : {total_clean} ({total_clean/num_shipments*100:.1f}%)")

    print(f"\n[2/3] Executing end-to-end FreightFlow Pipeline across all {num_shipments:,} shipments...")
    print("  Pipeline steps per file: Container Checksum -> Audit -> Invoice Gen -> CargoWise Universal XML")

    latencies_ms = []
    detected_checksum_count = 0
    detected_overweight_count = 0
    detected_slot_count = 0
    clean_approved_count = 0
    total_xml_bytes = 0

    bench_start = time.perf_counter()

    for item in dataset:
        t0 = time.perf_counter()

        si = item["si"]
        booking = item["booking"]

        # 1. Audit Checksum & Booking Reconciliation
        audit: ReconciliationResult = DahNAYReconciliationEngine.audit(si, booking)

        # 2. Commercial Invoice Synthesis
        invoice: CommercialInvoice = CommercialInvoiceGenerator.generate(si, booking, audit)

        # 3. CargoWise UniversalShipment XML Export
        xml_str = CargoWiseUniversalExporter.generate_universal_xml(si, invoice, booking)
        total_xml_bytes += len(xml_str.encode("utf-8"))

        t_elapsed = (time.perf_counter() - t0) * 1000.0  # ms
        latencies_ms.append(t_elapsed)

        # Track discrepancy detection
        flag_fields = [f.field_name for f in audit.flags]
        if any("container_" in f for f in flag_fields):
            detected_checksum_count += 1
        is_crit_overweight = any(f.field_name == "total_gross_weight_kg" and f.severity == DiscrepancySeverity.CRITICAL for f in audit.flags)
        if is_crit_overweight:
            detected_overweight_count += 1
        if "containers_count" in flag_fields:
            detected_slot_count += 1
        if audit.match_status == "MATCHED":
            clean_approved_count += 1

    total_bench_time = time.perf_counter() - bench_start

    # Metrics
    latencies_ms.sort()
    p50 = statistics.median(latencies_ms)
    mean_lat = statistics.mean(latencies_ms)
    p95 = latencies_ms[int(len(latencies_ms) * 0.95)]
    p99 = latencies_ms[int(len(latencies_ms) * 0.99)]
    min_lat = min(latencies_ms)
    max_lat = max(latencies_ms)

    throughput_sec = num_shipments / total_bench_time
    total_teus = sum(len(d["si"].containers) for d in dataset)
    teus_sec = total_teus / total_bench_time

    print(f"\n[3/3] BENCHMARK RESULTS & METRICS SUMMARY")
    print("-" * 75)
    print(f"  Total Shipments Processed     : {num_shipments:,}")
    print(f"  Total TEUs Equivalent         : {total_teus:,}")
    print(f"  Total Execution Time          : {total_bench_time:.3f} seconds")
    print(f"  Throughput (Shipments / Sec)  : {throughput_sec:.1f} shipments/sec")
    print(f"  Throughput (TEUs / Sec)       : {teus_sec:.1f} TEUs/sec")
    print(f"  Total CargoWise XML Generated : {total_xml_bytes / (1024 * 1024):.2f} MB")
    print("-" * 75)
    print(f"  LATENCY PROFILE (Per Document Processing Time):")
    print(f"    • Minimum Latency : {min_lat:.3f} ms")
    print(f"    • Mean Latency    : {mean_lat:.3f} ms")
    print(f"    • Median (P50)    : {p50:.3f} ms")
    print(f"    • P95 Latency     : {p95:.3f} ms")
    print(f"    • P99 Latency     : {p99:.3f} ms")
    print(f"    • Maximum Latency : {max_lat:.3f} ms")
    print("-" * 75)
    print(f"  DISCREPANCY DETECTION ACCURACY:")
    print(f"    • ISO 6346 Checksum Accuracy : {detected_checksum_count}/{total_injected_checksum} ({(detected_checksum_count / max(1, total_injected_checksum)) * 100:.1f}%)")
    print(f"    • SOLAS VGM Overweight Recog : {detected_overweight_count}/{total_injected_overweight} ({(detected_overweight_count / max(1, total_injected_overweight)) * 100:.1f}%)")
    print(f"    • Slot Over-Allocation Catch : {detected_slot_count}/{total_injected_slot} ({(detected_slot_count / max(1, total_injected_slot)) * 100:.1f}%)")
    print("-" * 75)

    # Annual Scale Extrapolation for DahNAY (120,000 TEUs/year)
    annual_teus = 120000
    avg_teu_per_shipment = total_teus / num_shipments
    annual_shipments = int(annual_teus / avg_teu_per_shipment)
    annual_runtime_sec = annual_shipments / throughput_sec
    annual_runtime_min = annual_runtime_sec / 60.0

    # Manual Baseline Comparison (20 mins per SI manual entry)
    manual_hours = (annual_shipments * 20.0) / 60.0
    fte_documentation_execs = manual_hours / (8 * 250)  # 250 work days, 8 hrs/day
    amendment_penalties_prevented = (total_injected_checksum + total_injected_overweight) / num_shipments * annual_shipments * 150  # $150/error

    print(f"\n  EXTRAPOLATION TO DAHNAY'S ANNUAL VOLUME (120,000 TEUs):")
    print(f"    • Estimated Annual SIs Needed      : {annual_shipments:,} documents")
    print(f"    • Automated Processing Run Time    : {annual_runtime_min:.1f} minutes ({annual_runtime_sec:.1f} seconds total!)")
    print(f"    • Manual Operator Time Saved       : {manual_hours:,.0f} hours / year")
    print(f"    • Equivalent Full-Time Headcount   : ~{fte_documentation_execs:.1f} Documentation Executives")
    print(f"    • B/L Amendment Penalties Prevented: ${amendment_penalties_prevented:,.0f} USD (~₹{amendment_penalties_prevented * 86.5 / 100000:.1f} Lakhs)")
    print("=" * 75)

    return {
        "num_shipments": num_shipments,
        "total_teus": total_teus,
        "throughput_sec": throughput_sec,
        "mean_lat": mean_lat,
        "p50": p50,
        "p95": p95,
        "p99": p99,
        "annual_shipments": annual_shipments,
        "annual_runtime_min": annual_runtime_min,
        "manual_hours_saved": manual_hours,
        "fte_saved": fte_documentation_execs,
        "amendment_penalties_usd": amendment_penalties_prevented
    }


if __name__ == "__main__":
    count = 1000
    if len(sys.argv) > 1:
        try:
            count = int(sys.argv[1])
        except ValueError:
            pass
    run_scalability_benchmark(count)
