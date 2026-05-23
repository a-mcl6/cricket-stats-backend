from fastapi import APIRouter, HTTPException
from sqlalchemy import select
from app.schemas.api import MatchListItem, MatchScorecardResponse
from app.db.models import Match
from app.db.session import SessionLocal

from app.db.repositories import get_match_with_scorecard


router = APIRouter(prefix="/matches", tags=["matches"])


@router.get("", response_model=list[MatchListItem])
def list_matches(season: str | None = None) -> list[dict]:
    with SessionLocal() as db:
        query = select(Match)

        if season:
            query = query.where(Match.season == season)

        matches = db.scalars(
            query.order_by(Match.id.desc())
        ).all()

    return [
        {
            "id": match.id,
            "nvplay_match_id": match.nvplay_match_id,
            "competition": match.competition,
            "date": match.date,
            "venue": match.venue,
            "team_1_score": match.team_1_score,
            "team_2_score": match.team_2_score,
            "result": match.result,
        }
        for match in matches
    ]
    
@router.get("/{match_id}", response_model=MatchScorecardResponse)
def get_match(match_id: int) -> dict:
    with SessionLocal() as db:
        match = get_match_with_scorecard(db, match_id)

        if match is None:
            raise HTTPException(status_code=404, detail="Match not found")

    innings_data = []

    for innings_number in [1, 2]:
        batting = [
            innings
            for innings in match.batting_innings
            if innings.innings_number == innings_number
        ]

        bowling = [
            spell
            for spell in match.bowling_spells
            if spell.innings_number == innings_number
        ]

        innings_data.append(
            {
                "innings_number": innings_number,
                "batting": [
                    {
                        "player": entry.player.name,
                        "runs": entry.runs,
                        "balls": entry.balls,
                        "fours": entry.fours,
                        "sixes": entry.sixes,
                        "dismissal": entry.dismissal,
                        "not_out": entry.not_out,
                    }
                    for entry in batting
                ],
                "bowling": [
                    {
                        "player": spell.player.name,
                        "overs": spell.overs,
                        "maidens": spell.maidens,
                        "runs": spell.runs,
                        "wickets": spell.wickets,
                        "economy": spell.economy,
                    }
                    for spell in bowling
                ],
            }
        )

    return {
        "id": match.id,
        "competition": match.competition,
        "date": match.date,
        "venue": match.venue,
        "result": match.result,
        "innings": innings_data,
    }