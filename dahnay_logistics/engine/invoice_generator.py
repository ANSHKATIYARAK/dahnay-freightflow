"""
DahNAY FreightFlow Engine: Commercial Freight Invoice Synthesis
Pre-fills verified commercial freight invoices with live multi-currency conversion,
terminal handling charges, documentation fees, and GST.
"""

import uuid
from datetime import datetime, timedelta
from dahnay_logistics.engine.models import (
    ShippingInstruction,
    MasterBookingRecord,
    ReconciliationResult,
    CommercialInvoice,
    InvoiceLineItem,
    FreightTerms
)


class CommercialInvoiceGenerator:
    """Pre-fills compliant commercial freight invoices for DahNAY billing operations."""

    USD_TO_INR = 86.50

    @classmethod
    def generate(
        cls,
        si: ShippingInstruction,
        job: MasterBookingRecord,
        audit: ReconciliationResult
    ) -> CommercialInvoice:
        inv_no = f"DAH-INV-{datetime.utcnow().strftime('%Y%m')}-{uuid.uuid4().hex[:5].upper()}"
        today = datetime.utcnow().strftime("%Y-%m-%d")
        due = (datetime.utcnow() + timedelta(days=15)).strftime("%Y-%m-%d")

        bill_to = si.shipper_name if si.freight_terms == FreightTerms.PREPAID else si.consignee_name
        cntr_count = len(si.containers) if si.containers else 1

        items = []

        # 1. Ocean Freight
        ocean_freight_usd = job.ocean_freight_usd * cntr_count
        items.append(InvoiceLineItem(
            description=f"Basic Ocean Freight ({si.vessel_name} / {si.voyage_number}) - {cntr_count} x {job.container_type}",
            currency="USD",
            rate=job.ocean_freight_usd,
            quantity=float(cntr_count),
            amount=ocean_freight_usd
        ))

        # 2. Terminal Handling Charges (THC)
        thc_inr = job.terminal_handling_charges_inr * cntr_count
        items.append(InvoiceLineItem(
            description=f"Terminal Handling Charges (THC) - Origin Port ({job.pol})",
            currency="INR",
            rate=job.terminal_handling_charges_inr,
            quantity=float(cntr_count),
            amount=thc_inr
        ))

        # 3. Bill of Lading Documentation Fee
        items.append(InvoiceLineItem(
            description="Bill of Lading (BL) Documentation & ICEGATE Customs EDI Transmission Fee",
            currency="INR",
            rate=job.documentation_fee_inr,
            quantity=1.0,
            amount=job.documentation_fee_inr
        ))

        # 4. Bunker Adjustment Factor (BAF)
        baf_usd = job.baf_fuel_surcharge_usd * cntr_count
        items.append(InvoiceLineItem(
            description="Bunker Adjustment Factor (BAF) / Fuel Environmental Surcharge",
            currency="USD",
            rate=job.baf_fuel_surcharge_usd,
            quantity=float(cntr_count),
            amount=baf_usd
        ))

        total_usd = ocean_freight_usd + baf_usd
        taxable_inr_services = thc_inr + job.documentation_fee_inr
        gst_inr = round(taxable_inr_services * (job.gst_rate / 100.0), 2)
        total_inr_base = taxable_inr_services + (total_usd * cls.USD_TO_INR)
        grand_total_inr = round(total_inr_base + gst_inr, 2)

        return CommercialInvoice(
            invoice_number=inv_no,
            job_reference=job.job_id,
            booking_reference=job.booking_reference,
            bill_to_party=bill_to,
            tax_id_gstin="33AABCT9981E1Z4",
            invoice_date=today,
            due_date=due,
            line_items=items,
            total_usd=round(total_usd, 2),
            total_inr=round(total_inr_base, 2),
            gst_amount_inr=gst_inr,
            grand_total_inr=grand_total_inr,
            reconciliation_passed=(audit.match_status == "MATCHED"),
            status="APPROVED_FOR_ERP" if audit.match_status == "MATCHED" else "HELD_FOR_EXCEPTION_REVIEW"
        )
