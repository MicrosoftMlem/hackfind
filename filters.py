def apply_filters(hackathons, tags=None, prize_only=False, days=None, exclude_past=True):
    results = hackathons

    if exclude_past:
        results = _filter_out_past(results)

    if tags:
        results = _filter_by_tags(results, tags)

    if prize_only:
        results = [h for h in results if h.get("prize")]

    if days is not None:
        results = _filter_by_days(results, days)

    return results


def _filter_out_past(hackathons):
    from datetime import datetime

    today = datetime.now().date()
    results = []

    for h in hackathons:
        date_str = h.get("date", "")
        end_date = _try_parse_end_date(date_str)

        if end_date is None:
            results.append(h)
            continue

        if isinstance(end_date, datetime):
            end_date = end_date.date()

        if end_date >= today:
            results.append(h)

    return results


def _try_parse_end_date(date_str: str):
    if not date_str:
        return None

    date_str = date_str.strip()

    # handle explicit range separators first
    import re
    parts = [p.strip() for p in re.split(r"\s*→\s*|\s*–\s*|\s*—\s*|\s+-\s+", date_str) if p.strip()]
    if len(parts) > 1:
        candidate = _try_parse_date(parts[-1])
        if candidate:
            return candidate

        candidate = _try_parse_date(_expand_date_range(parts[0], parts[-1]))
        if candidate:
            return candidate

    return _try_parse_date(date_str)


def _expand_date_range(start: str, end: str) -> str:
    import re

    if re.search(r"[A-Za-z]{3,}|\d{4}-\d{2}-\d{2}", end):
        return end

    month_match = re.search(r"([A-Za-z]+)\s+\d{1,2}", start)
    year_match = re.search(r"(\d{4})", end) or re.search(r"(\d{4})", start)
    day_match = re.search(r"(\d{1,2})", end)

    if month_match and day_match:
        month = month_match.group(1)
        year = year_match.group(1) if year_match else str(__import__("datetime").datetime.now().year)
        return f"{month} {day_match.group(1)}, {year}"

    return end


def _filter_by_tags(hackathons, tags):
    matched = []
    normalised_tags = [t.lower() for t in tags]

    for h in hackathons:
        searchable = " ".join([
            h.get("title", ""),
            " ".join(h.get("tags", [])),
            h.get("location", ""),
        ]).lower()

        if any(tag in searchable for tag in normalised_tags):
            matched.append(h)

    return matched


def _filter_by_days(hackathons, days):
    from datetime import datetime, timedelta
    import re

    cutoff = datetime.now() + timedelta(days=days)
    results = []

    for h in hackathons:
        date_str = h.get("date", "")
        parsed = _try_parse_date(date_str)
        if parsed is None:
            # can't parse date — include anyway (don't silently drop)
            results.append(h)
        elif parsed <= cutoff:
            results.append(h)

    return results


def _try_parse_date(date_str: str, default_year=None):
    from datetime import datetime
    import re

    if not date_str:
        return None

    s = date_str.strip()
    s = re.sub(r"[–—→]", "-", s)
    s = re.sub(r"(\d+)(st|nd|rd|th)", r"\1", s, flags=re.I)

    if re.search(r"\d{4}-\d{2}-\d{2}", s):
        try:
            return datetime.strptime(re.search(r"(\d{4}-\d{2}-\d{2})", s).group(1), "%Y-%m-%d")
        except ValueError:
            pass

    # standard date formats with year
    for fmt in ("%b %d, %Y", "%B %d, %Y", "%b %d %Y", "%B %d %Y", "%d %b %Y", "%d %B %Y"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass

    # if year missing, try with default year or current year
    if not re.search(r"\d{4}", s):
        year = default_year or datetime.now().year
        for fmt in ("%b %d", "%B %d", "%d %b", "%d %B"):
            try:
                return datetime.strptime(f"{s} {year}", fmt + " %Y")
            except ValueError:
                pass

    return None


def _try_parse_end_date(date_str: str):
    import re

    if not date_str:
        return None

    s = date_str.strip()
    starts_ends = re.search(r"starts\s+(.+?)\s+ends\s+(.+)", s, flags=re.I)
    if starts_ends:
        start_part = starts_ends.group(1).strip()
        end_part = starts_ends.group(2).strip()

        start_year = None
        if re.search(r"\d{4}", start_part):
            start_year = re.search(r"(\d{4})", start_part).group(1)

        parsed = _try_parse_date(end_part, default_year=start_year)
        if parsed:
            return parsed

    # handle explicit range separators
    parts = [p.strip() for p in re.split(r"\s*→\s*|\s*-\s*|\s*–\s*|\s*—\s*", s) if p.strip()]
    if len(parts) > 1:
        candidate = _try_parse_date(parts[-1])
        if candidate:
            return candidate

        candidate = _try_parse_date(_expand_date_range(parts[0], parts[-1]))
        if candidate:
            return candidate

    return _try_parse_date(s)


def _expand_date_range(start: str, end: str) -> str:
    import re

    if re.search(r"[A-Za-z]{3,}|\d{4}-\d{2}-\d{2}", end):
        return end

    month_match = re.search(r"([A-Za-z]+)\s+\d{1,2}", start)
    year_match = re.search(r"(\d{4})", end) or re.search(r"(\d{4})", start)
    day_match = re.search(r"(\d{1,2})", end)

    if month_match and day_match:
        month = month_match.group(1)
        year = year_match.group(1) if year_match else str(__import__("datetime").datetime.now().year)
        return f"{month} {day_match.group(1)}, {year}"

    return end
