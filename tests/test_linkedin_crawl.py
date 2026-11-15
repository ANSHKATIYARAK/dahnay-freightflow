import asyncio
from crawl4ai import AsyncWebCrawler

async def main():
    async with AsyncWebCrawler(verbose=False) as c:
        res = await c.arun(url="https://www.linkedin.com/in/muhammad-hudaifah-mubarak-a98239279")
        print("Status:", res.status_code)
        print("Length:", len(res.markdown))
        print("Content Preview:")
        print(res.markdown[:1000])

if __name__ == "__main__":
    asyncio.run(main())
