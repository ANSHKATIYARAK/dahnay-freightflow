"""
DahNAY FreightFlow Engine: Reconciliation & Discrepancy Gatekeeper
Cross-references extracted Shipping Instructions against ERP Master Booking slots.
Uses RapidFuzz for entity verification and ISO 6346 for container integrity.
"""

import uuid
from typing import List
from rapidfuzz import fuzz

from dahnay_logistics.engine.models import (
    ShippingInstruction,
    MasterBookingRecord,
    DiscrepancyFlag,
    DiscrepancySeverity,
    ReconciliationResult
)
from dahnay_logistics.engine.checksum import PortLocationValidator


class DahNAYReconciliationEngine:
    """Enterprise audit engine eliminating BL amendments and VGM weight rejections."""

    @staticmethod
    def audit(si: ShippingInstruction, job: MasterBookingRecord) -> ReconciliationResult:
        flags: List[DiscrepancyFlag] = []

        # 1. Booking Reference Exact Match
        if si.booking_reference.strip().upper() != job.booking_reference.strip().upper():
            flags.append(DiscrepancyFlag(
                field_name="booking_reference",
                si_value=si.booking_reference,
                job_value=job.booking_reference,
                severity=DiscrepancySeverity.CRITICAL,
                issue_description=f"Booking Ref Mismatch: SI indicates '{si.booking_reference}' while ERP booking is '{job.booking_reference}'.",
                remedy_suggestion="Hold job immediately. Check booking transfer note with carrier."
            ))

        # 2. Container ISO 6346 Checksum Audit
        for cntr in si.containers:
            if not cntr.is_valid_iso6346:
                flags.append(DiscrepancyFlag(
                    field_name=f"container_{cntr.container_number}",
                    si_value=cntr.container_number,
                    job_value=f"Check Digit {cntr.iso_check_digit}",
                    severity=DiscrepancySeverity.CRITICAL,
                    issue_description=f"Invalid Container Checksum: '{cntr.container_number}' failed ISO 6346 algorithm (Expected digit: {cntr.iso_check_digit}).",
                    remedy_suggestion="Verify physical container door photo or EIR gate ticket to correct typo."
                ))

        # 3. SOLAS VGM Weight Tolerance Audit
        weight_diff = si.total_gross_weight_kg - job.approved_weight_limit_kg
        if weight_diff > 500.0:
            flags.append(DiscrepancyFlag(
                field_name="total_gross_weight_kg",
                si_value=f"{si.total_gross_weight_kg:,.1f} KGS",
                job_value=f"{job.approved_weight_limit_kg:,.1f} KGS",
                severity=DiscrepancySeverity.CRITICAL,
                issue_description=f"Overweight Alert: SI weight exceeds carrier approved slot by {weight_diff:,.1f} KGS (VGM Shut-Out Risk).",
                remedy_suggestion="Request shipper re-weighing certificate or buy additional slot weight allocation from MSC."
            ))
        elif abs(weight_diff) > 50.0:
            flags.append(DiscrepancyFlag(
                field_name="total_gross_weight_kg",
                si_value=f"{si.total_gross_weight_kg:,.1f} KGS",
                job_value=f"{job.approved_weight_limit_kg:,.1f} KGS",
                severity=DiscrepancySeverity.WARNING,
                issue_description=f"Weight Variance: SI deviates from booking manifest by {weight_diff:,.1f} KGS.",
                remedy_suggestion="Transmit amended VGM to terminal before cutoff to prevent gate-in demurrage."
            ))

        # 4. Port Validation (UN/LOCODE)
        si_pol_code, _ = PortLocationValidator.resolve_port(si.port_of_loading)
        job_pol_code, _ = PortLocationValidator.resolve_port(job.pol)
        if si_pol_code != job_pol_code and si_pol_code != "UNKNOWN":
            flags.append(DiscrepancyFlag(
                field_name="port_of_loading",
                si_value=f"{si.port_of_loading} ({si_pol_code})",
                job_value=f"{job.pol} ({job_pol_code})",
                severity=DiscrepancySeverity.CRITICAL,
                issue_description="Port of Loading conflict between Shipping Instructions and Carrier Booking.",
                remedy_suggestion="Verify port call terminal with DahNAY operations desk."
            ))

        si_pod_code, _ = PortLocationValidator.resolve_port(si.port_of_discharge)
        job_pod_code, _ = PortLocationValidator.resolve_port(job.pod)
        if si_pod_code != job_pod_code and si_pod_code != "UNKNOWN":
            flags.append(DiscrepancyFlag(
                field_name="port_of_discharge",
                si_value=f"{si.port_of_discharge} ({si_pod_code})",
                job_value=f"{job.pod} ({job_pod_code})",
                severity=DiscrepancySeverity.CRITICAL,
                issue_description="Port of Discharge mismatch! Container risks landing in wrong international terminal.",
                remedy_suggestion="Do not issue draft BL. Carrier charges $150 USD amendment fee if filed."
            ))

        # 5. Fuzzy Shipper & Consignee Similarity Check (RapidFuzz)
        shipper_sim = fuzz.token_set_ratio(si.shipper_name.lower(), job.customer_account.lower())
        if shipper_sim < 70.0:
            flags.append(DiscrepancyFlag(
                field_name="shipper_name",
                si_value=si.shipper_name,
                job_value=job.customer_account,
                severity=DiscrepancySeverity.WARNING,
                issue_description=f"Shipper Entity Name Variance ({round(shipper_sim)}% similarity match).",
                remedy_suggestion="Confirm if booking is booked under a freight forwarder/sister concern account."
            ))

        # 6. Container Count Discrepancy
        if len(si.containers) != job.approved_containers_count:
            flags.append(DiscrepancyFlag(
                field_name="containers_count",
                si_value=len(si.containers),
                job_value=job.approved_containers_count,
                severity=DiscrepancySeverity.CRITICAL,
                issue_description=f"Container count mismatch: SI lists {len(si.containers)}, booking confirmed for {job.approved_containers_count}.",
                remedy_suggestion="Confirm part-shipment or request booking amendment with shipping line."
            ))

        # 7. HS Code Check
        if not si.hs_code or len(si.hs_code.replace(".", "")) < 4:
            flags.append(DiscrepancyFlag(
                field_name="hs_code",
                si_value=si.hs_code or "MISSING",
                job_value="6109.10",
                severity=DiscrepancySeverity.WARNING,
                issue_description="Incomplete HS Tariff Code in Shipping Instructions.",
                remedy_suggestion="Request 6-digit Harmonized Tariff code from shipper for ICEGATE EDI submission."
            ))

        # Overall Status
        has_critical = any(f.severity == DiscrepancySeverity.CRITICAL for f in flags)
        has_warning = any(f.severity == DiscrepancySeverity.WARNING for f in flags)

        if has_critical:
            status = "CRITICAL_REJECT"
            conf = max(0.40, 0.95 - (len(flags) * 0.12))
        elif has_warning:
            status = "FLAGGED_FOR_REVIEW"
            conf = max(0.70, 0.95 - (len(flags) * 0.05))
        else:
            status = "MATCHED"
            conf = 0.99

        return ReconciliationResult(
            reconciliation_id=f"AUD-{uuid.uuid4().hex[:8].upper()}",
            booking_reference=si.booking_reference,
            match_status=status,
            confidence_score=round(conf, 2),
            flags=flags
        )
