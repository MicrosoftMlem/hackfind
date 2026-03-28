import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}


def scrape(online_only=False):
    hackathons = []

    # Devfolio public GraphQL / REST endpoint (confirmed working)
    url = "https://devfolio.co/api/search/hackathons"
    params = {"q": "", "filter": "upcoming", "type": "open"}

    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("results", data.get("hackathons", []))
    except Exception:
        # Fallback: scrape the public listing page
        items = []
        hackathons = _scrape_page(online_only)
        return hackathons

    for item in items:
        is_online = item.get("is_online", True)
        if online_only and not is_online:
            continue

        title = item.get("name", item.get("title", "Unknown"))
        slug = item.get("slug", "")
        url_link = f"https://devfolio.co/hackathons/{slug}" if slug else "https://devfolio.co/hackathons"

        start = (item.get("starts_at", "") or "")[:10]
        end = (item.get("ends_at", "") or "")[:10]
        date_str = f"{start} → {end}" if start and end else start or end

        prize_usd = item.get("prize_pool", 0) or 0
        prize = f"${int(prize_usd):,}" if prize_usd else ""

        tags = [t.lower() for t in (item.get("themes", []) or item.get("tags", []))]
        location = "Online" if is_online else item.get("city", "In-Person")

        hackathons.append({
            "title": title,
            "url": url_link,
            "date": date_str,
            "prize": prize,
            "tags": tags,
            "location": location,
            "source": "Devfolio",
        })

    return hackathons


def _scrape_page(online_only=False):
    """Fallback: scrape devfolio.co/hackathons HTML page."""
    hackathons = []
    url = "https://devfolio.co/hackathons"
    try:
        resp = requests.get(url, headers={**HEADERS, "Accept": "text/html"}, timeout=10)
        resp.raise_for_status()
    except Exception as e:
        print(f"[devfolio] page scrape error: {e}")
        return hackathons

    soup = BeautifulSoup(resp.text, "html.parser")
    cards = soup.select("[class*='HackathonCard']") or soup.select("a[href*='/hackathons/']")

    for card in cards:
        title_el = card.select_one("h2, h3, [class*='title'], [class*='name']")
        title = title_el.get_text(strip=True) if title_el else None
        if not title or title == "Hackathons":
            continue
        href = card.get("href", "")
        if href and not href.startswith("http"):
            href = "https://devfolio.co" + href
        hackathons.append({
            "title": title,
            "url": href,
            "date": "",
            "prize": "",
            "tags": [],
            "location": "Online" if online_only else "",
            "source": "Devfolio",
        })

    return hackathons