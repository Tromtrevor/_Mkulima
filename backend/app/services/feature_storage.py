from datetime import date

from sqlalchemy.orm import Session

from app.models.farm_feature import FarmFeature


def save_weather_features(
    db: Session,
    farm_id: int,
    rainfall_mm: float,
    temperature: float,
    observation_date: date
):
    feature = FarmFeature(
        farm_id=farm_id,
        rainfall_mm=rainfall_mm,
        temperature=temperature,
        observation_date=observation_date
    )

    db.add(feature)
    db.commit()
    db.refresh(feature)

    return feature