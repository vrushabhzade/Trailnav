"""GET /api/export/fhir — Export a single trial as FHIR R4 ResearchStudy."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, HTTPException
from pipeline.retriever import fetch_trials_sync
from pipeline.exporter import export_fhir_r4

router = APIRouter(tags=["Export"])


@router.get("/export/fhir/{nct_id}")
async def export_fhir(nct_id: str):
    """Export a single trial as a minimal FHIR R4 ResearchStudy resource."""
    try:
        # Use the NCT ID as condition to get the trial
        trials = fetch_trials_sync(nct_id, max_results=1)
        if not trials:
            raise HTTPException(status_code=404, detail=f"Trial {nct_id} not found.")
        bundle = export_fhir_r4({}, trials)
        return bundle
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
