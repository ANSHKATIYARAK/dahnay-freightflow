"""
VentureOS: Product Archetype Catalog
Modular templates for generating diverse SaaS utilities across any vertical.
"""

from typing import Dict, List, Any
from pydantic import BaseModel, Field


class ArchetypeDefinition(BaseModel):
    archetype_id: str
    name: str
    category: str
    description: str
    typical_buyer: str
    average_setup_fee_inr: float
    average_monthly_fee_inr: float
    tech_stack: List[str]
    core_modules: List[str]
    default_selectors_or_endpoints: Dict[str, str] = Field(default_factory=dict)
    sample_pains: List[str] = Field(default_factory=list)


ARCHETYPES: Dict[str, ArchetypeDefinition] = {
    "price_radar": ArchetypeDefinition(
        archetype_id="price_radar",
        name="24/7 E-Commerce Price & Buy Box Sentinel",
        category="E-Commerce Intelligence",
        description="Continuously monitors product listings on Amazon, Flipkart, and Meesho to catch price undercutting and Buy Box hijackers.",
        typical_buyer="D2C Brand Founders, Amazon/Meesho Sellers",
        average_setup_fee_inr=15000.0,
        average_monthly_fee_inr=8000.0,
        tech_stack=["Playwright", "FastAPI", "Telegram Bot API", "SQLite"],
        core_modules=["scraper_worker", "buybox_detector", "telegram_alert_bot", "history_db"],
        default_selectors_or_endpoints={
            "title": "#productTitle",
            "price": ".a-price .a-offscreen",
            "seller": "#merchant-info"
        },
        sample_pains=[
            "Losing Buy Box at 3 AM to unauthorized 3rd-party sellers",
            "Competitors violating Minimum Advertised Price (MAP)"
        ]
    ),
    "lead_enricher": ArchetypeDefinition(
        archetype_id="lead_enricher",
        name="B2B Hyper-Local Lead Discovery & Enrichment Radar",
        category="Sales Intelligence",
        description="Scrapes Google Maps, industry directories, and LinkedIn to enrich decision-maker emails, phone numbers, and tech stack tags.",
        typical_buyer="Marketing Agencies, B2B SaaS Founders, Consultants",
        average_setup_fee_inr=20000.0,
        average_monthly_fee_inr=10000.0,
        tech_stack=["HTTPX", "BeautifulSoup4", "Apollo/Hunter API", "FastAPI"],
        core_modules=["directory_crawler", "contact_extractor", "enrichment_engine", "csv_exporter"],
        default_selectors_or_endpoints={
            "business_name": "h1.entry-title",
            "phone": "a[href^='tel:']",
            "email": "a[href^='mailto:']"
        },
        sample_pains=[
            "Paying $200/mo for Apollo with outdated Indian phone numbers",
            "Spending 15 hours a week manually copying local business contacts"
        ]
    ),
    "content_monitor": ArchetypeDefinition(
        archetype_id="content_monitor",
        name="Social & Brand Mention Social Listening Sentinel",
        category="Brand Protection & PR",
        description="Tracks Reddit, Twitter/X, and YouTube for high-intent keywords, competitor mentions, and unresolved customer complaints.",
        typical_buyer="D2C Brands, PR Agencies, SaaS Marketers",
        average_setup_fee_inr=12000.0,
        average_monthly_fee_inr=6000.0,
        tech_stack=["Reddit API / PRAW", "Twitter Scraper", "Discord/Slack Webhooks"],
        core_modules=["feed_listener", "sentiment_classifier", "lead_qualifier", "slack_notifier"],
        sample_pains=[
            "Missing high-intent 'looking for alternative to X' posts on Reddit",
            "Slow response to viral negative reviews on Twitter"
        ]
    ),
    "doc_processor": ArchetypeDefinition(
        archetype_id="doc_processor",
        name="Automated Invoice & Tax Document Parser",
        category="Operations & FinTech",
        description="Parses PDF invoices, GST challans, and delivery receipts, extracting line items into structured Google Sheets / ERPs.",
        typical_buyer="Chartered Accountants, Logistics Managers, CFOs",
        average_setup_fee_inr=25000.0,
        average_monthly_fee_inr=12000.0,
        tech_stack=["PyMuPDF", "FastAPI", "Google Sheets API", "Pydantic"],
        core_modules=["pdf_extractor", "gst_validator", "line_item_normalizer", "erp_sync"],
        sample_pains=[
            "Accountants manually entering 400 vendor invoices into Tally every week",
            "GST mismatch errors costing penalties during monthly reconciliation"
        ]
    ),
    "api_wrapper": ArchetypeDefinition(
        archetype_id="api_wrapper",
        name="Legacy Portal Headless API & Webhook Wrapper",
        category="Developer Infrastructure",
        description="Turns portal websites lacking public APIs into high-speed JSON endpoints with webhook notifications.",
        typical_buyer="Tech Leads, Automation Specialists, No-Code Builders",
        average_setup_fee_inr=18000.0,
        average_monthly_fee_inr=9000.0,
        tech_stack=["FastAPI", "Playwright", "Redis Queue", "Docker"],
        core_modules=["session_manager", "portal_automation", "rest_gateway", "webhook_dispatcher"],
        sample_pains=[
            "Government/vendor portal has no API, requiring staff to log in 50x daily",
            "Need real-time sync with legacy legacy databases"
        ]
    )
}


def get_archetype(archetype_id: str) -> ArchetypeDefinition:
    """Retrieves an archetype definition or raises KeyError."""
    if archetype_id not in ARCHETYPES:
        raise KeyError(f"Archetype '{archetype_id}' not found. Available: {list(ARCHETYPES.keys())}")
    return ARCHETYPES[archetype_id]
