"""
Step 3 — Eligibility reasoning with a hard 15s timeout + keyword fallback.
Strategy:
  1. Try the Gemini unified-match call with a 15-second thread timeout.
  2. If it fails or times out → return keyword-scored results instantly (< 1s).
This prevents the 60-second Gemini retry delays from blocking the user.
"""
import json
import re
import time
import threading
from typing import List, Dict, Optional
from loguru import logger
from models import model_router

# ── Compact prompt — short eligibility snippets only ─────────────────────────
UNIFIED_MATCH_PROMPT = """You are a clinical trial eligibility expert.
Extract patient profile and score each trial.

PATIENT NOTE: {clinical_note}

TRIALS:
{trials_block}

Return ONLY compact JSON:
{{"patient_profile":{{"diagnosis":"...","histology":"...","biomarkers":[],"ecog":"...","age":"...","sex":"..."}},"evaluations":[{{"nct_id":"...","overall_verdict":"ELIGIBLE|LIKELY_ELIGIBLE|BORDERLINE|INELIGIBLE","match_score":0-100,"reasoning_steps":[{{"criterion":"...","verdict":"MET|NOT_MET|BORDERLINE","explanation":"..."}}]}}]}}"""


def _format_trials_block(trials: List[Dict]) -> str:
    """Format trials — dramatically shorter eligibility snippets to save tokens."""
    parts = []
    for i, t in enumerate(trials, 1):
        # Only take the first 400 chars of eligibility criteria — biggest token saver
        crit = t.get("eligibility_criteria", "")[:400]
        parts.append(
            f"[{i}] NCT:{t.get('nct_id','')} Phase:{t.get('phase','?')}\n"
            f"Title:{t.get('title','')[:100]}\n"
            f"Criteria:{crit}"
        )
    return "\n---\n".join(parts)


def _keyword_score(clinical_note: str, trial: dict) -> int:
    """Fast local keyword scoring — runs in microseconds, no AI cost."""
    note_lower = clinical_note.lower()
    text = (
        trial.get("title", "") + " " +
        trial.get("eligibility_criteria", "") + " " +
        trial.get("summary", "")
    ).lower()

    # Extract meaningful words from the note (4+ chars)
    keywords = set(re.findall(r"\b\w{4,}\b", note_lower))

    # Count how many note keywords appear in the trial text
    overlap = sum(1 for kw in keywords if kw in text)

    # Normalize to a 0-100 score
    max_possible = max(len(keywords), 1)
    return min(int((overlap / max_possible) * 200), 85)  # cap at 85 to distinguish from AI


def _extract_profile_keywords(clinical_note: str) -> dict:
    """Fast regex-based profile extraction — no AI needed."""
    note_lower = clinical_note.lower()
    
    # Age
    age_match = re.search(r"(\d{2})[- ]?year", note_lower)
    age = age_match.group(1) if age_match else "unknown"
    
    # Sex
    sex = "male" if " male" in note_lower else ("female" if "female" in note_lower else "unknown")
    
    # ECOG
    ecog_match = re.search(r"ecog[^0-9]*([0-4])", note_lower)
    ecog = ecog_match.group(1) if ecog_match else "unknown"

    # Diagnosis — look for common cancer terms
    diagnosis = "cancer"
    for term in ["glioblastoma", "gbm", "nsclc", "non-small cell lung", "breast cancer",
                 "leukemia", "cll", "aml", "lymphoma", "pancreatic", "renal cell",
                 "colorectal", "melanoma", "prostate", "ovarian"]:
        if term in note_lower:
            diagnosis = term
            break

    return {
        "diagnosis": diagnosis,
        "age": age,
        "sex": sex,
        "ecog": ecog,
        "biomarkers": re.findall(r"\b(EGFR|ALK|ROS1|KRAS|BRAF|BRCA[12]?|HER2|PD-L1|MSI|FLT3|IDH[12]?|MGMT|TP53|MET|RET|NTRK)\b", clinical_note, re.I),
        "histology": "unknown"
    }


def _fallback_results(clinical_note: str, trials: List[dict]) -> dict:
    """Return instantly-scored keyword results when AI is unavailable."""
    logger.info("Using fast keyword fallback (AI unavailable/timed out).")
    profile = _extract_profile_keywords(clinical_note)
    
    results = []
    for t in trials:
        score = _keyword_score(clinical_note, t)
        verdict = (
            "LIKELY_ELIGIBLE" if score >= 60
            else "BORDERLINE" if score >= 35
            else "INELIGIBLE"
        )
        results.append({
            "nct_id": t.get("nct_id", ""),
            "title": t.get("title", ""),
            "phase": t.get("phase", ""),
            "sponsor": t.get("sponsor", ""),
            "url": t.get("url", ""),
            "summary": t.get("summary", ""),
            "overall_verdict": verdict,
            "match_score": score,
            "reasoning_steps": [{"criterion": "Keyword overlap analysis", "verdict": "MET" if score >= 50 else "BORDERLINE", "explanation": f"Matched {score}% of patient terms in trial criteria (fast keyword scan)."}],
            "ai_scored": False,
        })
    
    ranked = sorted(results, key=lambda x: x["match_score"], reverse=True)
    return {"patient_profile": profile, "matched_trials": ranked}


def unified_match(clinical_note: str, trials: List[dict], timeout_secs: int = 20) -> dict:
    """
    Unified extraction + evaluation with a hard timeout.
    
    - Tries AI evaluation for up to `timeout_secs` seconds.
    - If Gemini is rate-limited or times out → returns keyword fallback instantly.
    """
    if not trials:
        return {"patient_profile": {}, "matched_trials": []}

    logger.info(f"Unified match: {len(trials)} trials, {timeout_secs}s timeout.")
    
    result_container: List[Optional[dict]] = [None]
    error_container: List[Optional[Exception]] = [None]

    def _run_ai():
        try:
            trials_block = _format_trials_block(trials)
            prompt = UNIFIED_MATCH_PROMPT.format(
                clinical_note=clinical_note,
                num_trials=len(trials),
                trials_block=trials_block,
            )
            logger.debug(f"Prompt size: {len(prompt)} chars")
            response = model_router.generate(prompt, temperature=0.1)

            # Parse JSON from response
            m = re.search(r"\{.*\}", response, re.DOTALL)
            raw = json.loads(m.group() if m else response)

            profile = raw.get("patient_profile", {})
            evals = raw.get("evaluations", [])

            trial_map = {t["nct_id"]: t for t in trials}
            merged = []
            for item in evals:
                nct = item.get("nct_id", "")
                meta = trial_map.get(nct, {})
                item.update({
                    "title": meta.get("title", ""),
                    "phase": meta.get("phase", ""),
                    "sponsor": meta.get("sponsor", ""),
                    "url": meta.get("url", ""),
                    "summary": meta.get("summary", ""),
                    "ai_scored": True,
                })
                merged.append(item)

            ranked = sorted(merged, key=lambda x: x.get("match_score", 0), reverse=True)
            result_container[0] = {"patient_profile": profile, "matched_trials": ranked}

        except Exception as e:
            logger.warning(f"AI call failed: {e}")
            error_container[0] = e

    # Run AI in a background thread with a hard timeout
    t = threading.Thread(target=_run_ai, daemon=True)
    t.start()
    t.join(timeout=timeout_secs)

    if result_container[0] is not None:
        logger.success("AI match completed within timeout.")
        return result_container[0]
    
    # Timed out or errored — use instant fallback
    if t.is_alive():
        logger.warning(f"AI timed out after {timeout_secs}s — using keyword fallback.")
    else:
        logger.warning("AI failed — using keyword fallback.")
    
    return _fallback_results(clinical_note, trials)


def _make_fallback(t: dict) -> dict:
    """Create a minimal result dict."""
    return {
        "nct_id": t.get("nct_id", ""),
        "title": t.get("title", ""),
        "phase": t.get("phase", ""),
        "sponsor": t.get("sponsor", ""),
        "url": t.get("url", ""),
        "summary": t.get("summary", ""),
        "overall_verdict": "UNKNOWN",
        "match_score": 0,
        "reasoning_steps": [],
        "ai_scored": False,
        "parse_error": True,
    }
