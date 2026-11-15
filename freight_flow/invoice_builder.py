"""
FreightFlow AI: Commercial Freight Invoice Builder
Pre-fills export/import freight invoices automatically from verified Shipping Instructions & Job tariffs.
"""

import uuid
from datetime import datetime, timedelta
from freight_flow.models import (
    ShippingInstruction,
    MasterJobRecord,
    ReconciliationResult,
    PreFilledInvoice,
    InvoiceLineItem,
    FreightTerms
)


class FreightInvoiceBuilder:
    """Generates pre-filled, compliant commercial freight invoices ready for ERP sync."""

    USD_TO_INR_RATE = 86.50

    @classmethod
    def generate_invoice(
        cls,
        si: ShippingInstruction,
        job: MasterJobRecord,
        audit: ReconciliationResult
    ) -> PreFilledInvoice:
        inv_number = f"INV-{datetime.utcnow().strftime('%Y%m')}-{uuid.uuid4().hex[:5].upper()}"
        today = datetime.utcnow().strftime("%Y-%m-%d")
        due = (datetime.utcnow() + timedelta(days=15)).strftime("%Y-%m-%d")

        # Determine bill-to
        bill_to = si.shipper_name if si.freight_terms == FreightTerms.PREPAID else si.consignee_name

        # Calculate charges
        line_items = []

        # 1. Ocean Freight
        ocean_freight_inr = job.agreed_ocean_freight_usd * cls.USD_TO_INR_RATE
        line_items.append(InvoiceLineItem(
            description=f"Basic Ocean Freight ({si.vessel_name} / {si.voyage_number}) - {len(si.containers)} x 40HC",
            currency="USD",
            rate=job.agreed_ocean_freight_usd,
            quantity=float(len(si.containers)),
            amount=job.agreed_ocean_freight_usd * len(si.containers)
        ))

        # 2. Terminal Handling Charges (THC)
        line_items.append(InvoiceLineItem(
            description=f"Terminal Handling Charges (THC) - {si.port_of_loading}",
            currency="INR",
            rate=job.terminal_handling_charges_inr,
            quantity=float(len(si.containers)),
            amount=job.terminal_handling_charges_inr * len(si.containers)
        ))

        # 3. Bill of Lading (BL) Documentation Fee
        line_items.append(InvoiceLineItem(
            description="Bill of Lading Documentation & EDI Customs Transmission Fee",
            currency="INR",
            rate=job.documentation_fee_inr,
            quantity=1.0,
            amount=job.documentation_fee_inr
        ))

        # 4. Port Congestion / Fuel Surcharge (BAF/CAF)
        baf_surcharge_usd = 120.0 * len(si.containers)
        line_items.append(InvoiceLineItem(
            description="Bunker Adjustment Factor (BAF) / Fuel Environmental Surcharge",
            currency="USD",
            rate=120.0,
            quantity=float(len(si.containers)),
            amount=baf_surcharge_usd
        ))

        # Totals
        total_usd = (job.agreed_ocean_freight_usd * len(si.containers)) + baf_surcharge_usd
        total_inr = (
            (job.terminal_handling_charges_inr * len(si.containers))
            + job.documentation_fee_inr
            + (total_usd * cls.USD_TO_INR_RATE)
        )

        return PreFilledInvoice(
            invoice_number=inv_number,
            job_reference=job.job_id,
            bill_to_party=bill_to,
            tax_id_gstin="33AABCD1234E1Z9",
            invoice_date=today,
            due_date=due,
            line_items=line_items,
            total_amount_inr=round(total_inr, 2),
            total_amount_usd=round(total_usd, 2),
            reconciliation_verified=(audit.match_status == "MATCHED"),
            status="READY_FOR_APPROVAL" if audit.match_status == "MATCHED" else "PENDING_EXCEPTION_CLEARANCE"
        )
