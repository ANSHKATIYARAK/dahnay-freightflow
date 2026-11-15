"""
LinkedIn Profile Extractor via Chrome DevTools Protocol (CDP)
Connects directly to your running Chrome browser on port 9222 to read your logged-in session.
"""

import asyncio
import json
import os
import sys

# Ensure root in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright
from tools.parse_linkedin import parse_linkedin_html
from tools.build_portfolio import build_portfolio

async def extract_from_cdp():
    print("Connecting to live Chrome instance over CDP on http://localhost:9222...")
    async with async_playwright() as p:
        try:
            browser = await p.chromium.connect_over_cdp("http://localhost:9222")
            contexts = browser.contexts
            if not contexts:
                print("✖ No active browser context found on Chrome.")
                return

            context = contexts[0]
            pages = context.pages
            print(f"✔ Connected to Chrome! Found {len(pages)} open tabs.")

            # Look for active LinkedIn tab or navigate to profile
            target_page = None
            for page in pages:
                if "linkedin.com" in page.url:
                    target_page = page
                    break

            if not target_page:
                print("Opening LinkedIn profile in a new tab...")
                target_page = await context.new_page()
                await target_page.goto("https://www.linkedin.com/in/muhammad-hudaifah-mubarak-a98239279", wait_until="domcontentloaded")

            await target_page.bring_to_front()
            await target_page.wait_for_timeout(3000)

            title = await target_page.title()
            print(f"Active Tab Title: {title}")

            content = await target_page.content()
            profile_data = parse_linkedin_html(content)
            profile_data["url"] = target_page.url

            os.makedirs("build/profile", exist_ok=True)
            with open("build/profile/extracted_linkedin.json", "w", encoding="utf-8") as f:
                json.dump(profile_data, f, indent=2)

            portfolio_path = build_portfolio(profile_data)
            print("\n✔ Successfully extracted profile data from Chrome & rebuilt portfolio:")
            print(json.dumps(profile_data, indent=2))
            print(f"\nPortfolio generated at: {portfolio_path}")
            return profile_data

        except Exception as e:
            print(f"\n✖ Could not connect to Chrome on port 9222: {e}")
            print("\nTo allow your agent to read your open Chrome tabs:")
            print("1. Close Chrome")
            print("2. Launch Chrome with remote debugging enabled:")
            print('   & "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" --remote-debugging-port=9222')
            print("3. Run this script again: .venv\\Scripts\\python.exe tools/extract_via_cdp.py")

if __name__ == "__main__":
    asyncio.run(extract_from_cdp())
