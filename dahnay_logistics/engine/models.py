"""
DahNAY FreightFlow Engine: Enterprise Data Models
Typed schemas for multimodal shipping instructions, CargoWise job records,
discrepancies, and commercial invoices.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class FreightTerms(str, Enum):
    PREPAID = "PREPAID"
    COLLECT = "COLLECT"


class DiscrepancySeverity(str, Enum):
    CRITICAL = "CRITICAL"  # Blocker: Weight mismatch (>500kg), invalid container checksum, wrong port
    WARNING = "WARNING"    # Potential amendment fee: Spelling, missing HS code, slight weight diff
    INFO = "INFO"          # Auto-resolved default


class ContainerDetail(BaseModel):
    container_number: str
    seal_number: str
    container_type: str = "40HC"
    gross_weight_kg: float
    cbm: float
    packages_count: int
    is_valid_iso6346: bool = True
    iso_check_digit: Optional[int] = None


class ShippingInstruction(BaseModel):
    si_number: str
    booking_reference: str
    shipper_name: str
    shipper_address: str
    shipper_iec: Optional[str] = None
    shipper_gstin: Optional[str] = None
    consignee_name: str
    consignee_address: str
    consignee_tax_id: Optional[str] = None
    notify_party: Optional[str] = "SAME AS CONSIGNEE"
    vessel_name: str
    voyage_number: str
    port_of_loading: str
    port_of_discharge: str
    final_destination: Optional[str] = None
    freight_terms: FreightTerms = FreightTerms.PREPAID
    cargo_description: str
    hs_code: Optional[str] = None
    total_packages: int
    package_type: str = "Cartons"
    total_gross_weight_kg: float
    total_cbm: float
    containers: List[ContainerDetail] = Field(default_factory=list)
    raw_document_source: Optional[str] = None
    extraction_confidence: float = 1.0


class MasterBookingRecord(BaseModel):
    job_id: str
    booking_reference: str
    customer_account: str
    carrier_line: str
    pol: str
    pod: str
    vessel_scheduled: str
    voyage_scheduled: str
    approved_weight_limit_kg: float
    approved_containers_count: int
    container_type: str = "40HC"
    ocean_freight_usd: float
    terminal_handling_charges_inr: float
    documentation_fee_inr: float = 4500.00
    baf_fuel_surcharge_usd: float = 120.00
    gst_rate: float = 18.0


class DiscrepancyFlag(BaseModel):
    field_name: str
    si_value: Any
    job_value: Any
    severity: DiscrepancySeverity
    issue_description: str
    remedy_suggestion: str


class ReconciliationResult(BaseModel):
    reconciliation_id: str
    booking_reference: str
    match_status: str  # "MATCHED", "FLAGGED_FOR_REVIEW", "CRITICAL_REJECT"
    confidence_score: float
    flags: List[DiscrepancyFlag] = Field(default_factory=list)
    audit_timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class InvoiceLineItem(BaseModel):
    description: str
    currency: str
    rate: float
    quantity: float
    amount: float


class CommercialInvoice(BaseModel):
    invoice_number: str
    job_reference: str
    booking_reference: str
    bill_to_party: str
    tax_id_gstin: Optional[str] = None
    invoice_date: str
    due_date: str
    line_items: List[InvoiceLineItem] = Field(default_factory=list)
    total_usd: float
    total_inr: float
    gst_amount_inr: float
    grand_total_inr: float
    reconciliation_passed: bool
    status: str = "DRAFT"
