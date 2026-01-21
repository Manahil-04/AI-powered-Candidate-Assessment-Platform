from fastapi import FastAPI
from app.core.config import settings
from app.core.logging import setup_logging
from app.api import candidate
from app.api import ws


def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(
        title="AI Candidate Assessment Platform",
        version="0.1.0"
    )

    @app.get("/health")
    def health_check():
        return {"status": "ok"}
    
    app.include_router(candidate.router)
    app.include_router(ws.router)

    return app

app = create_app()
    