"""
Test Crawl4AI Integration for Autonomous Pain Mining & Web Extraction
"""

import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    print("Testing Crawl4AI AsyncWebCrawler...")
    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(url="https://news.ycombinator.com")
        print("\nCrawl4AI Extraction Result:")
        print(f"Status Code: {result.status_code}")
        print(f"Markdown Length: {len(result.markdown)} characters")
        print("First 200 chars of extracted Markdown:")
        print(result.markdown[:200])

if __name__ == "__main__":
    asyncio.run(main())
