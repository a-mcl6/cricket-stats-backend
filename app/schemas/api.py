from pydantic import BaseModel


class PlayerListItem(BaseModel):
    id: int
    name: str


class BattingStats(BaseModel):
    innings: int
    not_outs: int
    runs: int
    balls_faced: int
    fours: int
    sixes: int
    highest_score: int | None
    average: float | None
    strike_rate: float | None

    
class BestBowling(BaseModel):
    wickets: int
    runs: int
    figures: str

class BowlingStats(BaseModel):
    balls_bowled: int
    overs: str
    maidens: int
    runs_conceded: int
    wickets: int
    best_bowling: BestBowling | None
    average: float | None
    economy: float | None
    strike_rate: float | None
    wides: int
    no_balls: int


class PlayerStatsResponse(BaseModel):
    player_id: int
    player_name: str
    batting: BattingStats
    bowling: BowlingStats


class PlayerMatchBatting(BaseModel):
    innings_number: int
    team_id: int
    position: int | None
    runs: int
    balls: int
    fours: int
    sixes: int
    dismissal: str
    not_out: bool


class PlayerMatchBowling(BaseModel):
    team_id: int
    innings_number: int
    overs: str
    balls_bowled: int
    maidens: int
    runs: int
    wickets: int
    economy: float


class PlayerMatchResponse(BaseModel):
    match_id: int
    date: str | None
    competition: str | None
    venue: str | None
    result: str | None
    batting: PlayerMatchBatting | None
    bowling: PlayerMatchBowling | None


class MatchListItem(BaseModel):
    id: int
    nvplay_match_id: str
    competition: str | None
    date: str | None
    venue: str | None
    team_1_score: str | None
    team_2_score: str | None
    result: str | None


class ScorecardBattingEntry(BaseModel):
    player: str
    runs: int
    balls: int
    fours: int
    sixes: int
    dismissal: str
    not_out: bool


class ScorecardBowlingEntry(BaseModel):
    player: str
    overs: str
    maidens: int
    runs: int
    wickets: int
    economy: float


class MatchInningsResponse(BaseModel):
    innings_number: int
    batting: list[ScorecardBattingEntry]
    bowling: list[ScorecardBowlingEntry]


class MatchScorecardResponse(BaseModel):
    id: int
    competition: str | None
    date: str | None
    venue: str | None
    result: str | None
    innings: list[MatchInningsResponse]


class BattingLeaderboardEntry(BaseModel):
    player_id: int
    player_name: str
    innings: int
    not_outs: int
    runs: int
    balls_faced: int
    fours: int
    sixes: int
    highest_score: int | None
    average: float | None
    strike_rate: float | None


class BowlingLeaderboardEntry(BaseModel):
    player_id: int
    player_name: str
    balls_bowled: int
    overs: str
    maidens: int
    runs_conceded: int
    wickets: int
    best_bowling: BestBowling | None
    average: float | None
    economy: float | None
    strike_rate: float | None
    wides: int
    no_balls: int
    
class TeamListItem(BaseModel):
    id: int
    name: str


class TeamPlayerItem(BaseModel):
    id: int
    name: str