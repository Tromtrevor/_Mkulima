from pydantic import BaseModel


class PredictResponse(BaseModel):
    prediction_id: int
    farm_id: int
    cycle_id: int
    predicted_yield: float | None
    unit: str | None
    model_version: str | None
    features_used: list[str]

    model_config = {
        "from_attributes": True
    }
