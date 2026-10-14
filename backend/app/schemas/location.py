from datetime import datetime

from pydantic import BaseModel


class LocationResponse(BaseModel):
    farm_id: int
    farm_name: str | None
    longitude: float | None
    latitude: float | None

    model_config = {
        "from_attributes": True
    }