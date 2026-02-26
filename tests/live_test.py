"""Quick live test of the /api/match endpoint."""
import requests, json

payload = {
    "clinical_note": "58F, EGFR exon 19 deletion, stage IIIB NSCLC, progressed on osimertinib. ECOG 1. PD-L1 45%.",
    "max_trials": 5,
    "min_score": 0,
    "generate_summary": False,
    "export_fhir": False
}

print("Sending POST /api/match ...")
r = requests.post("http://localhost:8001/api/match", json=payload, timeout=300)
d = r.json()

print(f"HTTP Status: {r.status_code}")

if r.status_code != 200:
    print(f"Error: {d.get('detail', '')[:400]}")
else:
    print(f"Diagnosis: {d.get('patient_profile', {}).get('diagnosis', 'N/A')}")
    print(f"Trials fetched: {d.get('total_fetched')} | Matched: {d.get('total_matched')}")
    for t in d.get("matched_trials", [])[:5]:
        rank = t.get("rank", "?")
        nct = t.get("nct_id", "?")
        score = t.get("match_score", 0)
        verdict = t.get("overall_verdict", "?")
        print(f"  Rank {rank} | {nct} | Score: {score}% | {verdict}")
