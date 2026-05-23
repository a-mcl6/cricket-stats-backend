from fastapi import APIRouter, HTTPException
from sqlalchemy import case, func, select
from app.schemas.api import PlayerListItem, PlayerMatchResponse, PlayerStatsResponse
from app.db.models import BattingInnings, BowlingSpell, Match, Player
from app.db.session import SessionLocal

router = APIRouter(prefix="/players", tags=["players"])


@router.get("", response_model=list[PlayerListItem])
def list_players() -> list[dict]:
    with SessionLocal() as db:
        players = db.scalars(select(Player).order_by(Player.name)).all()

    return [
        {
            "id": player.id,
            "name": player.name,
        }
        for player in players
    ]


@router.get("/{player_id}/stats", response_model=PlayerStatsResponse)
def get_player_stats(
    player_id: int,
    season: str | None = None,
    team_id: int | None = None,
) -> dict:
    with SessionLocal() as db:
        player = db.get(Player, player_id)

        if player is None:
            raise HTTPException(status_code=404, detail="Player not found")
    
        batting_query = (
            select(
                func.count(BattingInnings.id),
                func.sum(BattingInnings.runs),
                func.sum(BattingInnings.balls),
                func.sum(BattingInnings.fours),
                func.sum(BattingInnings.sixes),
                func.sum(case((BattingInnings.not_out == True, 1), else_=0)),
                func.max(BattingInnings.runs),
            )
            .join(Match, BattingInnings.match_id == Match.id)
            .where(BattingInnings.player_id == player_id)
        )

        if season:
            batting_query = batting_query.where(Match.season == season)
            
        if team_id:
            batting_query = batting_query.where(BattingInnings.team_id == team_id)

        batting = db.execute(batting_query).one()

        bowling_query = (
            select(
                func.sum(BowlingSpell.balls_bowled),
                func.sum(BowlingSpell.runs),
                func.sum(BowlingSpell.wickets),
                func.sum(BowlingSpell.maidens),
                func.sum(BowlingSpell.wides),
                func.sum(BowlingSpell.no_balls),
            )
            .join(Match, BowlingSpell.match_id == Match.id)
            .where(BowlingSpell.player_id == player_id)
        )

        if season:
            bowling_query = bowling_query.where(Match.season == season)
        
        if team_id:
            bowling_query = bowling_query.where(BowlingSpell.team_id == team_id)
        
        
        best_bowling_query = (
            select(BowlingSpell)
            .join(Match, BowlingSpell.match_id == Match.id)
            .where(BowlingSpell.player_id == player_id)
        )

        if season:
            best_bowling_query = best_bowling_query.where(Match.season == season)

        if team_id:
            best_bowling_query = best_bowling_query.where(BowlingSpell.team_id == team_id)

        best_bowling_row = db.scalars(
            best_bowling_query.order_by(
                BowlingSpell.wickets.desc(),
                BowlingSpell.runs.asc(),
            )
        ).first()

        bowling = db.execute(bowling_query).one()

    innings = batting[0] or 0
    runs = batting[1] or 0
    balls_faced = batting[2] or 0
    fours = batting[3] or 0
    sixes = batting[4] or 0
    not_outs = batting[5] or 0
    highest_score = batting[6]
    dismissals = innings - not_outs

    balls_bowled = bowling[0] or 0
    runs_conceded = bowling[1] or 0
    wickets = bowling[2] or 0
    maidens = bowling[3] or 0
    wides = bowling[4] or 0
    no_balls = bowling[5] or 0
    best_bowling = (
        {
            "wickets": best_bowling_row.wickets,
            "runs": best_bowling_row.runs,
            "figures": f"{best_bowling_row.wickets}/{best_bowling_row.runs}",
        }
        if best_bowling_row
        else None
    )

    return {
        "player_id": player.id,
        "player_name": player.name,
        "batting": {
            "innings": innings,
            "not_outs": not_outs,
            "runs": runs,
            "balls_faced": balls_faced,
            "fours": fours,
            "sixes": sixes,
            "highest_score": highest_score,
            "average": round(runs / dismissals, 2) if dismissals else None,
            "strike_rate": round((runs / balls_faced) * 100, 2)
            if balls_faced
            else None,
        },
        "bowling": {
            "balls_bowled": balls_bowled,
            "overs": f"{balls_bowled // 6}.{balls_bowled % 6}",
            "maidens": maidens,
            "runs_conceded": runs_conceded,
            "wickets": wickets,
            "best_bowling": best_bowling,
            "average": round(runs_conceded / wickets, 2) if wickets else None,
            "economy": round((runs_conceded / balls_bowled) * 6, 2)
            if balls_bowled
            else None,
            "strike_rate": round(balls_bowled / wickets, 2) if wickets else None,
            "wides": wides,
            "no_balls": no_balls,
        },
    }


@router.get("/{player_id}/matches", response_model=list[PlayerMatchResponse])
def get_player_matches(
    player_id: int,
    season: str | None = None,
    team_id: int | None = None,
) -> list[dict]:
    with SessionLocal() as db:
        player = db.get(Player, player_id)

        if player is None:
            raise HTTPException(status_code=404, detail="Player not found")

        batting_query = (
            select(BattingInnings, Match)
            .join(Match, BattingInnings.match_id == Match.id)
            .where(BattingInnings.player_id == player_id)
        )

        if season:
            batting_query = batting_query.where(Match.season == season)
            
        if team_id:
            batting_query = batting_query.where(BattingInnings.team_id == team_id)

        batting_rows = db.execute(
            batting_query.order_by(Match.id.desc())
        ).all()

        bowling_query = (
            select(BowlingSpell, Match)
            .join(Match, BowlingSpell.match_id == Match.id)
            .where(BowlingSpell.player_id == player_id)
        )

        if season:
            bowling_query = bowling_query.where(Match.season == season)
            
        if team_id:
            bowling_query = bowling_query.where(BowlingSpell.team_id == team_id)

        bowling_rows = db.execute(
            bowling_query.order_by(Match.id.desc())
        ).all()

    matches: dict[int, dict] = {}

    for batting, match in batting_rows:
        matches.setdefault(
            match.id,
            {
                "match_id": match.id,
                "date": match.date,
                "competition": match.competition,
                "venue": match.venue,
                "result": match.result,
                "batting": None,
                "bowling": None,
            },
        )

        matches[match.id]["batting"] = {
            "innings_number": batting.innings_number,
            "position": batting.batting_position,
            "runs": batting.runs,
            "balls": batting.balls,
            "fours": batting.fours,
            "sixes": batting.sixes,
            "dismissal": batting.dismissal,
            "not_out": batting.not_out,
            "team_id": batting.team_id,
        }

    for bowling, match in bowling_rows:
        matches.setdefault(
            match.id,
            {
                "match_id": match.id,
                "date": match.date,
                "competition": match.competition,
                "venue": match.venue,
                "result": match.result,
                "batting": None,
                "bowling": None,
            },
        )

        matches[match.id]["bowling"] = {
            "innings_number": bowling.innings_number,
            "overs": bowling.overs,
            "balls_bowled": bowling.balls_bowled,
            "maidens": bowling.maidens,
            "runs": bowling.runs,
            "wickets": bowling.wickets,
            "economy": bowling.economy,
            "team_id": bowling.team_id,
        }

    return list(matches.values())