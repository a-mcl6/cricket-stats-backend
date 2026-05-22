from fastapi import APIRouter, HTTPException
from sqlalchemy import Integer, func, select

from app.db.models import BattingInnings, BowlingSpell, Player
from app.db.session import SessionLocal

router = APIRouter(prefix="/players", tags=["players"])


@router.get("")
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
    
@router.get("/{player_id}/stats")
def get_player_stats(player_id: int) -> dict:
    with SessionLocal() as db:
        player = db.get(Player, player_id)

        if player is None:
            raise HTTPException(status_code=404, detail="Player not found")

        batting = db.execute(
            select(
                func.count(BattingInnings.id),
                func.sum(BattingInnings.runs),
                func.sum(BattingInnings.balls),
                func.sum(BattingInnings.fours),
                func.sum(BattingInnings.sixes),
                func.sum(func.cast(BattingInnings.not_out, Integer)),
            ).where(BattingInnings.player_id == player_id)
        ).one()

        bowling = db.execute(
            select(
                func.sum(BowlingSpell.balls_bowled),
                func.sum(BowlingSpell.runs),
                func.sum(BowlingSpell.wickets),
                func.sum(BowlingSpell.maidens),
                func.sum(BowlingSpell.wides),
                func.sum(BowlingSpell.no_balls),
            ).where(BowlingSpell.player_id == player_id)
        ).one()

    innings = batting[0] or 0
    runs = batting[1] or 0
    balls_faced = batting[2] or 0
    fours = batting[3] or 0
    sixes = batting[4] or 0
    not_outs = batting[5] or 0
    dismissals = innings - not_outs

    balls_bowled = bowling[0] or 0
    runs_conceded = bowling[1] or 0
    wickets = bowling[2] or 0
    maidens = bowling[3] or 0
    wides = bowling[4] or 0
    no_balls = bowling[5] or 0

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
            "average": round(runs / dismissals, 2) if dismissals else None,
            "strike_rate": round((runs / balls_faced) * 100, 2) if balls_faced else None,
        },
        "bowling": {
            "balls_bowled": balls_bowled,
            "overs": f"{balls_bowled // 6}.{balls_bowled % 6}",
            "maidens": maidens,
            "runs_conceded": runs_conceded,
            "wickets": wickets,
            "average": round(runs_conceded / wickets, 2) if wickets else None,
            "economy": round((runs_conceded / balls_bowled) * 6, 2) if balls_bowled else None,
            "strike_rate": round(balls_bowled / wickets, 2) if wickets else None,
            "wides": wides,
            "no_balls": no_balls,
        },
    }