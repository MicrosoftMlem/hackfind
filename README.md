# 🔍 hackfind

A CLI tool that scrapes upcoming hackathons from **Devpost**, **MLH**, **Devfolio**, and **Hackathon.com**, aggregates them, deduplicates, and filters to show only what suits you.

---

## Installation

```bash
git clone https://github.com/you/hackfind.git
cd hackfind
pip install -r requirements.txt
```

---

## Usage

```bash
python main.py [OPTIONS]
```

### Options

| Flag | Short | Description |
|------|-------|-------------|
| `--tags TAG [TAG ...]` | `-t` | Filter by keywords (OR logic). Matches title + tags. |
| `--prize` | `-p` | Only show hackathons that list a cash prize. |
| `--online` | `-o` | Only show online / remote hackathons. |
| `--days N` | `-d` | Only show hackathons starting within N days. |
| `--sources SOURCE [...]` | `-s` | Scrape specific sources only. |
| `--all` | `-a` | Show everything, no filters. |
| `--limit N` | `-l` | Max results to display (default: 50). |
| `--mock` | | Use built-in mock data (no network needed, for testing). |

### Sources

`devpost` `mlh` `devfolio` `hackathons_com`

---

## Examples

```bash
# Find AI + Python hackathons
python main.py --tags ai python

# Blockchain hackathons with a prize, online only
python main.py --tags blockchain web3 --prize --online

# Anything starting in the next 30 days
python main.py --all --days 30

# Only scrape Devpost and Devfolio
python main.py --tags health --sources devpost devfolio

# Test without scraping (uses mock data)
python main.py --mock --tags ai --prize
```

---

## Project Structure

```
hackfind/
├── main.py              # CLI entrypoint
├── aggregator.py        # Merges + deduplicates results from all scrapers
├── filters.py           # Tag/keyword + prize + date filtering logic
├── display.py           # Rich terminal table output
├── mock_data.py         # Sample data for offline testing
├── scrapers/
│   ├── devpost.py       # Scrapes devpost.com/hackathons
│   ├── mlh.py           # Scrapes mlh.io/seasons
│   ├── devfolio.py      # Uses Devfolio's public API
│   └── hackathons_com.py # Scrapes hackathon.com
└── requirements.txt
```

---

## How it works

```
┌─────────────┐  ┌─────────┐  ┌──────────────┐  ┌──────────────┐
│   Devpost   │  │   MLH   │  │   Devfolio   │  │ Hackathon.com│
└──────┬──────┘  └────┬────┘  └──────┬───────┘  └──────┬───────┘
       │              │              │                   │
       └──────────────┴──────────────┴───────────────────┘
                              │
                        aggregator.py
                     (merge + deduplicate)
                              │
                          filters.py
                   (tags / prize / days / online)
                              │
                          display.py
                     (rich terminal table)
```

1. **Scrapers** fetch upcoming hackathons from each source independently
2. **Aggregator** merges all results and deduplicates by normalised title
3. **Filters** narrow down results by your criteria
4. **Display** renders a clean, colour-coded table with `rich`

---

## Notes

- Devpost and Hackathon.com use HTML scraping — may need updates if their layouts change
- Devfolio uses their public search API (more stable)
- MLH scrapes their public events page
- The `--mock` flag is useful for testing filters and display without hitting any network

---

## Requirements

- Python 3.8+
- `requests`
- `beautifulsoup4`
- `rich`
