from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Team(Base):
    __tablename__ = "teams"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)


class Player(Base):
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    nvplay_match_id: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
    )
    competition: Mapped[str | None] = mapped_column(String)
    status: Mapped[str | None] = mapped_column(String)
    match_type: Mapped[str | None] = mapped_column(String)
    date: Mapped[str | None] = mapped_column(String)
    venue: Mapped[str | None] = mapped_column(String)
    team_1_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"))
    team_2_id: Mapped[int | None] = mapped_column(ForeignKey("teams.id"))
    team_1_score: Mapped[str | None] = mapped_column(String)
    team_2_score: Mapped[str | None] = mapped_column(String)
    result: Mapped[str | None] = mapped_column(String)
    batting_innings: Mapped[list["BattingInnings"]] = relationship()
    bowling_spells: Mapped[list["BowlingSpell"]] = relationship()


class BattingInnings(Base):
    __tablename__ = "batting_innings"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)
    innings_number: Mapped[int] = mapped_column(Integer)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)

    batting_position: Mapped[int | None] = mapped_column(Integer)
    dismissal: Mapped[str] = mapped_column(String)
    runs: Mapped[int] = mapped_column(Integer)
    balls: Mapped[int] = mapped_column(Integer)
    minutes: Mapped[int] = mapped_column(Integer)
    fours: Mapped[int] = mapped_column(Integer)
    sixes: Mapped[int] = mapped_column(Integer)
    not_out: Mapped[bool] = mapped_column(Boolean)
    is_captain: Mapped[bool] = mapped_column(Boolean)
    is_wicket_keeper: Mapped[bool] = mapped_column(Boolean)
    player: Mapped["Player"] = relationship()


class BowlingSpell(Base):
    __tablename__ = "bowling_spells"

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id"), index=True)
    innings_number: Mapped[int] = mapped_column(Integer)
    player_id: Mapped[int] = mapped_column(ForeignKey("players.id"), index=True)

    overs: Mapped[str] = mapped_column(String)
    balls_bowled: Mapped[int] = mapped_column(Integer)
    maidens: Mapped[int] = mapped_column(Integer)
    runs: Mapped[int] = mapped_column(Integer)
    wickets: Mapped[int] = mapped_column(Integer)
    economy: Mapped[float]
    wides: Mapped[int] = mapped_column(Integer)
    no_balls: Mapped[int] = mapped_column(Integer)
    player: Mapped["Player"] = relationship()