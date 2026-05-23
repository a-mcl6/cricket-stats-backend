from app.schemas.api import TeamListItem, TeamPlayerItem
from fastapi import APIRouter, HTTPException
from sqlalchemy import distinct, select

from app.db.models import BattingInnings, BowlingSpell, Player, Team
from app.db.session import SessionLocal

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get("", response_model=list[TeamListItem])
def list_teams() -> list[dict]:
    with SessionLocal() as db:
        teams = db.scalars(
            select(Team).order_by(Team.name)
        ).all()

    return [
        {
            "id": team.id,
            "name": team.name,
        }
        for team in teams
    ]


@router.get("/{team_id}/players", response_model=list[TeamPlayerItem])
def get_team_players(team_id: int) -> list[dict]:
    with SessionLocal() as db:
        team = db.get(Team, team_id)

        if team is None:
            raise HTTPException(status_code=404, detail="Team not found")

        batting_players = db.execute(
            select(
                distinct(Player.id),
                Player.name,
            )
            .join(BattingInnings, BattingInnings.player_id == Player.id)
            .where(BattingInnings.team_id == team_id)
        ).all()

        bowling_players = db.execute(
            select(
                distinct(Player.id),
                Player.name,
            )
            .join(BowlingSpell, BowlingSpell.player_id == Player.id)
            .where(BowlingSpell.team_id == team_id)
        ).all()

    players = {}

    for player_id, player_name in batting_players:
        players[player_id] = {
            "id": player_id,
            "name": player_name,
        }

    for player_id, player_name in bowling_players:
        players[player_id] = {
            "id": player_id,
            "name": player_name,
        }

    return sorted(players.values(), key=lambda p: p["name"])