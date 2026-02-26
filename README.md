# TrialNav 🩺

**TrialNav** is an AI-powered Clinical Trial Matching Navigator designed to bridge the gap between complex patient clinical notes and the massive database of recruiting clinical trials on ClinicalTrials.gov.

By leveraging Google's **Gemini 2.5 Flash** models, TrialNav intelligently extracts patient biomarkers, diagnoses, and regimens, and evaluates them strictly against detailed trial eligibility criteria to find the best possible matches.

![TrialNav Demo](https://img.shields.io/badge/Status-Active-success) ![License](https://img.shields.io/badge/License-MIT-blue) ![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![React](https://img.shields.io/badge/React-18-blue)

---

## ✨ Features

- **🧠 Advanced AI Extraction:** Automatically pulls out key clinical entities like Age, Sex, ECOG Status, Histology, and complex Biomarkers (e.g., EGFR, BRCA, PD-L1) from unstructured clinical notes.
- **⚡ Hybrid Matching Engine:** Uses a blazing-fast local keyword pre-ranking algorithm to filter the top candidates from CT.gov before using a targeted Unified AI call to evaluate inclusion/exclusion criteria.
- **🛡️ Rate-Limit Resilient:** Features a robust 25-second async timeout with an instant local keyword-scoring fallback to ensure the UI never hangs, even when free-tier API limits are reached.
- **📄 FHIR R4 Export:** Allows exporting patient profiles and matched trial recommendations into a standard HL7 FHIR Bundle for easy EHR integration.
- **📝 Patient-Friendly Summaries:** Uses AI to generate a jargon-free summary explaining the matched trials so patients can discuss them easily with their oncologists.

---

## 🏗️ Architecture

TrialNav operates on a decoupled **Python FastApi** Backend and **React (Vite)** Frontend.

### Backend (`/api` & `/pipeline`)
- **FastAPI**: Handles API routing cleanly and asynchronously.
- **Retrievers**: Hits the `ClinicalTrials.gov` REST API to dynamically pull the latest recruiting trials.
- **Reasoner (`pipeline/reasoner.py`)**: Uses the new official `google-genai` SDK to execute structured generation prompts, validating eligibility criteria against the patient's profile.

### Frontend (`/web`)
- **React + Vite**: High-performance, hot-reloading frontend.
- **Tailwind CSS**: A beautiful, dark-mode, responsive UI focused on healthcare accessibility.

---

## 🚀 Getting Started

### Prerequisites
- [Node.js](https://nodejs.org/) (v18+)
- [Python 3.10+](https://www.python.org/)
- Google AI Studio API Key (Free tier works perfectly)

### 1️⃣ Backend Setup
Navigate to the root directory and install Python dependencies:
```bash
pip install -r requirements.txt
```

Create a `.env` file in the root based on the `.env.example` (or configure it as follows):
```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

Run the backend server:
```bash
python api/main.py
```
*The server will start on `http://localhost:8001`.*

### 2️⃣ Frontend Setup
Open a new terminal and navigate to the `web` directory:
```bash
cd web
npm install
npm run dev
```
*The React app will start on `http://localhost:5173`.*

---

## 🧪 Demo Cases
The application comes pre-loaded with several realistic oncology vignettes located in `data/sample_patients/` and hardcoded in the UI for easy demoing:
- 🫁 **NSCLC (Post-Osimertinib)**
- 🎗️ **Triple-Negative Breast Cancer**
- 🧠 **Glioblastoma (Recurrent)**
- 🩸 **CLL (Post-BTKi)**
- ... and more.

---

## 🛠️ Built With

- **[Google Gemini](https://ai.google.dev/)** - Foundational LLM for Extraction & Reasoning
- **[FastAPI](https://fastapi.tiangolo.com/)** - High-performance Python backend framework
- **[React](https://react.dev/)** - UI Library
- **[Vite](https://vitejs.dev/)** - Frontend Tooling
- **[ClinicalTrials.gov API](https://clinicaltrials.gov/data-api/api)** - Live trial data source

---

## 📄 License
This project is licensed under the MIT License - see the LICENSE file for details.
