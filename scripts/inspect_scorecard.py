from pathlib import Path
from pprint import pprint

from app.services.scraping.match_scraper import parse_scorecard_tables


html = Path("tmp_nvplay_page.html").read_text(encoding="utf-8")

scorecard = parse_scorecard_tables(html)

pprint(scorecard)