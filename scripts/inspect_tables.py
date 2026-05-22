from pathlib import Path

from bs4 import BeautifulSoup


html = Path("tmp_nvplay_page.html").read_text(encoding="utf-8")
soup = BeautifulSoup(html, "lxml")

tables = soup.select(".nvp-scorecard__table")

print(f"Tables found: {len(tables)}")

for table_index, table in enumerate(tables, start=1):
    rows = table.select(".nvp-scorecard__table-row")
    print(f"\nTABLE {table_index} - rows: {len(rows)}")

    for row_index, row in enumerate(rows[:20], start=1):
        text = " | ".join(row.stripped_strings)
        print(f"{row_index}: {text}")