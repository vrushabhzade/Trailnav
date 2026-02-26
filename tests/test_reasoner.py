"""
Unit tests for the eligibility reasoner.
Mocks model_router — no API key or Ollama needed.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import unittest
from unittest.mock import patch

SAMPLE_PROFILE = {
    "diagnosis": "stage IIIB non-small cell lung cancer",
    "biomarkers": ["EGFR exon 19 deletion", "PD-L1 TPS 45%"],
    "ecog": "1",
    "prior_treatments": ["osimertinib"],
    "age": "58",
    "sex": "female",
}

SAMPLE_TRIAL = {
    "nct_id": "NCT12345678",
    "title": "Phase II Study of Novel EGFR Inhibitor in NSCLC",
    "phase": "PHASE2",
    "sponsor": "Test Pharma",
    "eligibility_criteria": (
        "Inclusion: Age >= 18. Stage IIIB/IV NSCLC. EGFR mutation. Prior TKI. ECOG 0-2.\n"
        "Exclusion: Active CNS metastases. Prior immunotherapy within 3 months."
    ),
    "url": "https://clinicaltrials.gov/study/NCT12345678",
    "summary": "A study evaluating a novel EGFR inhibitor in patients with NSCLC.",
}

MOCK_VERDICT = json.dumps({
    "nct_id": "NCT12345678",
    "overall_verdict": "LIKELY_ELIGIBLE",
    "match_score": 78,
    "reasoning_steps": [
        {
            "criterion": "EGFR mutation required",
            "patient_status": "EGFR exon 19 deletion confirmed",
            "verdict": "MET",
            "explanation": "Patient has confirmed EGFR mutation.",
        }
    ],
    "key_inclusions_met": ["EGFR mutation", "ECOG 0-2"],
    "key_exclusions_triggered": [],
    "borderline_factors": ["PD-L1 status not listed in criteria"],
    "recommended_action": "Contact trial coordinator for pre-screening.",
})


class TestReasoner(unittest.TestCase):

    @patch("models.model_router.generate", return_value=MOCK_VERDICT)
    def test_evaluate_returns_dict(self, mock_gen):
        from pipeline.reasoner import evaluate_eligibility
        result = evaluate_eligibility(SAMPLE_PROFILE, SAMPLE_TRIAL)
        self.assertIsInstance(result, dict)

    @patch("models.model_router.generate", return_value=MOCK_VERDICT)
    def test_evaluate_has_verdict(self, mock_gen):
        from pipeline.reasoner import evaluate_eligibility
        result = evaluate_eligibility(SAMPLE_PROFILE, SAMPLE_TRIAL)
        self.assertIn(result["overall_verdict"], [
            "ELIGIBLE", "LIKELY_ELIGIBLE", "BORDERLINE", "INELIGIBLE", "UNKNOWN"
        ])

    @patch("models.model_router.generate", return_value=MOCK_VERDICT)
    def test_evaluate_has_score(self, mock_gen):
        from pipeline.reasoner import evaluate_eligibility
        result = evaluate_eligibility(SAMPLE_PROFILE, SAMPLE_TRIAL)
        self.assertIsInstance(result.get("match_score"), int)
        self.assertGreaterEqual(result["match_score"], 0)
        self.assertLessEqual(result["match_score"], 100)

    @patch("models.model_router.generate", return_value="bad json response")
    def test_evaluate_handles_parse_error(self, mock_gen):
        from pipeline.reasoner import evaluate_eligibility
        result = evaluate_eligibility(SAMPLE_PROFILE, SAMPLE_TRIAL)
        self.assertIsInstance(result, dict)
        self.assertEqual(result["overall_verdict"], "UNKNOWN")

    @patch("models.model_router.generate", return_value=MOCK_VERDICT)
    def test_batch_sorted_by_score(self, mock_gen):
        from pipeline.reasoner import evaluate_batch
        trials = [SAMPLE_TRIAL, SAMPLE_TRIAL]
        results = evaluate_batch(SAMPLE_PROFILE, trials)
        scores = [r.get("match_score", 0) for r in results]
        self.assertEqual(scores, sorted(scores, reverse=True))


if __name__ == "__main__":
    unittest.main()
