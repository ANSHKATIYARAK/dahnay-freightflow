import requests

url = "https://www.linkedin.com/in/muhammad-hudaifah-mubarak-a98239279"

# Test 1: Googlebot header
headers_googlebot = {
    "User-Agent": "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

# Test 2: Bingbot header
headers_bingbot = {
    "User-Agent": "Mozilla/5.0 (compatible; bingbot/2.0; +http://www.bing.com/bingbot.htm)",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
}

# Test 3: Standard Mobile Safari
headers_mobile = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Accept-Language": "en-US,en;q=0.9"
}

for name, h in [("Googlebot", headers_googlebot), ("Bingbot", headers_bingbot), ("MobileSafari", headers_mobile)]:
    try:
        r = requests.get(url, headers=h, timeout=10)
        print(f"[{name}] Status: {r.status_code}, Length: {len(r.text)}, Title in text: {'<title>' in r.text}")
        if r.status_code == 200:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(r.text, "html.parser")
            print(f"[{name}] Title:", soup.title.string if soup.title else "No title")
            # print meta description
            desc = soup.find("meta", {"name": "description"})
            if desc:
                print(f"[{name}] Meta Desc:", desc.get("content"))
            # print og:title, og:description
            og_title = soup.find("meta", {"property": "og:title"})
            if og_title:
                print(f"[{name}] OG Title:", og_title.get("content"))
            og_desc = soup.find("meta", {"property": "og:description"})
            if og_desc:
                print(f"[{name}] OG Desc:", og_desc.get("content"))
    except Exception as e:
        print(f"[{name}] Error: {e}")
