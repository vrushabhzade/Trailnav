"""
Step 5 — Generate patient-friendly summary + FHIR R4 ResearchStudy bundle export.
"""
import json
import re
from datetime import date
from typing import List, Dict, Optional
from loguru import logger
from models import model_router

SUMMARY_PROMPT = """You are a compassionate medical communicator. A patient has been matched with clinical trials.
Write a clear, warm, easy-to-understand summary at an 8th-grade reading level that explains:
1. What clinical trials are and why they may benefit this patient (2-3 sentences)
2. A brief description of the top 3 matched trials in plain language (no jargon)
3. Practical next steps the patient should take

Patient: {profile_summary}

Top Matched Trials:
{trial_summaries}

Write the patient-friendly summary now (plain text, no markdown headers):"""


def generate_patient_summary(profile: dict, top_trials: List[dict]) -> str:
    """Generate a plain-language patient summary using AI."""
    diagnosis = profile.get("diagnosis", "your condition")
    age = profile.get("age", "")
    sex = profile.get("sex", "")
    profile_summary = f"{diagnosis}" + (f", {age} year old {sex}" if age else "")

    trial_summaries = "\n".join([
        f"{i}. {t.get('title', 'Unknown Trial')} "
        f"(Match Score: {t.get('match_score', 0)}%, {t.get('phase', '')}): "
        f"{t.get('recommended_action', t.get('summary', '')[:150])}"
        for i, t in enumerate(top_trials[:3], 1)
    ])

    prompt = SUMMARY_PROMPT.format(
        profile_summary=profile_summary,
        trial_summaries=trial_summaries,
    )

    logger.info("Generating patient-friendly summary...")
    return model_router.generate(prompt, temperature=0.4)


def export_fhir_r4(patient_profile: dict, matched_trials: List[dict]) -> dict:
    """Generate FHIR R4 Bundle with ResearchStudy resources for matched trials."""
    entries = []
    for trial in matched_trials[:5]:
        entries.append({
            "fullUrl": f"https://clinicaltrials.gov/study/{trial.get('nct_id', '')}",
            "resource": {
                "resourceType": "ResearchStudy",
                "id": trial.get("nct_id", ""),
                "identifier": [{
                    "system": "https://clinicaltrials.gov",
                    "value": trial.get("nct_id", ""),
                }],
                "title": trial.get("title", ""),
                "status": "active",
                "phase": {"text": trial.get("phase", "")},
                "sponsor": {
                    "display": trial.get("sponsor", ""),
                },
                "extension": [
                    {
                        "url": "https://trialnav.ai/eligibility-score",
                        "valueInteger": trial.get("match_score", 0),
                    },
                    {
                        "url": "https://trialnav.ai/verdict",
                        "valueString": trial.get("overall_verdict", "UNKNOWN"),
                    },
                    {
                        "url": "https://trialnav.ai/recommended-action",
                        "valueString": trial.get("recommended_action", ""),
                    },
                ],
            },
        })

    return {
        "resourceType": "Bundle",
        "type": "collection",
        "timestamp": date.today().isoformat(),
        "meta": {
            "source": "TrialNav v1.0 · Gemini 2.0 Flash + ClinicalTrials.gov",
        },
        "total": len(entries),
        "entry": entries,
    }
