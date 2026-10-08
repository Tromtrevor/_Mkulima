from datetime import datetime

from pydantic import BaseModel


class FarmResponse(BaseModel):
    farm_id: int
    farmer_id: int | None
    farm_name: str | None
    area_ha: float | None
    created_at: datetime | None

    model_config = {
        "from_attributes": True
    }