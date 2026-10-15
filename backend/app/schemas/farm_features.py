from datetime import datetime
from typing import Any

from pydantic import BaseModel


class FarmFeatureResponse(BaseModel):

	feature_id: int
	farm_id: int
	cycle_id: int
	planting_date: datetime | None = None
	observation_date: datetime | None = None
	weather: dict[str, Any]
	ndvi: dict[str, Any]
	soil: dict[str, Any]
	elevation: dict[str, Any]