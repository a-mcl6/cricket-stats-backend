import sys

from app.db.session import SessionLocal
from app.services.ingestion.match_ingestor import ingest_scorecard
from app.services.scraping.match_scraper import parse_scorecard_tables
from app.services.scraping.nvplay_client import fetch_page_html

from urllib.parse import urlparse

def extract_nvplay_match_id(url: str) -> str:

    fragment = urlparse(url).fragment

    if not fragment:

        raise ValueError("NV Play URL does not contain a match ID fragment")

    return fragment

def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("Usage: poetry run python scripts/ingest_scorecard.py <nvplay_url>")

    url = sys.argv[1]

    html = fetch_page_html(url)
    scorecard = parse_scorecard_tables(html)

    with SessionLocal() as db:
        nvplay_match_id = extract_nvplay_match_id(url)
        match = ingest_scorecard(db, scorecard, nvplay_match_id)

    print(f"Ingested match ID: {match.id}")
    print(f"{scorecard.match.team_1} {scorecard.match.team_1_score}")
    print(f"{scorecard.match.team_2} {scorecard.match.team_2_score}")


if __name__ == "__main__":
    main()