from datetime import date

from sqlalchemy.orm import Session

from app.models.yield_prediction import YieldPrediction


def save_prediction(
    db: Session,
    cycle_id: int,
    predicted_yield: float,
    model_version: str = "maize_v2",
    confidence: float | None = None,
) -> int:
    
    prediction = YieldPrediction(
        cycle_id=cycle_id,
        prediction_date=date.today(),
        predicted_yield=predicted_yield,
        confidence=confidence,
        model_version=model_version,
    )

    try:
        db.add(prediction)
        db.commit()
        db.refresh(prediction)

        return prediction.prediction_id

    except Exception:
        db.rollback()
        raise