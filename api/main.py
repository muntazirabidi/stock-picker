"""FastAPI backend for Equity Research frontend."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import universe, company, portfolio, system

app = FastAPI(
    title="Equity Research API",
    description="API for the Equity Research stock analysis system",
    version="1.0.0",
)

# CORS middleware for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(universe.router, prefix="/api/universe", tags=["Universe"])
app.include_router(company.router, prefix="/api/company", tags=["Company"])
app.include_router(portfolio.router, prefix="/api/portfolio", tags=["Portfolio"])
app.include_router(system.router, prefix="/api/system", tags=["System"])


@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
