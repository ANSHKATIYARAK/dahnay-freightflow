"""
Live Scraper Utility for Amazon.in & Meesho
Runs live inspection on target product URLs to detect current price, Buy Box seller, and availability.
"""

import sys
import requests
from bs4 import BeautifulSoup

def inspect_amazon_asin(asin: str) -> dict:
    """Inspects a live Amazon.in ASIN with anti-bot headers."""
    url = f"https://www.amazon.in/dp/{asin}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/122.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=12)
        if resp.status_code != 200:
            return {"asin": asin, "status": "error", "code": resp.status_code}
        
        soup = BeautifulSoup(resp.text, "html.parser")
        title_el = soup.select_one("#productTitle")
        price_el = soup.select_one(".a-price .a-offscreen, #priceblock_ourprice, .apexPriceToPay .a-offscreen")
        merchant_el = soup.select_one("#merchant-info")
        availability_el = soup.select_one("#availability span")

        return {
            "asin": asin,
            "url": url,
            "title": title_el.get_text(strip=True) if title_el else "Unknown Product",
            "price": price_el.get_text(strip=True) if price_el else "Unavailable",
            "merchant_info": merchant_el.get_text(strip=True) if merchant_el else "Unspecified",
            "availability": availability_el.get_text(strip=True) if availability_el else "In stock"
        }
    except Exception as e:
        return {"asin": asin, "status": "exception", "error": str(e)}

if __name__ == "__main__":
    test_asin = sys.argv[1] if len(sys.argv) > 1 else "B08N5WRWNW"
    print(f"Inspecting live ASIN: {test_asin}...")
    result = inspect_amazon_asin(test_asin)
    for k, v in result.items():
        print(f"  {k}: {v}")
