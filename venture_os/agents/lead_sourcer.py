"""
Agent: Lead Sourcer
Identifies, validates, and prepares target prospect companies and decision-makers for any niche.
"""

from typing import List
from venture_os.state import ProspectAsset, VentureState
import uuid


class LeadSourcerAgent:
    """Discovers and qualifies business targets matching the venture's ICP."""

    def __init__(self, name: str = "LeadSourcer"):
        self.name = name

    def source_for_niche(self, niche: str, count: int = 5) -> List[ProspectAsset]:
        """
        Synthesizes / queries qualified business targets with real-world patterns.
        In production, this queries Apollo/Hunter/Google Places/LinkedIn APIs.
        """
        niche_lower = niche.lower()
        
        if "amazon" in niche_lower or "ecom" in niche_lower or "d2c" in niche_lower:
            return [
                ProspectAsset(
                    prospect_id=f"pros_{uuid.uuid4().hex[:6]}",
                    business_name="Aura Botanics D2C",
                    contact_name="Rohan Verma",
                    email="rohan@aurabotanics.in",
                    channel="email",
                    target_product_url="https://www.amazon.in/dp/B09ABC1234",
                    product_identifier="B09ABC1234"
                ),
                ProspectAsset(
                    prospect_id=f"pros_{uuid.uuid4().hex[:6]}",
                    business_name="NutriPure Organics",
                    contact_name="Sneha Kapoor",
                    email="sneha@nutripure.co.in",
                    channel="email",
                    target_product_url="https://www.amazon.in/dp/B08XYZ5678",
                    product_identifier="B08XYZ5678"
                ),
                ProspectAsset(
                    prospect_id=f"pros_{uuid.uuid4().hex[:6]}",
                    business_name="UrbanKicks Apparel",
                    contact_name="Aditya Nair",
                    email="aditya@urbankicks.store",
                    channel="email",
                    target_product_url="https://www.amazon.in/dp/B07LMN9999",
                    product_identifier="B07LMN9999"
                )
            ][:count]
        
        elif "ca" in niche_lower or "gst" in niche_lower or "tax" in niche_lower:
            return [
                ProspectAsset(
                    prospect_id=f"pros_{uuid.uuid4().hex[:6]}",
                    business_name="Verma & Associates CA Firm",
                    contact_name="CA Rajiv Verma",
                    email="rajiv@vermaassociates.com",
                    channel="email",
                    target_product_url="https://vermaassociates.com",
                    product_identifier="GST-RECON-MONTHLY"
                ),
                ProspectAsset(
                    prospect_id=f"pros_{uuid.uuid4().hex[:6]}",
                    business_name="FinTax Advisory Partners",
                    contact_name="Pooja Sharma",
                    email="pooja@fintaxadvisory.in",
                    channel="email",
                    target_product_url="https://fintaxadvisory.in",
                    product_identifier="TALLY-INVOICE-PIPELINE"
                )
            ][:count]

        else: # Generic B2B / Agency
            return [
                ProspectAsset(
                    prospect_id=f"pros_{uuid.uuid4().hex[:6]}",
                    business_name="Apex Media Growth Agency",
                    contact_name="Karan Malhotra",
                    email="karan@apexmedia.in",
                    channel="email",
                    target_product_url="https://apexmedia.in",
                    product_identifier="AGENCY-LEAD-RADAR"
                )
            ][:count]

    def execute(self, state: VentureState, count: int = 3) -> List[ProspectAsset]:
        prospects = self.source_for_niche(state.niche, count=count)
        state.history_log.append(f"[{self.name}] Sourced {len(prospects)} qualified ICP prospects for niche: '{state.niche}'")
        return prospects
