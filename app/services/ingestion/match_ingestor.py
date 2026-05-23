from datetime import date

from sqlalchemy.orm import Session

from app.db.models import BattingInnings, BowlingSpell, Match
from app.db.repositories import (
    get_or_create_player,
    get_or_create_team,
    get_match_by_nvplay_id,
)
from app.schemas.scorecard import Scorecard


def ingest_scorecard(db: Session, scorecard: Scorecard, nvplay_match_id: str) -> Match:
    existing_match = get_match_by_nvplay_id(db, nvplay_match_id)

    if existing_match:
        return existing_match
    team_1 = get_or_create_team(db, scorecard.match.team_1)
    team_2 = get_or_create_team(db, scorecard.match.team_2)

    match = Match(
        nvplay_match_id=nvplay_match_id,
        competition=scorecard.match.competition,
        status=scorecard.match.status,
        match_type=scorecard.match.match_type,
        date=scorecard.match.date,
        venue=scorecard.match.venue,
        team_1_id=team_1.id,
        team_2_id=team_2.id,
        team_1_score=scorecard.match.team_1_score,
        team_2_score=scorecard.match.team_2_score,
        result=scorecard.match.result,
        season=scorecard.match.date.split()[-1],
    )

    db.add(match)
    db.flush()

    for innings in scorecard.innings:
        if innings.innings_number == 1:
            batting_team = team_1
            bowling_team = team_2
        else:
            batting_team = team_2
            bowling_team = team_1
        for position, batter in enumerate(innings.batting, start=1):
            player = get_or_create_player(db, batter.player_name)

            batting = BattingInnings(
                match_id=match.id,
                innings_number=innings.innings_number,
                player_id=player.id,
                batting_position=position,
                dismissal=batter.dismissal,
                runs=batter.runs,
                balls=batter.balls,
                minutes=batter.minutes,
                fours=batter.fours,
                sixes=batter.sixes,
                not_out=batter.not_out,
                is_captain=batter.is_captain,
                is_wicket_keeper=batter.is_wicket_keeper,
                team_id=batting_team.id,
            )

            db.add(batting)

        for bowler in innings.bowling:
            player = get_or_create_player(db, bowler.player_name)

            spell = BowlingSpell(
                match_id=match.id,
                innings_number=innings.innings_number,
                player_id=player.id,
                overs=bowler.overs,
                balls_bowled=bowler.balls_bowled,
                maidens=bowler.maidens,
                runs=bowler.runs,
                wickets=bowler.wickets,
                economy=bowler.economy,
                wides=bowler.wides,
                no_balls=bowler.no_balls,
                team_id=bowling_team.id,
            )

            db.add(spell)

    db.commit()

    return match