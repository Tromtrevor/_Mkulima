# app/routers/prediction.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.farm import Farm
from app.models.crop_cycle import CropCycle
from app.models.yield_prediction import YieldPrediction

router = APIRouter(
    prefix="/predictions",
    tags=["Predictions"]
)


@router.get("/farms/{farm_id}/predictions")
def get_farm_predictions(
    farm_id: int,
    db: Session = Depends(get_db),
):
    farm = db.query(Farm).filter(
        Farm.farm_id == farm_id
    ).first()

    if farm is None:
        raise HTTPException(
            status_code=404,
            detail="Farm not found",
        )

    predictions = (
        db.query(YieldPrediction)
        .join(
            CropCycle,
            YieldPrediction.cycle_id == CropCycle.cycle_id,
        )
        .filter(CropCycle.farm_id == farm_id)
        .order_by(YieldPrediction.prediction_date.desc())
        .all()
    )

    return {
        "farm_id": farm_id,
        "farm_name": farm.farm_name,
        "total_predictions": len(predictions),
        "predictions": [
            {
                "prediction_id": p.prediction_id,
                "cycle_id": p.cycle_id,
                "prediction_date": p.prediction_date,
                "predicted_yield": p.predicted_yield,
                "confidence": p.confidence,
                "model_version": p.model_version,
            }
            for p in predictions
        ],
    }