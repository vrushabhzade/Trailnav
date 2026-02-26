CONSOLIDATED_MATCH_PROMPT = """You are an expert clinical oncology system.
TASK: 
1. Extract a structured patient profile from the note.
2. Evaluate eligibility for the provided trials.

PATIENT NOTE:
{clinical_note}

TRIALS ({num_trials}):
{trials_block}

RETURN ONLY A JSON OBJECT:
{{
  "patient_profile": {{
    "diagnosis": "stage and type",
    "histology": "subtype",
    "biomarkers": ["list"],
    "ecog": "status",
    "age": "age",
    "sex": "sex"
  }},
  "evaluations": [
    {{
      "nct_id": "...",
      "overall_verdict": "ELIGIBLE|LIKELY_ELIGIBLE|BORDERLINE|INELIGIBLE",
      "match_score": 0-100,
      "reasoning": "brief summary",
      "matches": ["list of met criteria"],
      "exclusions": ["list of exclusion triggers"]
    }}
  ]
}}"""
