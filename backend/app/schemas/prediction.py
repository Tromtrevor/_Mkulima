from datetime import datetime

from pydantic import BaseModel


class PredictionResponse(BaseModel):
    prediction_id: int
    cycle_id: int
    prediction_date: datetime | None
    predicted_yield: float | None
    confidence: float | None
    model_version: str | None

    model_config = {
        "from_attributes": True
    }