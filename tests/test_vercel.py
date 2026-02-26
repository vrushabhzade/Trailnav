import requests

url = "https://trailnav.vercel.app/api/match"
payload = {
    "clinical_note": "58F, stage IV NSCLC, progressed on osimertinib. ECOG 1. PD-L1 45%.",
    "max_trials": 2,
    "generate_summary": False,
    "export_fhir": False
}

print(f"Pinging {url} ...")
try:
    r = requests.post(url, json=payload, timeout=40)
    print(f"Status: {r.status_code}")
    if r.status_code != 200:
        print("Error Response:")
        print(r.text)
    else:
        print("Success!")
        d = r.json()
        print(f"Matched {len(d.get('matched_trials', []))} trials.")
except Exception as e:
    print(f"Request failed: {e}")
