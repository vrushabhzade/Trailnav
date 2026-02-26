"""
End-to-end tests for TrialNav.

test_fetch_trials — hits live ClinicalTrials.gov API (requires internet)
test_ranker — purely local, tests ranking logic
test_full_pipeline — skipped if GEMINI_API_KEY not set
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
import json


class TestRetriever(unittest.TestCase):
    """Live ClinicalTrials.gov API tests (no AI)."""

    def test_fetch_nsclc_trials(self):
        from pipeline.retriever import fetch_trials_sync
        trials = fetch_trials_sync("lung cancer", max_results=5)
        self.assertIsInstance(trials, list)
        self.assertGreater(len(trials), 0)

    def test_trial_has_required_fields(self):
        from pipeline.retriever import fetch_trials_sync
        trials = fetch_trials_sync("breast cancer", max_results=3)
        for t in trials:
            self.assertIn("nct_id", t)
            self.assertIn("title", t)
            self.assertIn("eligibility_criteria", t)

    def test_fetch_with_invalid_condition(self):
        from pipeline.retriever import fetch_trials_sync
        trials = fetch_trials_sync("xyznonexistentcondition12345", max_results=5)
        self.assertIsInstance(trials, list)
        # Empty list is OK for non-existent condition


class TestRanker(unittest.TestCase):
    """Local ranker tests (no API)."""

    def _make_trial(self, score, verdict):
        return {"nct_id": f"NCT{score}", "title": f"Trial {score}", "match_score": score, "overall_verdict": verdict}

    def test_ranks_descending(self):
        from pipeline.ranker import rank_trials
        trials = [self._make_trial(60, "BORDERLINE"), self._make_trial(90, "ELIGIBLE"), self._make_trial(40, "BORDERLINE")]
        ranked = rank_trials(trials, min_score=0)
        scores = [t["match_score"] for t in ranked]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_filters_below_min_score(self):
        from pipeline.ranker import rank_trials
        trials = [self._make_trial(20, "INELIGIBLE"), self._make_trial(80, "ELIGIBLE")]
        ranked = rank_trials(trials, min_score=50)
        self.assertEqual(len(ranked), 1)
        self.assertEqual(ranked[0]["match_score"], 80)

    def test_adds_rank_field(self):
        from pipeline.ranker import rank_trials
        trials = [self._make_trial(70, "ELIGIBLE")]
        ranked = rank_trials(trials, min_score=0)
        self.assertEqual(ranked[0]["rank"], 1)


class TestFullPipeline(unittest.TestCase):
    """Full integration test — requires GEMINI_API_KEY or USE_OLLAMA=true."""

    @unittest.skipUnless(
        os.getenv("GEMINI_API_KEY") or os.getenv("USE_OLLAMA", "").lower() == "true",
        "Skipped: set GEMINI_API_KEY or USE_OLLAMA=true to run full pipeline test"
    )
    def test_nsclc_pipeline(self):
        from pipeline.extractor import extract_patient_profile
        from pipeline.retriever import fetch_trials_sync
        from pipeline.reasoner import evaluate_batch
        from pipeline.ranker import rank_trials

        with open("data/sample_patients/vignette_nsclc.json") as f:
            vignette = json.load(f)

        profile = extract_patient_profile(vignette["note"])
        self.assertIn("diagnosis", profile)

        trials = fetch_trials_sync("lung cancer", max_results=3)
        self.assertGreater(len(trials), 0)

        evaluated = evaluate_batch(profile, trials[:2])
        ranked = rank_trials(evaluated, min_score=0)
        self.assertIsInstance(ranked, list)


if __name__ == "__main__":
    unittest.main()
