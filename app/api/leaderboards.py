from fastapi import APIRouter
from sqlalchemy import case, func, select

from app.db.models import BattingInnings, BowlingSpell, Match, Player
from app.schemas.api import BattingLeaderboardEntry, BowlingLeaderboardEntry
from app.db.session import SessionLocal

router = APIRouter(prefix="/leaderboards", tags=["leaderboards"])


@router.get("/batting", response_model=list[BattingLeaderboardEntry])
def batting_leaderboard(
    season: str | None = None,
    team_id: int | None = None,
    min_innings: int = 1,
    sort_by: str = "runs",
) -> list[dict]:
    with SessionLocal() as db:
        query = (
            select(
                Player.id.label("player_id"),
                Player.name.label("player_name"),
                func.count(BattingInnings.id).label("innings"),
                func.sum(BattingInnings.runs).label("runs"),
                func.sum(BattingInnings.balls).label("balls"),
                func.sum(BattingInnings.fours).label("fours"),
                func.sum(BattingInnings.sixes).label("sixes"),
                func.sum(case((BattingInnings.not_out == True, 1), else_=0)).label(
                    "not_outs"
                ),
                func.max(BattingInnings.runs).label("highest_score"),
            )
            .join(BattingInnings, BattingInnings.player_id == Player.id)
            .join(Match, BattingInnings.match_id == Match.id)
            .group_by(Player.id, Player.name)
        )

        if season:
            query = query.where(Match.season == season)

        if team_id:
            query = query.where(BattingInnings.team_id == team_id)

        rows = db.execute(query).all()

    leaderboard = []

    for row in rows:
        dismissals = row.innings - row.not_outs
        average = round(row.runs / dismissals, 2) if dismissals else None
        strike_rate = round((row.runs / row.balls) * 100, 2) if row.balls else None

        if row.innings < min_innings:
            continue

        leaderboard.append(
            {
                "player_id": row.player_id,
                "player_name": row.player_name,
                "innings": row.innings,
                "not_outs": row.not_outs,
                "runs": row.runs,
                "balls_faced": row.balls,
                "fours": row.fours,
                "sixes": row.sixes,
                "highest_score": row.highest_score,
                "average": average,
                "strike_rate": strike_rate,
            }
        )

    sort_keys = {
        "runs": lambda item: item["runs"],
        "average": lambda item: item["average"] if item["average"] is not None else -1,
        "strike_rate": lambda item: item["strike_rate"] if item["strike_rate"] is not None else -1,
        "highest_score": lambda item: item["highest_score"] if item["highest_score"] is not None else -1,
    }

    sort_key = sort_keys.get(sort_by, sort_keys["runs"])

    return sorted(leaderboard, key=sort_key, reverse=True)

@router.get("/bowling", response_model=list[BowlingLeaderboardEntry])
def bowling_leaderboard(
    season: str | None = None,
    team_id: int | None = None,
    min_wickets: int = 1,
    sort_by: str = "wickets",
) -> list[dict]:
    with SessionLocal() as db:
        query = (
            select(
                Player.id.label("player_id"),
                Player.name.label("player_name"),
                func.sum(BowlingSpell.balls_bowled).label("balls_bowled"),
                func.sum(BowlingSpell.maidens).label("maidens"),
                func.sum(BowlingSpell.runs).label("runs_conceded"),
                func.sum(BowlingSpell.wickets).label("wickets"),
                func.sum(BowlingSpell.wides).label("wides"),
                func.sum(BowlingSpell.no_balls).label("no_balls"),
            )
            .join(BowlingSpell, BowlingSpell.player_id == Player.id)
            .join(Match, BowlingSpell.match_id == Match.id)
            .group_by(Player.id, Player.name)
        )

        if season:
            query = query.where(Match.season == season)

        if team_id:
            query = query.where(BowlingSpell.team_id == team_id)

        rows = db.execute(query).all()

        best_query = (
            select(
                BowlingSpell.player_id,
                BowlingSpell.wickets,
                BowlingSpell.runs,
            )
            .join(Match, BowlingSpell.match_id == Match.id)
        )

        if season:
            best_query = best_query.where(Match.season == season)

        if team_id:
            best_query = best_query.where(BowlingSpell.team_id == team_id)

        best_rows = db.execute(
            best_query.order_by(
                BowlingSpell.player_id,
                BowlingSpell.wickets.desc(),
                BowlingSpell.runs.asc(),
            )
        ).all()

    best_by_player = {}

    for row in best_rows:
        if row.player_id not in best_by_player:
            best_by_player[row.player_id] = {
                "wickets": row.wickets,
                "runs": row.runs,
                "figures": f"{row.wickets}/{row.runs}",
            }

    leaderboard = []

    for row in rows:
        if row.wickets < min_wickets:
            continue

        average = (
            round(row.runs_conceded / row.wickets, 2)
            if row.wickets
            else None
        )
        economy = (
            round((row.runs_conceded / row.balls_bowled) * 6, 2)
            if row.balls_bowled
            else None
        )
        strike_rate = (
            round(row.balls_bowled / row.wickets, 2)
            if row.wickets
            else None
        )

        leaderboard.append(
            {
                "player_id": row.player_id,
                "player_name": row.player_name,
                "balls_bowled": row.balls_bowled,
                "overs": f"{row.balls_bowled // 6}.{row.balls_bowled % 6}",
                "maidens": row.maidens,
                "runs_conceded": row.runs_conceded,
                "wickets": row.wickets,
                "best_bowling": best_by_player.get(row.player_id),
                "average": average,
                "economy": economy,
                "strike_rate": strike_rate,
                "wides": row.wides,
                "no_balls": row.no_balls,
            }
        )

        sort_keys = {
        "wickets": lambda item: item["wickets"],
        "average": lambda item: item["average"] if item["average"] is not None else float("inf"),
        "economy": lambda item: item["economy"] if item["economy"] is not None else float("inf"),
        "strike_rate": lambda item: item["strike_rate"] if item["strike_rate"] is not None else float("inf"),
    }

    sort_key = sort_keys.get(sort_by, sort_keys["wickets"])
    reverse = sort_by == "wickets"

    return sorted(leaderboard, key=sort_key, reverse=reverse)