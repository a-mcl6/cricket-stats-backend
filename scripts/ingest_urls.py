from pathlib import Path
import sys
from urllib.parse import urlparse

from app.db.session import SessionLocal
from app.services.ingestion.match_ingestor import ingest_scorecard
from app.services.scraping.match_scraper import parse_scorecard_tables
from app.services.scraping.nvplay_client import fetch_page_html


def extract_nvplay_match_id(url: str) -> str:
    fragment = urlparse(url).fragment

    if not fragment:
        raise ValueError("NV Play URL does not contain a match ID fragment")

    return fragment


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("Usage: poetry run python scripts/ingest_urls.py urls.txt")

    file_path = Path(sys.argv[1])

    urls = [
        line.strip()
        for line in file_path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]

    for url in urls:
        try:
            nvplay_match_id = extract_nvplay_match_id(url)

            print(f"\nIngesting {nvplay_match_id}...")

            html = fetch_page_html(url)
            scorecard = parse_scorecard_tables(html)

            with SessionLocal() as db:
                match = ingest_scorecard(db, scorecard, nvplay_match_id)

            print(f"✓ Match {match.id}")
            print(f"  {scorecard.match.team_1} {scorecard.match.team_1_score}")
            print(f"  {scorecard.match.team_2} {scorecard.match.team_2_score}")

        except Exception as exc:
            print(f"✗ Failed for {url}")
            print(f"  {exc}")


if __name__ == "__main__":
    main()