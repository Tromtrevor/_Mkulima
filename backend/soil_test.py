
from app.database import SessionLocal
from app.services.ndvi import initialize_earth_engine
from app.services.soil import get_farm_soil

initialize_earth_engine()

db = SessionLocal()

try:
    result = get_farm_soil(
        db=db,
        farm_id=1  # Use an existing farm ID
    )

    print(result)

finally:
    db.close()