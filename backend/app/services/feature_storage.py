from datetime import date

from sqlalchemy import text
from sqlalchemy.orm import Session


def save_weather_features(
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
            rainfall_mm,
            temperature,
            observation_date
        )
        VALUES (
            :farm_id,
            :cycle_id,
            :rainfall_mm,
            :temperature,
            :observation_date
        )
        RETURNING feature_id
    """)

    result = db.execute(
        query,
        {
            "farm_id": farm_id,
            "cycle_id": cycle_id,
            "rainfall_mm": features["rainfall_mm"],
            "temperature": features["temperature_mean_c"],
            "observation_date": observation_date
        }
    )

    feature_id = result.scalar_one()
    db.commit()

    return feature_id