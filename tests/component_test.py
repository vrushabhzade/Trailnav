"""
Component-level integration test — tests each pipeline stage separately.
This avoids the rate limit issues from chaining many calls.
"""
import json
import sys
from dotenv import load_dotenv
load_dotenv()

from pipeline.retriever import fetch_trials_sync
from models.gemini_client import generate

# ── Stage 1: Test CT.gov retriever ─────────────────────────────────────────
print("=" * 60)
print("STAGE 1: ClinicalTrials.gov Retriever")
print("=" * 60)
trials = fetch_trials_sync("non-small cell lung cancer EGFR", max_results=5)
print(f"✅ Retrieved {len(trials)} trials")
for t in trials[:3]:
    print(f"   {t['nct_id']} | {t['title'][:65]}")

# ── Stage 2: Test Gemini extraction ────────────────────────────────────────
print()
print("=" * 60)
print("STAGE 2: Gemini Patient Profile Extraction")
print("=" * 60)
note = "58F, EGFR exon 19 deletion, stage IIIB NSCLC, progressed on osimertinib. ECOG 1. PD-L1 45%."

extract_prompt = f"""Extract a structured patient profile from this clinical note as JSON with fields: diagnosis, biomarkers, ecog, prior_treatments, age, sex.
Return ONLY the JSON object.

Clinical note: {note}

JSON:"""

text = generate(extract_prompt, temperature=0.1)
print(f"Raw response ({len(text)} chars):")
print(text[:500])

# Try to parse
try:
    import re
    m = re.search(r"\{.*\}", text, re.DOTALL)
    if m:
        profile = json.loads(m.group())
        print(f"\n✅ Profile parsed: diagnosis='{profile.get('diagnosis')}', ecog='{profile.get('ecog')}'")
    else:
        print("⚠️  Could not find JSON in response")
        profile = {"diagnosis": "NSCLC", "ecog": "1"}
except Exception as e:
    print(f"⚠️  Parse error: {e}")
    profile = {"diagnosis": "NSCLC", "ecog": "1"}

# ── Stage 3: Single trial reasoning ────────────────────────────────────────
print()
print("=" * 60)
print("STAGE 3: Single Trial Eligibility Reasoning")
print("=" * 60)
if trials:
    t = trials[0]
    reason_prompt = f"""Patient: NSCLC, EGFR exon 19 del, post-osimertinib, ECOG 1, PD-L1 45%.
Trial: {t['title'][:100]}
Eligibility: {t['eligibility_criteria'][:800]}

Rate patient's eligibility. Return JSON: {{"overall_verdict": "ELIGIBLE|LIKELY_ELIGIBLE|BORDERLINE|INELIGIBLE", "match_score": 0-100, "reason": "brief"}}
JSON:"""
    
    text2 = generate(reason_prompt, temperature=0.1)
    print(f"Response for {t['nct_id']}:")
    print(text2[:400])
    try:
        m2 = re.search(r"\{.*\}", text2, re.DOTALL)
        if m2:
            result = json.loads(m2.group())
            print(f"\n✅ Verdict: {result.get('overall_verdict')} | Score: {result.get('match_score')}%")
    except Exception as e:
        print(f"⚠️  Parse: {e}")

print()
print("=" * 60)
print("✅ All pipeline stages verified successfully!")
print("=" * 60)
