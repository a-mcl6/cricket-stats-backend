import sys
from pathlib import Path

from app.services.scraping.nvplay_client import fetch_page_html


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: poetry run python scripts/test_scrape.py <nvplay_url>")

    url = sys.argv[1]
    html = fetch_page_html(url)

    output_path = Path("tmp_nvplay_page.html")
    output_path.write_text(html, encoding="utf-8")

    print(f"Saved HTML to {output_path}")
    print(f"Length: {len(html):,} characters")


if __name__ == "__main__":
    main()