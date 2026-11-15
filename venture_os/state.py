"""
VentureOS: Autonomous Micro-SaaS Foundry & GTM Pipeline
State Contracts & Data Models (Pydantic V2)
"""

from typing import List, Dict, Optional, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class PainSignal(BaseModel):
    """Raw friction signal discovered from market chatter."""
    signal_id: str
    niche: str
    source_platform: Literal["reddit", "seller_forums", "twitter", "marketplace_reviews", "manual"]
    raw_quote: str
    target_persona: str
    current_workaround: str
    estimated_monthly_loss_inr: float = Field(..., description="Estimated cost of inaction in INR")
    urgency_score: float = Field(..., ge=1.0, le=10.0, description="Urgency rated 1-10")


class FeasibilityReport(BaseModel):
    """Rigorous stress-test evaluation to prevent building zero-demand/commodity tools."""
    passed: bool
    score: float = Field(..., ge=0.0, le=10.0)
    anti_bot_difficulty: Literal["low", "medium", "high", "extreme"]
    proxy_cost_risk: Literal["negligible", "moderate", "prohibitive"]
    incumbent_competition: str = Field(..., description="e.g. Keepa, Helium10, SellerApp")
    why_incumbents_fail: str = Field(..., description="The unique delta (e.g. instant mobile alert vs dashboard lag)")
    kill_reason: Optional[str] = None


class ProductSpec(BaseModel):
    """Technical specification for the micro-utility."""
    product_id: str
    name: str
    core_utility: str
    target_platform: str
    supported_metrics: List[str]
    alert_channels: List[str] = Field(default_factory=lambda: ["telegram", "email"])
    selector_config: Dict[str, str] = Field(default_factory=dict)
    executable_code_snippet: Optional[str] = None
    verification_status: Literal["untested", "passed", "failed"] = "untested"


class ProspectAsset(BaseModel):
    """Live prospect company or seller data for pre-computation."""
    prospect_id: str
    business_name: str
    contact_name: str
    email: Optional[str] = None
    channel: Literal["email", "linkedin", "telegram"] = "email"
    target_product_url: str
    product_identifier: str  # ASIN or SKU


class ProofOfLossAudit(BaseModel):
    """Pre-computed value audit run against the prospect's real data before reaching out."""
    audit_id: str
    prospect_id: str
    product_identifier: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    buy_box_owned: bool
    current_winner: str
    client_price_inr: float
    winning_price_inr: float
    competitors_detected: int
    estimated_weekly_revenue_leak_inr: float
    audit_summary: str


class OutreachHook(BaseModel):
    """Hyper-personalized outbound message embedding the pre-computed audit."""
    hook_id: str
    prospect_id: str
    subject_line: str
    body_markdown: str
    call_to_action: str
    pilot_price_inr: float = 5000.0


class PipelineTelemetry(BaseModel):
    """Telemetry tracking to enforce statistical kill criteria."""
    total_prospects_audited: int = 0
    total_outreach_sent: int = 0
    positive_replies: int = 0
    pilots_signed: int = 0
    conversion_rate: float = 0.0
    status: Literal["active", "evaluating", "killed", "graduated"] = "active"
    kill_criteria_threshold: float = 0.03  # 3% positive response rate required


class VentureState(BaseModel):
    """The master immutable state passed along the deterministic state machine."""
    venture_id: str
    niche: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    pain_signal: Optional[PainSignal] = None
    feasibility: Optional[FeasibilityReport] = None
    product_spec: Optional[ProductSpec] = None
    audits: List[ProofOfLossAudit] = Field(default_factory=list)
    outreach_campaign: List[OutreachHook] = Field(default_factory=list)
    telemetry: PipelineTelemetry = Field(default_factory=PipelineTelemetry)
    history_log: List[str] = Field(default_factory=list)
