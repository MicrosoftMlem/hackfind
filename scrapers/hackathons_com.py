import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

URLS_TO_TRY = [
    "https://www.hackathon.com",
    "https://hackathon.com",
]

ONLINE_URLS_TO_TRY = [
    "https://www.hackathon.com/online",
    "https://hackathon.com/online",
    "https://www.hackathon.com",
    "https://hackathon.com",
]


def scrape(online_only=False):
    hackathons = []
    urls = ONLINE_URLS_TO_TRY if online_only else URLS_TO_TRY

    resp = None
    for url in urls:
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code == 200:
                resp = r
                break
        except Exception:
            continue

    if not resp:
        print(f"[hackathon.com] could not reach any URL")
        return hackathons

    soup = BeautifulSoup(resp.text, "html.parser")
    cards = soup.select(".hero__right") or [title_el.parent for title_el in soup.select("a.hero__title")]

    for card in cards:
        title_el = card.select_one("a.hero__title")
        if not title_el:
            continue

        title = title_el.get_text(strip=True)
        href = title_el.get("href", "")
        if href and href.startswith("/"):
            href = "https://www.hackathon.com" + href

        tag_els = card.select(".ht-event-topics__tag")
        tags = [t.get_text(strip=True).lower() for t in tag_els]

        location_el = card.select_one(".hero__key-info__location") or card.select_one("[class*='location']")
        location = location_el.get_text(" ", strip=True) if location_el else ("Online" if online_only else "")

        date_el = card.select_one("[class*='date']")
        date_str = date_el.get_text(" ", strip=True) if date_el else ""

        hackathons.append({
            "title": title,
            "url": href,
            "date": date_str,
            "prize": "",
            "tags": tags,
            "location": location,
            "source": "Hackathon.com",
        })

    return hackathons
