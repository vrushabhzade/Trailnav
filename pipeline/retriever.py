"""
Step 2 — Fetch relevant trials from ClinicalTrials.gov v2 API (completely free, no key needed).
Uses 'requests' library with browser User-Agent — httpx gets 403 from CT.gov on some networks.
"""
from typing import List, Dict, Optional
import requests
from loguru import logger

CT_GOV_BASE = "https://clinicaltrials.gov/api/v2/studies"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


def fetch_trials_sync(
    condition: str,
    intervention: Optional[str] = None,
    status: str = "RECRUITING",
    max_results: int = 20,
) -> List[Dict]:
    """Fetch trials from ClinicalTrials.gov API v2 (synchronous, no API key required)."""
    params = {
        "query.cond": condition,
        "filter.overallStatus": status,
        "pageSize": min(max_results, 50),
        "format": "json",
    }
    if intervention:
        params["query.intr"] = intervention

    logger.info(f"Fetching up to {max_results} trials for: '{condition}'")

    resp = requests.get(CT_GOV_BASE, params=params, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    trials = []
    for study in data.get("studies", []):
        proto = study.get("protocolSection", {})
        ident = proto.get("identificationModule", {})
        elig = proto.get("eligibilityModule", {})
        desc = proto.get("descriptionModule", {})
        status_mod = proto.get("statusModule", {})
        sponsor = proto.get("sponsorCollaboratorsModule", {})
        design = proto.get("designModule", {})

        phases = design.get("phases", [])
        phase_str = ", ".join(phases) if phases else "N/A"

        nct_id = ident.get("nctId", "")
        trials.append({
            "nct_id": nct_id,
            "title": ident.get("briefTitle", ""),
            "official_title": ident.get("officialTitle", ""),
            "phase": phase_str,
            "status": status_mod.get("overallStatus", ""),
            "eligibility_criteria": elig.get("eligibilityCriteria", "")[:4000],
            "summary": desc.get("briefSummary", ""),
            "sponsor": sponsor.get("leadSponsor", {}).get("name", ""),
            "url": f"https://clinicaltrials.gov/study/{nct_id}",
        })

    logger.success(f"Retrieved {len(trials)} trials from ClinicalTrials.gov")
    return trials
