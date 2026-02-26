"""
Step 4 — Score, filter, and rank matched trials.
"""
from typing import List, Dict

# Verdict weights used for secondary sorting
VERDICT_RANK = {
    "ELIGIBLE": 4,
    "LIKELY_ELIGIBLE": 3,
    "BORDERLINE": 2,
    "INELIGIBLE": 1,
    "UNKNOWN": 0,
}


def rank_trials(
    evaluated_trials: List[Dict],
    min_score: int = 30,
    max_results: int = 10,
) -> List[Dict]:
    """
    Filter and rank trials.

    Args:
        evaluated_trials: Output from reasoner.evaluate_batch()
        min_score: Minimum match_score threshold (0-100)
        max_results: Maximum trials to return

    Returns:
        Filtered, ranked list of trial dicts with rank field added.
    """
    # Filter below threshold
    filtered = [t for t in evaluated_trials if t.get("match_score", 0) >= min_score]

    # Sort: primary = match_score, secondary = verdict weight
    ranked = sorted(
        filtered,
        key=lambda t: (
            t.get("match_score", 0),
            VERDICT_RANK.get(t.get("overall_verdict", "UNKNOWN"), 0),
        ),
        reverse=True,
    )

    # Add rank fields
    for i, trial in enumerate(ranked[:max_results], 1):
        trial["rank"] = i

    return ranked[:max_results]
