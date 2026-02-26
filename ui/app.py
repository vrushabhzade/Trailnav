"""
TrialNav — Gradio Frontend
Free-tier: Gemini 2.0 Flash + ClinicalTrials.gov

Run:  python ui/app.py
Then: open http://localhost:7860
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

import gradio as gr
import httpx
import json

API_PORT = os.getenv("API_PORT", "8001")
API_URL = os.getenv("API_URL", f"http://localhost:{API_PORT}")

# ── Sample clinical notes ──────────────────────────────────────────────────────
SAMPLES = {
    "🫁 NSCLC (Post-Osimertinib)": (
        "58-year-old female with stage IIIB non-small cell lung cancer, "
        "EGFR exon 19 deletion confirmed on tissue biopsy. Progressed on osimertinib "
        "after 14 months. Prior platinum-based chemotherapy (carboplatin + pemetrexed, 4 cycles). "
        "ECOG performance status 1. PD-L1 TPS 45%, TMB 8 mut/Mb, TP53 co-mutation. "
        "Mild hepatic impairment (Child-Pugh A). No active autoimmune disease. "
        "No prior immunotherapy. eGFR 72 mL/min. Age 58."
    ),
    "🎗 Triple-Negative Breast Cancer": (
        "42-year-old female with triple-negative breast cancer (TNBC), stage IV metastatic. "
        "PD-L1 CPS 15, BRCA1/2 wild-type by germline testing. "
        "Previously treated with anthracycline and taxane-based regimen. "
        "No prior immunotherapy. ECOG PS 0. Normal organ function. "
        "Liver metastases confirmed on CT. Brain MRI negative."
    ),
    "🩸 CLL (Post-BTKi)": (
        "71-year-old male with chronic lymphocytic leukemia (CLL), del(17p) confirmed by FISH. "
        "Progressed on ibrutinib after 18 months of therapy (Bruton's kinase inhibitor). "
        "No prior venetoclax. ECOG PS 1. Creatinine clearance 58 mL/min. "
        "No active autoimmune disease. No transformation to Richter syndrome."
    ),
}


# ── Pipeline call ──────────────────────────────────────────────────────────────
def run_match(clinical_note: str, max_trials: int, min_score: int):
    if not clinical_note.strip():
        return "⚠️ Please enter a clinical note.", "", "", ""

    try:
        resp = httpx.post(
            f"{API_URL}/api/match",
            json={
                "clinical_note": clinical_note,
                "max_trials": int(max_trials),
                "min_score": int(min_score),
                "export_fhir": True,
                "generate_summary": True,
            },
            timeout=300.0,
        )
        resp.raise_for_status()
        data = resp.json()
    except httpx.ConnectError:
        err = (
            f"❌ Cannot connect to API at {API_URL}\n\n"
            "Make sure the FastAPI backend is running:\n"
            "```\nuvicorn api.main:app --reload --port 8000\n```"
        )
        return err, "", "", ""
    except Exception as e:
        return f"❌ Error: {e}", "", "", ""

    # ── Patient Profile Tab ────────────────────────────────────────────────────
    profile = data.get("patient_profile", {})
    profile_md = (
        f"## 🧬 Extracted Patient Profile\n\n"
        f"**Diagnosis:** {profile.get('diagnosis', 'N/A')}\n\n"
        f"**Histology:** {profile.get('histology', 'N/A')}\n\n"
        f"**Biomarkers:** {', '.join(profile.get('biomarkers', [])) or 'None listed'}\n\n"
        f"**ECOG PS:** {profile.get('ecog', 'N/A')}\n\n"
        f"**Prior Treatments:** {', '.join(profile.get('prior_treatments', [])) or 'None'}\n\n"
        f"**Comorbidities:** {', '.join(profile.get('comorbidities', [])) or 'None'}\n\n"
        f"**Age / Sex:** {profile.get('age', 'N/A')} / {profile.get('sex', 'N/A')}\n\n"
        f"---\n\n"
        f"<details><summary>📋 Full JSON</summary>\n\n```json\n{json.dumps(profile, indent=2)}\n```\n</details>"
    )

    # ── Matched Trials Tab ─────────────────────────────────────────────────────
    trials = data.get("matched_trials", [])
    total_fetched = data.get("total_fetched", 0)
    total_matched = data.get("total_matched", 0)

    verdict_emoji = {
        "ELIGIBLE": "✅",
        "LIKELY_ELIGIBLE": "🟢",
        "BORDERLINE": "🟡",
        "INELIGIBLE": "🔴",
        "UNKNOWN": "⚪",
    }

    trials_md = (
        f"## 🔬 Trial Match Results\n\n"
        f"**{total_matched} matched** out of {total_fetched} fetched from ClinicalTrials.gov\n\n---\n\n"
    )

    for t in trials[:8]:
        emoji = verdict_emoji.get(t.get("overall_verdict", "UNKNOWN"), "⚪")
        score = t.get("match_score", 0)
        verdict = t.get("overall_verdict", "UNKNOWN")
        score_bar = "█" * (score // 10) + "░" * (10 - score // 10)

        trials_md += (
            f"### {t.get('rank', '')}. {emoji} {t.get('title', 'Unknown')}\n\n"
            f"| Field | Value |\n|---|---|\n"
            f"| NCT ID | [{t.get('nct_id', '')}]({t.get('url', '#')}) |\n"
            f"| Phase | {t.get('phase', 'N/A')} |\n"
            f"| Sponsor | {t.get('sponsor', 'N/A')} |\n"
            f"| Verdict | **{verdict}** |\n"
            f"| Match Score | `{score_bar}` **{score}%** |\n\n"
        )

        if t.get("key_inclusions_met"):
            items = "\n".join(f"  - {x}" for x in t["key_inclusions_met"][:4])
            trials_md += f"**✅ Inclusions Met:**\n{items}\n\n"

        if t.get("key_exclusions_triggered"):
            items = "\n".join(f"  - {x}" for x in t["key_exclusions_triggered"][:3])
            trials_md += f"**🚫 Exclusions Triggered:**\n{items}\n\n"

        if t.get("borderline_factors"):
            items = "\n".join(f"  - {x}" for x in t["borderline_factors"][:2])
            trials_md += f"**⚠️ Borderline / Unclear:**\n{items}\n\n"

        if t.get("recommended_action"):
            trials_md += f"**📌 Recommended Action:** {t['recommended_action']}\n\n"

        trials_md += "---\n\n"

    if not trials:
        trials_md += "_No trials met the minimum match score threshold. Try lowering the Min Score slider._"

    # ── Patient Summary Tab ────────────────────────────────────────────────────
    summary = data.get("patient_summary") or "_No summary generated._"

    # ── FHIR JSON Tab ─────────────────────────────────────────────────────────
    fhir = json.dumps(data.get("fhir_bundle", {}), indent=2)

    return profile_md, trials_md, summary, fhir


# ── CVD Research Pipeline call ──────────────────────────────────────────────
def run_cvd_predict(
    age, sex, cp, trestbps, chol, fbs, restecg, 
    thalach, exang, oldpeak, slope, ca, thal
):
    try:
        # Map labels back to numeric values if needed
        sex_val = 1.0 if sex == "Male" else 0.0
        fbs_val = 1.0 if fbs == "Yes" else 0.0
        exang_val = 1.0 if exang == "Yes" else 0.0
        
        # Thalassemia mapping (3=normal, 6=fixed defect, 7=reversable defect)
        thal_map = {"Normal": 3.0, "Fixed Defect": 6.0, "Reversable Defect": 7.0}
        thal_val = thal_map.get(thal, 3.0)

        payload = {
            "age": float(age),
            "sex": sex_val,
            "cp": float(cp),
            "trestbps": float(trestbps),
            "chol": float(chol),
            "fbs": fbs_val,
            "restecg": float(restecg),
            "thalach": float(thalach),
            "exang": exang_val,
            "oldpeak": float(oldpeak),
            "slope": float(slope),
            "ca": float(ca),
            "thal": thal_val
        }

        resp = httpx.post(f"{API_URL}/api/cvd/predict", json=payload, timeout=30.0)
        resp.raise_for_status()
        data = resp.json()
        
        prob = data.get("risk_probability", 0.0)
        level = data.get("risk_level", "Low")
        factors = data.get("top_factors", [])
        
        # Format results
        result_md = f"## 🫀 Risk Assessment Result\n\n"
        result_md += f"### Risk Level: **{level}**\n"
        result_md += f"### Probability: `{prob * 100:.2f}%` \n\n"
        result_md += "---\n\n"
        result_md += "### 🔍 Top Contributing Factors (SHAP)\n"
        result_md += "_Positive values increase risk, negative values decrease risk._\n\n"
        
        for factor, val in factors:
            sign = "📈" if val > 0 else "📉"
            result_md += f"- **{factor}**: {sign} `{val:.4f}`\n"
            
        return result_md
    except Exception as e:
        return f"❌ Error: {e}"


def load_sample(sample_name: str):
    return SAMPLES.get(sample_name, "")


# ── Gradio UI ─────────────────────────────────────────────────────────────────
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&display=swap');

* { font-family: 'Sora', sans-serif !important; }

.gradio-container {
    max-width: 1300px !important;
    margin: auto !important;
    background: #0a0e1a !important;
}

body, .dark { background: #0a0e1a !important; }

#trialnav-header {
    background: linear-gradient(135deg, #0a0e1a 0%, #0f1e3a 50%, #0a1628 100%);
    padding: 40px 20px 30px;
    text-align: center;
    border-bottom: 1px solid #1e3a5f;
    margin-bottom: 24px;
}

#trialnav-header h1 {
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(90deg, #00d4ff, #7c3aed, #00d4ff);
    background-size: 200%;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    animation: shimmer 4s infinite linear;
    margin: 0;
}

@keyframes shimmer {
    0% { background-position: 0% }
    100% { background-position: 200% }
}

#trialnav-header p {
    color: #94a3b8;
    font-size: 1rem;
    margin-top: 8px;
}

.badge {
    display: inline-block;
    background: rgba(0, 212, 255, 0.1);
    border: 1px solid rgba(0, 212, 255, 0.3);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.75rem;
    color: #00d4ff;
    margin: 6px 4px;
}

.match-btn {
    background: linear-gradient(135deg, #00d4ff, #7c3aed) !important;
    color: white !important;
    font-weight: 700 !important;
    font-size: 1.05rem !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 14px !important;
    cursor: pointer !important;
    transition: all 0.3s !important;
    box-shadow: 0 4px 20px rgba(0, 212, 255, 0.3) !important;
}

.match-btn:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(0, 212, 255, 0.5) !important;
}

.panel {
    background: #0d1525 !important;
    border: 1px solid #1e3a5f !important;
    border-radius: 16px !important;
    padding: 20px !important;
}

label { color: #94a3b8 !important; font-size: 0.85rem !important; }

.status-bar {
    font-size: 0.8rem;
    color: #475569;
    text-align: center;
    margin-top: 16px;
    padding: 8px;
    border-top: 1px solid #1e293b;
}
"""

with gr.Blocks(
    title="TrialNav — AI Clinical Trial Matching",
    css=CSS,
    theme=gr.themes.Base(
        primary_hue="cyan",
        neutral_hue="slate",
        radius_size=gr.themes.sizes.radius_lg,
    ),
) as demo:

    # Header
    gr.HTML("""
    <div id="trialnav-header">
        <h1>🔬 MedGemma Research</h1>
        <p>AI Clinical Trial Platform & Healthcare Research Workbench</p>
        <div>
            <span class="badge">Gemini 2.0 Flash</span>
            <span class="badge">CVD Multi-Modal Model</span>
            <span class="badge">SHAP Interpretability</span>
            <span class="badge">FHIR R4</span>
        </div>
    </div>
    """)

    with gr.Tabs():
        with gr.Tab("🔬 Clinical Trial Navigator"):
            with gr.Row(equal_height=False):

                # Left panel — Input
                with gr.Column(scale=1, min_width=380, elem_classes=["panel"]):
                    gr.Markdown("### 📝 Patient Clinical Note")

                    sample_dd = gr.Dropdown(
                        choices=list(SAMPLES.keys()),
                        label="Load Demo Case",
                        value=None,
                        interactive=True,
                    )

                    note_input = gr.Textbox(
                        label="Clinical Note / EHR Summary",
                        placeholder=(
                            "Paste physician note, EHR summary, discharge summary, "
                            "or pathology report here..."
                        ),
                        lines=14,
                        max_lines=25,
                    )

                    with gr.Row():
                        max_trials = gr.Slider(
                            minimum=5, maximum=50, value=10, step=5,
                            label="Trials to Fetch from CT.gov",
                        )
                    with gr.Row():
                        min_score = gr.Slider(
                            minimum=0, maximum=80, value=30, step=10,
                            label="Minimum Match Score (%)",
                        )

                    match_btn = gr.Button(
                        "🔍 Match Trials",
                        elem_classes=["match-btn"],
                        size="lg",
                    )

                    gr.HTML("""
                    <div class="status-bar">
                        ⚡ Free tier · Gemini 2.0 Flash · ~30–60s per run
                    </div>
                    """)

                # Right panel — Output
                with gr.Column(scale=2, elem_classes=["panel"]):
                    gr.Markdown("### 📊 Results")
                    with gr.Tabs():
                        with gr.Tab("🧬 Patient Profile"):
                            profile_out = gr.Markdown(
                                value="_Run a match to see extracted patient profile..._"
                            )
                        with gr.Tab("🔬 Matched Trials"):
                            trials_out = gr.Markdown(
                                value="_Ranked trial matches will appear here..._"
                            )
                        with gr.Tab("📄 Patient Summary"):
                            summary_out = gr.Textbox(
                                label="Plain-Language Summary (8th Grade Reading Level)",
                                lines=18,
                                placeholder="Patient-friendly explanation of matched trials...",
                                interactive=False,
                            )
                        with gr.Tab("🏥 FHIR R4 Export"):
                            fhir_out = gr.Code(
                                language="json",
                                label="FHIR R4 Bundle (ResearchStudy resources)",
                            )

        with gr.Tab("🫀 CVD Risk Research"):
            with gr.Row():
                with gr.Column(scale=1, elem_classes=["panel"]):
                    gr.Markdown("### 🧬 Patient Parameters")
                    
                    with gr.Row():
                        age = gr.Slider(label="Age", minimum=1, maximum=120, value=50, step=1)
                        sex = gr.Radio(label="Sex", choices=["Male", "Female"], value="Male")
                    
                    with gr.Row():
                        cp = gr.Slider(label="Chest Pain Type (1-4)", minimum=1, maximum=4, value=2, step=1)
                        trestbps = gr.Slider(label="Resting BP (mm Hg)", minimum=80, maximum=200, value=120, step=1)
                    
                    with gr.Row():
                        chol = gr.Slider(label="Cholesterol (mg/dl)", minimum=100, maximum=600, value=200, step=1)
                        fbs = gr.Radio(label="Fasting Blood Sugar > 120", choices=["Yes", "No"], value="No")
                    
                    with gr.Row():
                        restecg = gr.Slider(label="Resting ECG Results (0-2)", minimum=0, maximum=2, value=0, step=1)
                        thalach = gr.Slider(label="Max Heart Rate achieved", minimum=60, maximum=220, value=150, step=1)
                    
                    with gr.Row():
                        exang = gr.Radio(label="Exercise Induced Angina", choices=["Yes", "No"], value="No")
                        oldpeak = gr.Slider(label="ST depression", minimum=0.0, maximum=6.2, value=0.0, step=0.1)
                    
                    with gr.Row():
                        slope = gr.Slider(label="Slope of peak exercise ST", minimum=1, maximum=3, value=1, step=1)
                        ca = gr.Slider(label="Number of major vessels (0-3)", minimum=0, maximum=3, value=0, step=1)
                        
                    thal = gr.Dropdown(
                        label="Thalassemia",
                        choices=["Normal", "Fixed Defect", "Reversable Defect"],
                        value="Normal"
                    )
                    
                    predict_btn = gr.Button("🧠 Analyze CVD Risk", elem_classes=["match-btn"])

                with gr.Column(scale=1, elem_classes=["panel"]):
                    gr.Markdown("### 📊 Research Analysis")
                    cvd_out = gr.Markdown(value="_Adjust parameters and run analysis to see insights..._")

    # ── Events ────────────────────────────────────────────────────────────────
    sample_dd.change(
        fn=load_sample,
        inputs=[sample_dd],
        outputs=[note_input],
    )

    match_btn.click(
        fn=run_match,
        inputs=[note_input, max_trials, min_score],
        outputs=[profile_out, trials_out, summary_out, fhir_out],
        api_name="match",
    )
    
    predict_btn.click(
        fn=run_cvd_predict,
        inputs=[
            age, sex, cp, trestbps, chol, fbs, restecg, 
            thalach, exang, oldpeak, slope, ca, thal
        ],
        outputs=[cvd_out]
    )

    # Footer
    gr.HTML("""
    <div style="text-align:center; color:#334155; font-size:0.75rem; padding:20px; margin-top:12px;">
        TrialNav v1.0 · MedGemma HAI-DEF Hackathon · MIT License ·
        <a href="http://localhost:8000/docs" style="color:#00d4ff;" target="_blank">API Docs →</a>
    </div>
    """)


if __name__ == "__main__":
    port = int(os.getenv("UI_PORT", 7860))
    demo.launch(
        server_name="0.0.0.0",
        server_port=port,
        share=False,
        show_error=True,
    )
