"""
Step 1 — Extract structured patient profile from clinical note using Gemini.
"""
import json
import re
from loguru import logger
from models import model_router

EXTRACT_PROMPT = """You are a clinical NLP system. Extract a structured patient profile from the clinical note below.
Return ONLY valid JSON with these exact fields (use null for missing fields):

{{
  "diagnosis": "primary diagnosis with stage",
  "histology": "histological subtype if mentioned",
  "biomarkers": ["list of biomarkers, e.g. EGFR L858R, PD-L1 TPS 45%"],
  "ecog": "ECOG performance status 0-4, or null",
  "prior_treatments": ["list of prior therapies"],
  "comorbidities": ["list of comorbidities"],
  "exclusions": ["factors that might exclude from trials"],
  "age": "patient age or null",
  "sex": "patient sex or null",
  "organ_function": {{
    "renal": "eGFR or creatinine if mentioned",
    "hepatic": "bilirubin/ALT or Child-Pugh if mentioned",
    "cardiac": "LVEF or cardiac conditions if mentioned"
  }},
  "key_labs": {{}}
}}

Clinical Note:
{note}

Return only the JSON object, no other text:"""


def extract_patient_profile(clinical_note: str) -> dict:
    """Use AI to extract structured patient profile from free-text clinical note."""
    prompt = EXTRACT_PROMPT.format(note=clinical_note)
    logger.info("Extracting patient profile...")

    response = model_router.generate(prompt, temperature=0.05)

    # Robust JSON extraction
    try:
        # Try to find JSON block in response
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            return json.loads(match.group())
        return json.loads(response)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error: {e}\nRaw response: {response[:500]}")
        return {
            "diagnosis": "unknown",
            "biomarkers": [],
            "prior_treatments": [],
            "comorbidities": [],
            "raw_response": response,
            "parse_error": True,
        }
