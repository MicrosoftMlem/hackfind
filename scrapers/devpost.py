import re
import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
}
API_URL = "https://devpost.com/api/hackathons"


def scrape(online_only=False):
    hackathons = []
    page = 1

    while True:
        params = {
            "status[]": "upcoming",
            "page": page,
            "per_page": 40,
        }

        try:
            resp = requests.get(API_URL, headers=HEADERS, params=params, timeout=10)
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            print(f"[devpost] error on page {page}: {e}")
            break

        items = data.get("hackathons", [])
        if not items:
            break

        for item in items:
            title = item.get("title", "Unknown")
            url_link = item.get("url", "")
            date_str = (item.get("submission_period_dates") or "").strip()
            prize = _clean_prize(item.get("prize_amount", ""))

            themes = item.get("themes", []) or []
            tags = [t.get("name", "").lower() for t in themes if isinstance(t, dict)]

            location = item.get("displayed_location", {})
            if isinstance(location, dict):
                location_str = location.get("location", "Online") or "Online"
            else:
                location_str = str(location) if location else "Online"

            if online_only and "online" not in location_str.lower():
                continue

            hackathons.append({
                "title": title,
                "url": url_link,
                "date": date_str,
                "prize": prize,
                "tags": tags,
                "location": location_str,
                "source": "Devpost",
            })

        total = data.get("meta", {}).get("total_count", 0)
        if total <= 0 or len(hackathons) >= total:
            break
        page += 1

    return hackathons


def _clean_prize(raw):
    if not raw:
        return ""
    clean = re.sub(r"<[^>]+>", "", str(raw)).strip()
    return clean
