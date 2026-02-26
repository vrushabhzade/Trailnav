"""
TrialNav FastAPI — main application.
Free-tier: Gemini 2.0 Flash + ClinicalTrials.gov API
"""
import sys
import os

# Allow imports from project root
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import match, trials, export

app = FastAPI(
    title="TrialNav API",
    description=(
        "AI Clinical Trial Matching Navigator — "
        "Free tier: Gemini 2.0 Flash + ClinicalTrials.gov"
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(match.router, prefix="/api")
app.include_router(trials.router, prefix="/api")
app.include_router(export.router, prefix="/api")



@app.get("/health", tags=["Health"])
async def health():
    gemini_key = os.getenv("GEMINI_API_KEY", "")
    use_ollama = os.getenv("USE_OLLAMA", "false").lower() == "true"
    return {
        "status": "ok",
        "ai_backend": "ollama" if use_ollama else ("gemini" if gemini_key else "not_configured"),
        "model": os.getenv("OLLAMA_MODEL", "gemma2:2b") if use_ollama else os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
        "version": "1.0.0",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.main:app", host="0.0.0.0", port=8001, reload=True)