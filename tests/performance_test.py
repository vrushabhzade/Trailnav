import requests
import time
import json

payload = {
    "clinical_note": "58-year-old female with stage IIIB non-small cell lung cancer, EGFR exon 19 deletion. Progressed on osimertinib. ECOG 1. PD-L1 45%.",
    "max_trials": 5,
    "min_score": 10,
    "generate_summary": True,
    "export_fhir": False
}

def test_performance():
    print(f"🚀 Sending POST /api/match (max_trials={payload['max_trials']})...")
    start_time = time.time()
    try:
        r = requests.post("http://localhost:8001/api/match", json=payload, timeout=300)
        end_time = time.time()
        
        duration = end_time - start_time
        print(f"✅ Completed in {duration:.2f} seconds.")
        
        if r.status_code == 200:
            data = r.json()
            print(f"Status: {r.status_code}")
            print(f"Trials fetched: {data.get('total_fetched')}")
            print(f"Trials matched: {data.get('total_matched')}")
        else:
            print(f"❌ Error {r.status_code}: {r.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_performance()
