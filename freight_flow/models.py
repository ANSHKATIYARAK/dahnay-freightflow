"""
FreightFlow AI: Data Models
Defines typed schemas for Shipping Instructions (SI), Master Job Orders, 
Discrepancy Audit Flags, and Commercial Invoice Pre-fills.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from enum import Enum
from datetime import datetime


class FreightTerms(str, Enum):
    PREPAID = "PREPAID"
    COLLECT = "COLLECT"


class DiscrepancySeverity(str, Enum):
    CRITICAL = "CRITICAL"  # Blocker: Weight mismatch, wrong port, invalid container
    WARNING = "WARNING"    # Potential amendment fee: Spelling, missing HS code
    INFO = "INFO"          # Auto-resolved default


class ContainerDetail(BaseModel):
    container_number: str
    seal_number: str
    container_type: str = "40HC"  # 20GP, 40GP, 40HC, etc.
    gross_weight_kg: float
    cbm: float
    packages_count: int


class ShippingInstruction(BaseModel):
    si_number: str
    booking_reference: str
    shipper_name: str
    shipper_address: str
    consignee_name: str
    consignee_address: str
    notify_party: Optional[str] = None
    vessel_name: str
    voyage_number: str
    port_of_loading: str
    port_of_discharge: str
    final_destination: Optional[str] = None
    freight_terms: FreightTerms = FreightTerms.PREPAID
    cargo_description: str
    hs_code: Optional[str] = None
    total_packages: int
    total_gross_weight_kg: float
    total_cbm: float
    containers: List[ContainerDetail] = Field(default_factory=list)
    raw_document_source: Optional[str] = None


class MasterJobRecord(BaseModel):
    job_id: str
    booking_reference: str
    customer_account: str
    expected_shipper: str
    expected_consignee: str
    pol: str
    pod: str
    approved_weight_limit_kg: float
    agreed_ocean_freight_usd: float
    terminal_handling_charges_inr: float
    documentation_fee_inr: float = 4500.00
    expected_containers_count: int


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
    confidence_score: float  # 0.0 - 1.0
    flags: List[DiscrepancyFlag] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class InvoiceLineItem(BaseModel):
    description: str
    currency: str
    rate: float
    quantity: float
    amount: float


class PreFilledInvoice(BaseModel):
    invoice_number: str
    job_reference: str
    bill_to_party: str
    tax_id_gstin: Optional[str] = None
    invoice_date: str
    due_date: str
    line_items: List[InvoiceLineItem] = Field(default_factory=list)
    total_amount_inr: float
    total_amount_usd: float
    reconciliation_verified: bool
    status: str = "DRAFT"  # DRAFT, APPROVED, PUSHED_TO_CARGOWISE
