"""GET /api/trials/search — Direct ClinicalTrials.gov search."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, Query, HTTPException
from pipeline.retriever import fetch_trials_sync

router = APIRouter(tags=["Trials"])


@router.get("/trials/search")
async def search_trials(
    q: str = Query(..., description="Condition or disease name"),
    max: int = Query(10, ge=1, le=50, description="Max results"),
):
    """Search ClinicalTrials.gov directly (no AI, instant results)."""
    try:
        trials = fetch_trials_sync(q, max_results=max)
        return {"query": q, "total": len(trials), "trials": trials}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
