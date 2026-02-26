"""
Unit tests for the profile extractor.
Mocks the model_router so no API key or Ollama is needed.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import unittest
from unittest.mock import patch


SAMPLE_NOTE = (
    "58-year-old female with stage IIIB NSCLC, EGFR exon 19 deletion. "
    "Progressed on osimertinib. ECOG 1. PD-L1 45%."
)

MOCK_RESPONSE = json.dumps({
    "diagnosis": "stage IIIB non-small cell lung cancer",
    "histology": "adenocarcinoma",
    "biomarkers": ["EGFR exon 19 deletion", "PD-L1 TPS 45%"],
    "ecog": "1",
    "prior_treatments": ["osimertinib"],
    "comorbidities": [],
    "exclusions": [],
    "age": "58",
    "sex": "female",
    "organ_function": {"renal": None, "hepatic": None, "cardiac": None},
    "key_labs": {},
})


class TestExtractor(unittest.TestCase):

    @patch("models.model_router.generate", return_value=MOCK_RESPONSE)
    def test_extract_returns_dict(self, mock_gen):
        from pipeline.extractor import extract_patient_profile
        result = extract_patient_profile(SAMPLE_NOTE)
        self.assertIsInstance(result, dict)

    @patch("models.model_router.generate", return_value=MOCK_RESPONSE)
    def test_extract_has_required_keys(self, mock_gen):
        from pipeline.extractor import extract_patient_profile
        result = extract_patient_profile(SAMPLE_NOTE)
        for key in ["diagnosis", "biomarkers", "prior_treatments"]:
            self.assertIn(key, result)

    @patch("models.model_router.generate", return_value=MOCK_RESPONSE)
    def test_extract_diagnosis_nonempty(self, mock_gen):
        from pipeline.extractor import extract_patient_profile
        result = extract_patient_profile(SAMPLE_NOTE)
        self.assertTrue(result.get("diagnosis"))

    @patch("models.model_router.generate", return_value=MOCK_RESPONSE)
    def test_extract_biomarkers_is_list(self, mock_gen):
        from pipeline.extractor import extract_patient_profile
        result = extract_patient_profile(SAMPLE_NOTE)
        self.assertIsInstance(result.get("biomarkers"), list)

    @patch("models.model_router.generate", return_value="not json at all")
    def test_extract_handles_bad_json(self, mock_gen):
        from pipeline.extractor import extract_patient_profile
        result = extract_patient_profile(SAMPLE_NOTE)
        # Should not raise, should return fallback dict
        self.assertIsInstance(result, dict)


if __name__ == "__main__":
    unittest.main()
