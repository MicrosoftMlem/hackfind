import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


def scrape(online_only=False):
    hackathons = []
    for season in ["2026", "2025", "2024"]:
        url = f"https://www.mlh.com/seasons/{season}/events"
        try:
            resp = requests.get(url, headers=HEADERS, timeout=10)
            if resp.status_code == 200:
                break
        except Exception as e:
            print(f"[mlh] error fetching {url}: {e}")
            continue
    else:
        return hackathons

    soup = BeautifulSoup(resp.text, "html.parser")
    events = (
        soup.select(".event.feature")
        or soup.select(".event")
        or soup.select("[class*='event-card']")
        or soup.select("[class*='EventCard']")
        or soup.select("article")
    )

    for event in events:
        title_el = event.select_one("h3.event-name") or event.select_one("h3") or event.select_one("[class*='event-title']")
        link_el = event.select_one("a.event-link") or event.select_one("a")
        date_el = event.select_one("p.event-date") or event.select_one(".event-date") or event.select_one("[class*='date']")
        location_el = event.select_one(".event-location") or event.select_one(".location") or event.select_one("[class*='location']")

        title = title_el.get_text(strip=True) if title_el else None
        if not title:
            continue

        href = ""
        if link_el and link_el.has_attr("href"):
            href = link_el["href"]
            if href.startswith("/"):
                href = "https://www.mlh.com" + href

        date_str = date_el.get_text(strip=True) if date_el else ""
        location = location_el.get_text(strip=True) if location_el else ""

        is_online = "online" in location.lower() or "digital" in location.lower() or "virtual" in location.lower()
        if online_only and not is_online:
            continue

        hackathons.append({
            "title": title,
            "url": href,
            "date": date_str,
            "prize": "",
            "tags": _infer_tags(title),
            "location": location or ("Online" if is_online else "In-Person"),
            "source": "MLH",
        })

    return hackathons


def _infer_tags(title: str) -> list:
    keywords = ["ai", "ml", "web", "mobile", "game", "blockchain", "health",
                "fintech", "climate", "data", "security", "iot", "hardware", "open source"]
    lower = title.lower()
    return [kw for kw in keywords if kw in lower]
