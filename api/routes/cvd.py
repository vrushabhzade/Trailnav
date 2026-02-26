from fastapi import APIRouter, HTTPException
from api.schemas import CVDRiskRequest, CVDRiskResponse
from models.cvd_model import cvd_model_engine
from loguru import logger

router = APIRouter(prefix="/cvd", tags=["Research - CVD"])

@router.post("/predict", response_model=CVDRiskResponse)
async def predict_cvd_risk(request: CVDRiskRequest):
    """
    Predicts Cardiovascular Disease risk based on clinical parameters.
    Returns risk probability, risk level, and top contributing factors (SHAP).
    """
    try:
        # Convert request to dictionary
        patient_data = request.model_dump()
        
        # Get prediction from model engine
        result = cvd_model_engine.predict(patient_data)
        
        if result is None:
            raise HTTPException(status_code=500, detail="Model prediction failed.")
            
        return CVDRiskResponse(
            risk_probability=result["risk_probability"],
            risk_level=result["risk_level"],
            top_factors=result["top_factors"]
        )
    except Exception as e:
        logger.exception(f"API Error in CVD prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/info")
async def get_model_info():
    """Returns basic information about the CVD research model."""
    return {
        "model_name": "Random Forest Classifier",
        "dataset": "UCI Heart Disease (de-identified)",
        "features": cvd_model_engine.feature_names,
        "is_trained": cvd_model_engine.is_trained
    }
