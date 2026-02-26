"""POST /api/match — Full TrialNav pipeline endpoint with async timeout."""
import sys, os, re, asyncio
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from fastapi import APIRouter, HTTPException
from api.schemas import MatchRequest, MatchResponse
from pipeline import reasoner as from_reasoner
from pipeline.retriever import fetch_trials_sync
from pipeline.exporter import generate_patient_summary, export_fhir_r4
from loguru import logger
from concurrent.futures import ThreadPoolExecutor

router = APIRouter(tags=["Match"])

# Shared thread pool — keeps the event loop unblocked during AI calls
_executor = ThreadPoolExecutor(max_workers=4)


def _detect_search_term(note_lower: str) -> str:
    """Keyword-detect cancer type from clinical note for CT.gov search."""
    if "glioblastoma" in note_lower or " gbm" in note_lower:
        return "glioblastoma"
    if "pancreatic" in note_lower:
        return "pancreatic cancer"
    if "leukemia" in note_lower or " cll" in note_lower or " aml" in note_lower:
        return "leukemia"
    if "lung" in note_lower or "nsclc" in note_lower:
        return "lung cancer"
    if "breast" in note_lower or "tnbc" in note_lower:
        return "breast cancer"
    if "renal" in note_lower or "rcc" in note_lower:
        return "renal cell carcinoma"
    if "colorectal" in note_lower or "colon" in note_lower:
        return "colorectal cancer"
    if "lymphoma" in note_lower:
        return "lymphoma"
    if "melanoma" in note_lower:
        return "melanoma"
    return "cancer"


@router.post("/match", response_model=MatchResponse)
async def match_trials(request: MatchRequest):
    """
    Fast hybrid pipeline:
    1. Detect cancer type → fetch trials from CT.gov (async, non-blocking)
    2. Keyword pre-rank → take top 5 candidates
    3. Try Gemini AI evaluation with a 25s asyncio timeout
    4. If timeout/rate-limit → auto-fall back to instant keyword results
    """
    logger.info("=== MATCH ROUTE STARTED ===")
    logger.info(f"Clinical note length: {len(request.clinical_note)}")
    loop = asyncio.get_event_loop()

    # ── Step 1: Fetch trials (run in thread to not block event loop) ──────────
    note_lower = request.clinical_note.lower()
    search_term = _detect_search_term(note_lower)
    logger.info(f"Detected search term: '{search_term}'")

    try:
        logger.info("Fetching trials...")
        trials = await loop.run_in_executor(
            _executor,
            lambda: fetch_trials_sync(search_term, max_results=max(request.max_trials, 30))
        )
        logger.info(f"Fetched {len(trials)} trials.")
    except Exception as e:
        logger.error(f"Trial fetch error: {e}")
        raise HTTPException(status_code=503, detail=f"Could not fetch trials: {e}")

    if not trials:
        raise HTTPException(status_code=404, detail=f"No recruiting trials found for: {search_term}")

    # ── Step 2: Keyword pre-rank (instant, no AI cost) ────────────────────────
    keywords = set(re.findall(r"\w{4,}", note_lower))
    for t in trials:
        txt = (t.get("title", "") + " " + t.get("eligibility_criteria", "")).lower()
        t["pre_score"] = sum(1 for kw in keywords if kw in txt)

    top5 = sorted(trials, key=lambda x: x.get("pre_score", 0), reverse=True)[:5]

    # ── Step 3: AI evaluation with hard 25s asyncio timeout ──────────────────
    try:
        result = await asyncio.wait_for(
            loop.run_in_executor(
                _executor,
                lambda: from_reasoner.unified_match(request.clinical_note, top5)
            ),
            timeout=25.0
        )
        logger.success("AI evaluation completed.")
    except asyncio.TimeoutError:
        logger.warning("AI evaluation timed out (25s). Using keyword fallback.")
        result = from_reasoner._fallback_results(request.clinical_note, top5)
    except Exception as e:
        logger.warning(f"AI evaluation error: {e}. Using keyword fallback.")
        result = from_reasoner._fallback_results(request.clinical_note, top5)

    profile = result.get("patient_profile", {})
    matched = result.get("matched_trials", [])

    # ── Step 4: Optional patient summary (best-effort, 10s timeout) ──────────
    summary = None
    if request.generate_summary and matched:
        try:
            summary = await asyncio.wait_for(
                loop.run_in_executor(
                    _executor,
                    lambda: generate_patient_summary(profile, matched[:2])
                ),
                timeout=10.0
            )
        except (asyncio.TimeoutError, Exception):
            summary = None   # Non-critical — skip silently

    return MatchResponse(
        patient_profile=profile,
        matched_trials=matched,
        patient_summary=summary,
        fhir_bundle=export_fhir_r4(profile, matched) if request.export_fhir else None,
        total_fetched=len(trials),
        total_matched=len(matched),
    )
