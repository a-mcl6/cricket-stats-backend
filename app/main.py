from fastapi import FastAPI

from app.api import leaderboards, matches, players, teams
from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    debug=settings.debug,
)

app.include_router(matches.router)
app.include_router(players.router)
app.include_router(leaderboards.router)
app.include_router(teams.router)


@app.get("/health")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "environment": settings.environment,
    }