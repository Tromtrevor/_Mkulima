
from datetime import date

from app.database import SessionLocal
from app.services.ndvi import (
    initialize_earth_engine,
    get_farm_ndvi,
)

initialize_earth_engine()

db = SessionLocal()

try:
    result = get_farm_ndvi(
        db=db,
        farm_id=1,  # Replace with an existing farm ID
        observation_date=date(2026, 4, 15)
    )

    print(result)

finally:
    db.close()