"""
FreightFlow AI: Discrepancy & Validation Engine
Cross-checks incoming Shipping Instructions against Master Job Records to eliminate
costly Bill of Lading (BL) amendment fees, weight misdeclarations, and customs penalties.
"""

import uuid
from typing import List
from freight_flow.models import (
    ShippingInstruction,
    MasterJobRecord,
    DiscrepancyFlag,
    DiscrepancySeverity,
    ReconciliationResult
)


class FreightReconciliationEngine:
    """Automated cross-check engine protecting freight forwarders from documentation errors."""

    @staticmethod
    def audit_shipping_instruction(si: ShippingInstruction, job: MasterJobRecord) -> ReconciliationResult:
        flags: List[DiscrepancyFlag] = []

        # 1. Booking Reference Check
        if si.booking_reference.strip().upper() != job.booking_reference.strip().upper():
            flags.append(DiscrepancyFlag(
                field_name="booking_reference",
                si_value=si.booking_reference,
                job_value=job.booking_reference,
                severity=DiscrepancySeverity.CRITICAL,
                issue_description=f"Booking reference mismatch: SI states '{si.booking_reference}' but Master Job is '{job.booking_reference}'.",
                remedy_suggestion="Verify booking confirmation with carrier line before issuing draft BL."
            ))

        # 2. Port of Loading (POL) Check
        if job.pol.lower() not in si.port_of_loading.lower() and si.port_of_loading.lower() not in job.pol.lower():
            flags.append(DiscrepancyFlag(
                field_name="port_of_loading",
                si_value=si.port_of_loading,
                job_value=job.pol,
                severity=DiscrepancySeverity.CRITICAL,
                issue_description=f"Port of Loading mismatch: SI specifies '{si.port_of_loading}' while job booking was confirmed for '{job.pol}'.",
                remedy_suggestion="Confirm departure terminal with shipper; cargo will be rejected at gate if vessel routing differs."
            ))

        # 3. Port of Discharge (POD) Check
        if job.pod.lower() not in si.port_of_discharge.lower() and si.port_of_discharge.lower() not in job.pod.lower():
            flags.append(DiscrepancyFlag(
                field_name="port_of_discharge",
                si_value=si.port_of_discharge,
                job_value=job.pod,
                severity=DiscrepancySeverity.CRITICAL,
                issue_description=f"Port of Discharge mismatch: SI states '{si.port_of_discharge}', Master Job specifies '{job.pod}'.",
                remedy_suggestion="Hold BL generation. Carrier will charge $100+ amendment fee if filed incorrectly."
            ))

        # 4. Gross Weight Overload Check (>5% variance or exceeding approved limit)
        weight_variance = si.total_gross_weight_kg - job.approved_weight_limit_kg
        if weight_variance > 500.0:  # Exceeds by more than 500 kg
            flags.append(DiscrepancyFlag(
                field_name="total_gross_weight_kg",
                si_value=f"{si.total_gross_weight_kg} kg",
                job_value=f"{job.approved_weight_limit_kg} kg",
                severity=DiscrepancySeverity.CRITICAL,
                issue_description=f"Overweight alert: SI weight ({si.total_gross_weight_kg} kg) exceeds approved slot limit by {round(weight_variance, 1)} kg.",
                remedy_suggestion="Request shipper re-weighing (VGM check) or buy additional slot weight allocation from carrier line."
            ))
        elif abs(weight_variance) > 50.0:
            flags.append(DiscrepancyFlag(
                field_name="total_gross_weight_kg",
                si_value=f"{si.total_gross_weight_kg} kg",
                job_value=f"{job.approved_weight_limit_kg} kg",
                severity=DiscrepancySeverity.WARNING,
                issue_description=f"Weight variance: SI weight differs from preliminary booking by {round(weight_variance, 1)} kg.",
                remedy_suggestion="Update VGM (Verified Gross Mass) in customs portal to prevent container shut-out."
            ))

        # 5. Consignee Entity Cross-Check
        if job.expected_consignee.lower() not in si.consignee_name.lower():
            flags.append(DiscrepancyFlag(
                field_name="consignee_name",
                si_value=si.consignee_name,
                job_value=job.expected_consignee,
                severity=DiscrepancySeverity.WARNING,
                issue_description=f"Consignee variance: SI names '{si.consignee_name}', while job order expected '{job.expected_consignee}'.",
                remedy_suggestion="Confirm if cargo was sold high-seas or consigned 'TO ORDER OF SHIPPER' before printing Negotiable BL."
            ))

        # 6. Container Count Discrepancy
        if len(si.containers) != job.expected_containers_count:
            flags.append(DiscrepancyFlag(
                field_name="containers_count",
                si_value=len(si.containers),
                job_value=job.expected_containers_count,
                severity=DiscrepancySeverity.CRITICAL,
                issue_description=f"Container count mismatch: SI lists {len(si.containers)} container(s), booking was confirmed for {job.expected_containers_count}.",
                remedy_suggestion="Check if part-shipment or if additional container was gated in."
            ))

        # 7. HS Code Validation
        if not si.hs_code or len(si.hs_code.replace(".", "")) < 4:
            flags.append(DiscrepancyFlag(
                field_name="hs_code",
                si_value=si.hs_code or "MISSING",
                job_value="Required for EXIM",
                severity=DiscrepancySeverity.WARNING,
                issue_description="HS Code is missing or incomplete in Shipping Instructions.",
                remedy_suggestion="Request 6-digit Harmonized Tariff code from shipper to avoid Indian Customs EDI freeze."
            ))

        # Determine overall match status
        has_critical = any(f.severity == DiscrepancySeverity.CRITICAL for f in flags)
        has_warning = any(f.severity == DiscrepancySeverity.WARNING for f in flags)

        if has_critical:
            status = "CRITICAL_REJECT"
            confidence = max(0.30, 0.95 - (len(flags) * 0.15))
        elif has_warning:
            status = "FLAGGED_FOR_REVIEW"
            confidence = max(0.65, 0.95 - (len(flags) * 0.08))
        else:
            status = "MATCHED"
            confidence = 0.99

        return ReconciliationResult(
            reconciliation_id=f"REC-{uuid.uuid4().hex[:8].upper()}",
            booking_reference=si.booking_reference,
            match_status=status,
            confidence_score=round(confidence, 2),
            flags=flags
        )
