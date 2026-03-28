from scrapers import devpost, mlh, devfolio, hackathons_com


def aggregate(sources=None, online_only=False):
    all_scrapers = {
        "devpost": devpost,
        "mlh": mlh,
        "devfolio": devfolio,
        "hackathons_com": hackathons_com,
    }

    if sources:
        active = {k: v for k, v in all_scrapers.items() if k in sources}
    else:
        active = all_scrapers

    results = []
    for name, scraper in active.items():
        print(f"  Scraping {name}...")
        try:
            items = scraper.scrape(online_only=online_only)
            results.extend(items)
            print(f"    ^ {len(items)} found")
        except Exception as e:
            print(f"    * failed: {e}")

    return _deduplicate(results)


def _deduplicate(hackathons):
    seen = set()
    unique = []
    for h in hackathons:
        key = _normalise(h["title"])
        if key not in seen:
            seen.add(key)
            unique.append(h)
    return unique


def _normalise(title: str) -> str:
    import re
    return re.sub(r"[^a-z0-9]", "", title.lower())
