"""Pydantic schemas for API request/response validation."""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class MatchRequest(BaseModel):
    clinical_note: str = Field(..., min_length=10, description="Free-text clinical note or EHR summary")
    max_trials: Optional[int] = Field(10, ge=1, le=50, description="Max trials to fetch from CT.gov")
    min_score: Optional[int] = Field(30, ge=0, le=100, description="Min match score threshold")
    export_fhir: Optional[bool] = True
    generate_summary: Optional[bool] = True


class ReasoningStep(BaseModel):
    criterion: str
    patient_status: str
    verdict: str  # MET | NOT_MET | BORDERLINE | UNKNOWN
    explanation: str


class TrialResult(BaseModel):
    nct_id: str
    title: str
    phase: Optional[str]
    sponsor: Optional[str]
    url: Optional[str]
    overall_verdict: str  # ELIGIBLE | LIKELY_ELIGIBLE | BORDERLINE | INELIGIBLE
    match_score: int
    reasoning_steps: Optional[List[ReasoningStep]] = []
    key_inclusions_met: Optional[List[str]] = []
    key_exclusions_triggered: Optional[List[str]] = []
    borderline_factors: Optional[List[str]] = []
    recommended_action: Optional[str] = ""
    rank: Optional[int]


class MatchResponse(BaseModel):
    patient_profile: Dict[str, Any]
    matched_trials: List[Dict[str, Any]]
    patient_summary: Optional[str]
    fhir_bundle: Optional[Dict[str, Any]]
    total_fetched: int
    total_matched: int


class CVDRiskRequest(BaseModel):
    age: float = Field(..., ge=1, le=120)
    sex: float = Field(..., description="1=male, 0=female")
    cp: float = Field(..., description="Chest pain type (1-4)")
    trestbps: float = Field(..., description="Resting blood pressure")
    chol: float = Field(..., description="Serum cholesterol in mg/dl")
    fbs: float = Field(..., description="Fasting blood sugar > 120 mg/dl (1=true, 0=false)")
    restecg: float = Field(..., description="Resting ECG results (0-2)")
    thalach: float = Field(..., description="Max heart rate achieved")
    exang: float = Field(..., description="Exercise induced angina (1=yes, 0=no)")
    oldpeak: float = Field(..., description="ST depression induced by exercise relative to rest")
    slope: float = Field(..., description="Slope of the peak exercise ST segment")
    ca: float = Field(..., description="Number of major vessels (0-3)")
    thal: float = Field(..., description="Thalassemia (3=normal, 6=fixed defect, 7=reversable defect)")


class CVDRiskResponse(BaseModel):
    risk_probability: float
    risk_level: str
    top_factors: List[List[Any]]
