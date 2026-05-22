from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.models import (
    BattingInnings,
    BowlingSpell,
    Match,
    Player,
    Team,
)

def get_match_by_nvplay_id(db: Session, nvplay_match_id: str) -> Match | None:
    return db.scalar(
        select(Match).where(Match.nvplay_match_id == nvplay_match_id)
    )
    
def get_match_with_scorecard(db: Session, match_id: int) -> Match | None:
    return db.scalar(
        select(Match)
        .where(Match.id == match_id)
        .options(
            selectinload(Match.batting_innings).selectinload(BattingInnings.player),
            selectinload(Match.bowling_spells).selectinload(BowlingSpell.player),
        )
    )

def get_or_create_team(db: Session, name: str) -> Team:
    existing = db.scalar(
        select(Team).where(Team.name == name)
    )

    if existing:
        return existing

    team = Team(name=name)

    db.add(team)
    db.flush()

    return team


def get_or_create_player(db: Session, name: str) -> Player:
    existing = db.scalar(
        select(Player).where(Player.name == name)
    )

    if existing:
        return existing

    player = Player(name=name)

    db.add(player)
    db.flush()

    return player