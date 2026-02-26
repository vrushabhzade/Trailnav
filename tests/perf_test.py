import time, sys
sys.path.insert(0, '.')
import requests

payload = {
    "clinical_note": "58F, EGFR exon 19 deletion, stage IV NSCLC, progressed on osimertinib. ECOG 1. PD-L1 45%.",
    "max_trials": 5, "min_score": 0, "generate_summary": False, "export_fhir": False
}
print("Testing with gemini-2.5-flash...")
start = time.time()
r = requests.post("http://localhost:8001/api/match", json=payload, timeout=60)
elapsed = time.time() - start
d = r.json()
print(f"Status: {r.status_code}  |  Time: {elapsed:.1f}s")
if r.status_code == 200:
    print(f"Trials matched: {d.get('total_matched')} / {d.get('total_fetched')}")
    for trial in d.get("matched_trials", [])[:3]:
        ai_tag = "(AI)" if trial.get("ai_scored") else "(KW)"
        print(f"  {ai_tag} {trial['nct_id']} | {trial['overall_verdict']} | Score:{trial['match_score']}%")
else:
    print("Error:", d.get("detail", "")[:200])
