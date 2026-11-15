import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        # Try launching installed Google Chrome
        browser = await p.chromium.launch(headless=True, channel="chrome")
        page = await browser.new_page()
        await page.goto("https://www.linkedin.com/in/muhammad-hudaifah-mubarak-a98239279", timeout=15000)
        title = await page.title()
        print("Page Title:", title)
        content = await page.content()
        print("Content length:", len(content))
        if "authwall" in page.url or "Sign In" in title:
            print("Blocked by AuthWall. URL:", page.url)
        else:
            print("Successfully loaded profile!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
