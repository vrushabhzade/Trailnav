# 🏥 TrailNav: AI Clinical Matcher & Cardological Research Tool

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-20232A?style=flat&logo=react)](https://reactjs.org/)
[![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat&logo=vite)](https://vitejs.dev/)
[![Gemini](https://img.shields.io/badge/Gemini%202.0-8E75B2?style=flat&logo=google-gemini)](https://ai.google.dev/)
[![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-F7931E?style=flat&logo=scikit-learn)](https://scikit-learn.org/)

**TrailNav** is an advanced medical platform that combines **Generative AI** for clinical trial matching with **Explainable ML** for cardiovascular risk assessment. It aims to streamline the workflow for medical researchers and clinicians by bridging the gap between clinical notes and actionable data.

---

## 🚀 Two Powerful Modules

### 1. 🧬 Clinical Trial Navigator
Automates the process of matching patients to clinical trials using **Google Gemini 2.0 Flash**.
- **Intelligent Extraction**: Parses unstructured notes into structured JSON patient profiles.
- **Hybrid Matching**: Combines Gemini's reasoning with a fast, local keyword-based fallback system.
- **FHIR Integration**: Built with interoperability in mind using FHIR-ready data schemas.

### 2. ❤️ CVD Research Engine
An explainable machine learning module for predicting Cardiovascular Disease risk.
- **Predictive Modeling**: Uses a Random Forest classifier trained on UCI Heart Disease datasets.
- **Explainability (SHAP)**: Provides personalized risk assessments with visual evidence of contributing factors.
- **Research Ready**: Includes EDA pipelines and interpretability reports.

---

## ✨ Features
- **Modern Dashboard**: Responsive UI built with Framer Motion for smooth, premium transitions.
- **Speed & Reliability**: Optimized pipeline ensures fast matches even when LLM APIs are rate-limited.
- **Privacy Focused**: Direct API integration with Google AI Studio—no intermediate data storage.
- **Developer Friendly**: Fully documented FastAPI backend with interactive Swagger & ReDoc.

---

## 🏗️ Architecture
TrailNav uses a multi-stage pipeline:
1. **Extractor**: Extracts markers (Diagnosis, ECOG, Biomarkers) from notes.
2. **Retriever**: Fetches real-time trials via ClinicalTrials.gov API.
3. **Reasoner**: Multi-step AI validation for eligibility criteria.
4. **CVD Engine**: Parallel ML processing for cardiac risk profiling.

---

## 🛠️ Installation

### Prerequisites
- Python 3.10+
- Node.js 18+
- [Google Gemini API Key](https://aistudio.google.com/)

### 🔧 Setup & Start
```bash
# Clone the repository
git clone https://github.com/vrushabhzade/Trailnav.git
cd Trailnav

# Backend Setup
# It is recommended to use a virtual environment
pip install -r requirements.txt
cp .env.example .env  # Add your GEMINI_API_KEY to .env

# Start Backend
python api/main.py

# Frontend Setup
npm install
npm run dev
```

---

## 📖 API Documentation
Once the backend is live at `http://localhost:8001`:
- **Swagger UI**: `/docs`
- **ReDoc**: `/redoc`

---

## 🤝 Contributing
Contributions are welcome! If you find a bug or have a feature request, please open an issue or submit a pull request.

---

## 📄 License
This project is licensed under the MIT License.
