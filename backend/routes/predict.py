from fastapi import APIRouter, HTTPException
import logging

from ..models.schemas import PredictRequest, ModelResult
from ..services.model_service import predict_probability

logger = logging.getLogger(__name__)

router = APIRouter()

@router.post("/predict", response_model=ModelResult)
def predict(req: PredictRequest) -> ModelResult:
    """Handle a /predict request: validate input, run the model, return the result."""
    try:
        logger.info(f"=== PREDICTION REQUEST ===")
        logger.info(f"Request data: {req.model_dump()}")
        
        payload = req.model_dump(mode="json")  # Enums -> strings
        logger.info(f"Payload (JSON mode): {payload}")
        
        result = predict_probability(payload)  # returns dict
        logger.info(f"Result: {result}")
        
        response = ModelResult(**result)
        logger.info(f"=== PREDICTION SUCCESS ===")
        return response
    except ValueError as e:
        logger.warning(f"Invalid prediction input: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        logger.exception("Error occurred during prediction")
        raise HTTPException(status_code=500, detail="Internal server error")