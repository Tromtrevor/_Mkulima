from datetime import date

from sqlalchemy import text
from sqlalchemy.orm import Session


def save_features(
    db: Session,
    farm_id: int,
    cycle_id: int,
    observation_date: date,
    features: dict
):

    query = text("""
        INSERT INTO farm_features (
            farm_id,
            cycle_id,
            ndvi_mean,
            ndvi_min,
            ndvi_max,
            rainfall_mm,
            temperature,
            observation_date
        )
        VALUES (
            :farm_id,
            :cycle_id,
            :ndvi_mean,
            :ndvi_min,
            :ndvi_max,
            :rainfall_mm,
            :temperature,
            :observation_date
        )
        ON CONFLICT (cycle_id, observation_date)
        DO UPDATE SET
            ndvi_mean = EXCLUDED.ndvi_mean,
            ndvi_min = EXCLUDED.ndvi_min,
            ndvi_max = EXCLUDED.ndvi_max,
            rainfall_mm = EXCLUDED.rainfall_mm,
            temperature = EXCLUDED.temperature
        RETURNING feature_id
    """)

    try:
        result = db.execute(
            query,
            {
                "farm_id": farm_id,
                "cycle_id": cycle_id,
                "ndvi_mean": features["ndvi_mean"],
                "ndvi_min": features["ndvi_min"],
                "ndvi_max": features["ndvi_max"],
                "rainfall_mm": features["rainfall_mm"],
                "temperature": features["temperature_mean_c"],
                "observation_date": observation_date
            }
        )

        feature_id = result.scalar_one()
        db.commit()

        return feature_id

    except Exception:
        db.rollback()
        raise
