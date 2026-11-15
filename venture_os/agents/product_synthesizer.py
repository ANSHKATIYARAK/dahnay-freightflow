"""
Agent 3: Product Synthesizer
Generates the technical architecture, selector configuration, and runnable code.
"""

from venture_os.state import ProductSpec, VentureState
import uuid


class ProductSynthesizerAgent:
    """Designs and synthesizes the headless automation code."""

    def __init__(self, name: str = "ProductSynthesizer"):
        self.name = name

    def execute(self, state: VentureState) -> VentureState:
        if not state.feasibility or not state.feasibility.passed:
            raise ValueError("Cannot synthesize product: Feasibility test did not pass.")

        spec = ProductSpec(
            product_id=f"prod_{uuid.uuid4().hex[:6]}",
            name="BuyBoxSentinel-IN",
            core_utility="Automated 24/7 Buy Box & Hijacker Radar for Amazon.in & Meesho",
            target_platform="Amazon.in",
            supported_metrics=["current_price", "buy_box_seller", "stock_status", "seller_count"],
            alert_channels=["telegram", "email"],
            selector_config={
                "title": "#productTitle",
                "price": ".a-price .a-offscreen, #priceblock_ourprice, #corePriceDisplay_desktop_feature_div .a-price-whole",
                "merchant_info": "#merchant-info",
                "availability": "#availability span"
            },
            executable_code_snippet="""
import requests
from bs4 import BeautifulSoup

def inspect_asin(asin: str, headers: dict = None) -> dict:
    url = f"https://www.amazon.in/dp/{asin}"
    resp = requests.get(url, headers=headers or {"User-Agent": "Mozilla/5.0"}, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")
    title = soup.select_one("#productTitle")
    price = soup.select_one(".a-price .a-offscreen")
    merchant = soup.select_one("#merchant-info")
    return {
        "asin": asin,
        "title": title.get_text(strip=True) if title else "Unknown",
        "price": price.get_text(strip=True) if price else "0",
        "seller": merchant.get_text(strip=True) if merchant else "Unknown"
    }
""",
            verification_status="untested"
        )

        state.product_spec = spec
        state.history_log.append(f"[{self.name}] Synthesized product specification: {spec.name} ({spec.product_id})")
        return state
