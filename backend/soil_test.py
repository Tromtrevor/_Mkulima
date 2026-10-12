
from app.database import SessionLocal
from app.services.elevation import get_farm_elevation


db = SessionLocal()

try:
    result = get_farm_elevation(
        db=db,
        farm_id=1
    )

    print(result)

finally:
    db.close()
