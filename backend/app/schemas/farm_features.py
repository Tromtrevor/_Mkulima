from datetime import datetime, date
from typing import Any

from pydantic import BaseModel


class FarmFeatureResponse(BaseModel):

	feature_id: int
	farm_id: int
	cycle_id: int
	planting_date: date
	observation_date: datetime | None = None
	weather: dict[str, Any]
	ndvi: dict[str, Any]
	soil: dict[str, Any]
	elevation: dict[str, Any]
	
	model_config = {
            "from_attributes": True
        }