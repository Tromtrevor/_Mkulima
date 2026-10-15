# app/routers/prediction.py
from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.farm import Farm
from app.models.crop_cycle import CropCycle
from app.schemas.predict import PredictResponse
from app.schemas.prediction import FarmPredictionResponse
from app.models.yield_prediction import YieldPrediction
from app.services.prediction import predict_yield
from app.services.prediction_storage import save_prediction

router = APIRouter(
    prefix="/predictions",
    tags=["Predictions"]
)

@router.post("/farms/{farm_id}/cycles/{cycle_id}/predict", response_model=PredictResponse)
def create_prediction(
    farm_id: int,
    cycle_id: int,
    db: Session = Depends(get_db),
):
    # Verify crop cycle belongs to the farm
    cycle = db.query(CropCycle).filter(
        CropCycle.cycle_id == cycle_id,
        CropCycle.farm_id == farm_id,
    ).first()

    if cycle is None:
        raise HTTPException(
            status_code=404,
            detail="Crop cycle not found for this farm",
        )

    # Retrieve the latest stored features
    row = db.execute(
        text("""
            SELECT
                elevation_m AS elev,
                temperature AS avg_season_tavg,
                rainfall_mm AS season_prec,
                soil_clay,
                "pH" AS "soil_pH",
                "soil_ECEC" AS "soil_ECEC",
                "soil_orgC" AS "soil_orgC"
            FROM farm_features
            WHERE farm_id = :farm_id
              AND cycle_id = :cycle_id
              AND observation_date <= :today
            ORDER BY observation_date DESC
            LIMIT 1
        """),
        {
            "farm_id": farm_id,
            "cycle_id": cycle_id,
            "today": date.today(),
        },
    ).mappings().first()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="No stored features found for this crop cycle",
        )

    features = dict(row)

    # Generate prediction
    try:
        result = predict_yield(features)
    except ValueError as exc:
        raise HTTPException(
            status_code=422,
            detail=str(exc),
        ) from exc
    except FileNotFoundError as exc:
        raise HTTPException(
            status_code=500,
            detail="Prediction model not found",
        ) from exc

    # Save prediction
    prediction_id = save_prediction(
        db=db,
        cycle_id=cycle_id,
        predicted_yield=result["predicted_yield"],
        model_version=result["model_version"],
    )

    return {
        "prediction_id": prediction_id,
        "farm_id": farm_id,
        "cycle_id": cycle_id,
        "predicted_yield": result["predicted_yield"],
        "unit": result["unit"],
        "model_version": result["model_version"],
        "features_used": result["features_used"],
    }


@router.get("/farms/{farm_id}/predictions", response_model=FarmPredictionResponse)
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