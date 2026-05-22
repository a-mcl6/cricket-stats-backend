from bs4 import BeautifulSoup

from app.schemas.scorecard import (
    BattingEntry,
    BowlingEntry,
    Innings,
    Scorecard,
    MatchInfo
)


def row_values(row) -> list[str]:
    return [" ".join(value.split()) for value in row.stripped_strings]


def is_batting_row(row: list[str]) -> bool:
    return (
        len(row) >= 7
        and row[0] not in {"Extras", "Total"}
    )


def is_bowling_row(row: list[str]) -> bool:
    return len(row) == 8

def clean_player_name(raw_name: str) -> tuple[str, bool, bool]:
    is_captain = "*" in raw_name
    is_wicket_keeper = "†" in raw_name

    name = raw_name.replace("*", "").replace("†", "")
    name = " ".join(name.split())

    return name, is_captain, is_wicket_keeper


def overs_to_balls(overs: str) -> int:
    if "." not in overs:
        return int(overs) * 6

    whole_overs, balls = overs.split(".", maxsplit=1)
    return int(whole_overs) * 6 + int(balls)


def parse_match_info(soup: BeautifulSoup) -> MatchInfo:
    teams = soup.select(".nvp-scorecard__team_pill")

    team_1 = teams[0].select_one("span:nth-of-type(2)") if len(teams) > 0 else None
    team_2 = teams[1].select_one("span:nth-of-type(2)") if len(teams) > 1 else None

    team_1_score = teams[0].select_one(".nvp-scorecard__match-score span") if len(teams) > 0 else None
    team_2_score = teams[1].select_one(".nvp-scorecard__match-score span") if len(teams) > 1 else None

    result = soup.select_one(".nvp-scorecard__match-result span")

    return MatchInfo(
        competition=get_text(soup.select_one(".nvp-scorecard__match_title span")),
        status=get_text(soup.select_one(".nvp-match_status")),
        match_type=get_text(soup.select_one(".nvp-scorecard__match-type")),
        date=get_text(soup.select_one(".nvp-scorecard__match-date")),
        venue=get_text(soup.select_one(".nvp-scorecard__match-venue")),
        team_1=get_text(team_1),
        team_1_score=get_text(team_1_score),
        team_2=get_text(team_2),
        team_2_score=get_text(team_2_score),
        result=get_text(result),
    )


def get_text(element) -> str | None:
    if element is None:
        return None

    text = " ".join(element.get_text(" ", strip=True).split())
    return text.replace(" ,", ",")

def parse_scorecard_tables(html: str) -> Scorecard:
    soup = BeautifulSoup(html, "lxml")
    tables = soup.select(".nvp-scorecard__table")

    batting_table_indexes = [5, 12]
    bowling_table_indexes = [6, 13]

    innings_data = []

    for innings_number, (batting_index, bowling_index) in enumerate(
        zip(batting_table_indexes, bowling_table_indexes),
        start=1,
    ):
        batting_entries = []
        bowling_entries = []

        batting_rows = [
            row_values(row)
            for row in tables[batting_index].select(".nvp-scorecard__table-row")
        ]

        for row in batting_rows:
            if not is_batting_row(row):
                continue
            
            player_name, is_captain, is_wicket_keeper = clean_player_name(row[0])

            batting_entries.append(
                BattingEntry(
                    player_name=player_name,
                    is_captain=is_captain,
                    is_wicket_keeper=is_wicket_keeper,
                    dismissal=row[1],
                    runs=int(row[2]),
                    balls=int(row[3]),
                    minutes=int(row[4]),
                    fours=int(row[5]),
                    sixes=int(row[6]),
                    not_out=row[1].lower() == "not out",
                )
            )

        bowling_rows = [
            row_values(row)
            for row in tables[bowling_index].select(".nvp-scorecard__table-row")
        ]

        for row in bowling_rows:
            if not is_bowling_row(row):
                continue

            bowling_entries.append(
                BowlingEntry(
                    player_name=clean_player_name(row[0])[0],
                    overs=row[1],
                    balls_bowled=overs_to_balls(row[1]),
                    maidens=int(row[2]),
                    runs=int(row[3]),
                    wickets=int(row[4]),
                    economy=float(row[5]),
                    wides=int(row[6]),
                    no_balls=int(row[7]),
                )
            )

        innings_data.append(
            Innings(
                innings_number=innings_number,
                batting=batting_entries,
                bowling=bowling_entries,
            )
        )

    return Scorecard(match=parse_match_info(soup), innings=innings_data)