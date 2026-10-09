
from datetime import date

from sqlalchemy import text
from sqlalchemy.orm import Session


def save_features(
    db: Session,
    farm_id: int,
    cycle_id: int,
    observation_date: date,
    weather: dict,
    ndvi: dict | None = None,
    soil: dict | None = None,
):
    ndvi = ndvi or {}
    soil = soil or {}

    query = text("""
        INSERT INTO farm_features (
            farm_id,
            cycle_id,
            ndvi_mean,
            ndvi_min,
            ndvi_max,
            rainfall_mm,
            temperature,
            "pH",
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
            :ph,
            :observation_date
        )
        ON CONFLICT (cycle_id, observation_date)
        DO UPDATE SET
            ndvi_mean = COALESCE(
                EXCLUDED.ndvi_mean,
                farm_features.ndvi_mean
            ),
            ndvi_min = COALESCE(
                EXCLUDED.ndvi_min,
                farm_features.ndvi_min
            ),
            ndvi_max = COALESCE(
                EXCLUDED.ndvi_max,
                farm_features.ndvi_max
            ),
            rainfall_mm = EXCLUDED.rainfall_mm,
            temperature = EXCLUDED.temperature,
            "pH" = COALESCE(
                EXCLUDED."pH",
                farm_features."pH"
            )
        RETURNING feature_id
    """)

    try:
        result = db.execute(
            query,
            {
                "farm_id": farm_id,
                "cycle_id": cycle_id,
                "ndvi_mean": ndvi["ndvi_mean"],
                "ndvi_min": ndvi["ndvi_min"],
                "ndvi_max": ndvi["ndvi_max"],
                "rainfall_mm": weather["rainfall_mm"],
                "temperature": weather["temperature_mean_c"],
                "ph": soil["ph"],
                "observation_date": observation_date,
            },
        )

        feature_id = result.scalar_one()
        db.commit()

        return feature_id

    except Exception:
        db.rollback()
        raise