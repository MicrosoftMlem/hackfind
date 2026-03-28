#!/usr/bin/env python3
import argparse
import sys
from aggregator import aggregate
from filters import apply_filters
from display import display, print_summary, console


SOURCES = ["devpost", "mlh", "devfolio", "hackathons_com"]


def build_parser():
    parser = argparse.ArgumentParser(
        prog="hackfind",
        description="🔍 Find upcoming hackathons that suit you",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --tags ai python
  python main.py --tags blockchain web3 --prize
  python main.py --online --days 30
  python main.py --tags health --sources devpost devfolio
  python main.py --all
        """,
    )

    parser.add_argument(
        "--tags", "-t",
        nargs="+",
        metavar="TAG",
        help="Keywords to filter by (e.g. --tags ai python web3). OR logic.",
    )
    parser.add_argument(
        "--prize", "-p",
        action="store_true",
        help="Only show hackathons that list a prize.",
    )
    parser.add_argument(
        "--online", "-o",
        action="store_true",
        help="Only show online / remote hackathons.",
    )
    parser.add_argument(
        "--days", "-d",
        type=int,
        metavar="N",
        help="Only show hackathons starting within N days.",
    )
    parser.add_argument(
        "--sources", "-s",
        nargs="+",
        choices=SOURCES,
        metavar="SOURCE",
        help=f"Which sources to scrape. Choices: {', '.join(SOURCES)}. Default: all.",
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Show all upcoming hackathons with no filters.",
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=50,
        metavar="N",
        help="Max results to display (default: 50).",
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Use built-in mock data instead of scraping (for testing).",
    )

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    # if no meaningful args, show help
    if not any([args.tags, args.prize, args.online, args.days, args.sources, args.all, args.mock]):
        parser.print_help()
        sys.exit(0)

    console.print(f"\n[bold cyan]hackfind[/bold cyan] [dim]— aggregating hackathons...[/dim]\n")

    # scrape (or use mock data)
    if args.mock:
        from mock_data import MOCK_HACKATHONS
        console.print("  [dim]Using mock data (--mock flag active)[/dim]\n")
        hackathons = MOCK_HACKATHONS
    else:
        hackathons = aggregate(sources=args.sources, online_only=args.online)
    total_scraped = len(hackathons)

    # filter
    filters_active = any([args.tags, args.prize, args.days, args.online])
    hackathons = apply_filters(
        hackathons,
        tags=args.tags,
        prize_only=args.prize,
        days=args.days,
    )

    # limit
    hackathons = hackathons[:args.limit]

    # display
    display(hackathons, tags=args.tags)
    print_summary(total_scraped, len(hackathons), filters_active)


if __name__ == "__main__":
    main()
