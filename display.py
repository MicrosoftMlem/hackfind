from rich.console import Console
from rich.table import Table
from rich.text import Text
from rich import box

console = Console()


def display(hackathons, tags=None):
    if not hackathons:
        console.print("\n[bold yellow]No hackathons found matching your criteria.[/bold yellow]")
        console.print("Try broader tags or remove filters.\n")
        return

    table = Table(
        box=box.ROUNDED,
        show_header=True,
        header_style="bold cyan",
        expand=True,
        title=f"[bold green] {len(hackathons)} Hackathon(s) Found[/bold green]",
        title_justify="left",
    )

    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Title", min_width=24)
    table.add_column("Source", width=12, style="magenta")
    table.add_column("Date", width=22, style="yellow")
    table.add_column("Location", width=14)
    table.add_column("Prize", width=10, style="green", justify="right")
    table.add_column("Tags", min_width=18, style="dim")
    table.add_column("URL", min_width=28, style="blue")

    for i, h in enumerate(hackathons, 1):
        title = _highlight(h.get("title", ""), tags)
        tag_str = ", ".join(h.get("tags", []))[:40]
        url = h.get("url", "")
        prize = h.get("prize", "") or "—"
        location = h.get("location", "") or "—"
        date = h.get("date", "") or "—"

        table.add_row(
            str(i),
            title,
            h.get("source", ""),
            date,
            location,
            prize,
            tag_str or "—",
            url,
        )

    console.print()
    console.print(table)
    console.print()


def _highlight(text: str, tags=None) -> Text:
    if not tags:
        return Text(text)

    result = Text()
    lower = text.lower()
    i = 0

    while i < len(text):
        matched = False
        for tag in (tags or []):
            tag_lower = tag.lower()
            idx = lower.find(tag_lower, i)
            if idx == i:
                result.append(text[i:i+len(tag)], style="bold white")
                i += len(tag)
                matched = True
                break
        if not matched:
            result.append(text[i])
            i += 1

    return result


def print_summary(total_scraped, total_shown, filters_active):
    parts = []
    if filters_active:
        parts.append(f"[dim]Filters active. {total_scraped} scraped -> [/dim][bold]{total_shown} shown[/bold]")
    else:
        parts.append(f"[bold]{total_shown}[/bold][dim] hackathons aggregated from all sources[/dim]")
    console.print(" ".join(parts))
