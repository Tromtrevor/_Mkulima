
from sqlalchemy import text
from sqlalchemy.orm import Session

def fetch_farm_location(farm_id: int, db: Session):

    query = text("""
        SELECT
            farm_id,
            farm_name,
            ST_X(ST_Centroid(boundary)) AS longitude,
            ST_Y(ST_Centroid(boundary)) AS latitude
        FROM farms
        WHERE farm_id = :farm_id
    """)

    result = db.execute(
        query,
        {"farm_id": farm_id}
    ).mappings().first()

    if not result:
        return None

    return {
        "farm_id": result["farm_id"],
        "farm_name": result["farm_name"],
        "longitude": result["longitude"],
        "latitude": result["latitude"]
    }