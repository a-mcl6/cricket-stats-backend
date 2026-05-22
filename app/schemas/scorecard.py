from pydantic import BaseModel


class BattingEntry(BaseModel):
    player_name: str
    is_captain: bool
    is_wicket_keeper: bool
    dismissal: str
    runs: int
    balls: int
    minutes: int
    fours: int
    sixes: int
    not_out: bool


class BowlingEntry(BaseModel):
    player_name: str
    overs: str
    balls_bowled: int
    maidens: int
    runs: int
    wickets: int
    economy: float
    wides: int
    no_balls: int


class Innings(BaseModel):
    innings_number: int
    batting: list[BattingEntry]
    bowling: list[BowlingEntry]
    
class MatchInfo(BaseModel):
    competition: str | None = None
    status: str | None = None
    match_type: str | None = None
    date: str | None = None
    venue: str | None = None
    team_1: str | None = None
    team_1_score: str | None = None
    team_2: str | None = None
    team_2_score: str | None = None
    result: str | None = None

class Scorecard(BaseModel):
    match: MatchInfo
    innings: list[Innings]
    
