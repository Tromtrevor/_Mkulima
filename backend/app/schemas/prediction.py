from datetime import datetime

from pydantic import BaseModel


class PredictionItem(BaseModel):
    prediction_id: int
    cycle_id: int
    prediction_date: datetime 
    predicted_yield: float
    confidence: float | None
    model_version: str

class FarmPredictionResponse(BaseModel):
    farm_id: int
    farm_name: str
    total_predictions: int
    predictions: list[PredictionItem]

    model_config = {
        "from_attributes": True
    }