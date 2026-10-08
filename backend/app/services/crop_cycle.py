from sqlalchemy import text
from sqlalchemy.orm import Session


def fetch_crop_cycle(cycle_id: int, db: Session):
    query = text("""
        SELECT
            cycle_id,
            farm_id,
            crop_id,
            planting_date,
            harvest_date
        FROM crop_cycles
        WHERE cycle_id = :cycle_id
    """)

    result = db.execute(
        query,
        {"cycle_id": cycle_id}
    ).mappings().first()

    if not result:
        return None

    return result