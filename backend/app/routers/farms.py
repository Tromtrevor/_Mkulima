from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.farm import Farm
from app.schemas.farm import FarmResponse
from app.services.location import fetch_farm_location
from app.services.nasa_power import get_daily_weather
from app.services.feature_extraction import extract_weather_features
from app.services.crop_cycle import fetch_crop_cycle

router = APIRouter(
    prefix="/farms",
    tags=["Farms"]
)

@router.get("/{farm_id}", response_model=FarmResponse)
def get_farm(farm_id: int, db: Session = Depends(get_db)):
    farm = db.query(Farm).filter(Farm.farm_id == farm_id).first()

    if not farm:
        raise HTTPException(
            status_code=404,
            detail="Farm not found"
        )

    return farm

@router.get("/{farm_id}/location")
def get_farm_location(farm_id: int, db: Session = Depends(get_db)):
    location = fetch_farm_location(farm_id=farm_id, db=db)

    if not location:
        raise HTTPException(
            status_code=404,
            detail="Farm location not found"
        )

    return location

@router.get("/{farm_id}/cycles/{cycle_id}/weather")
def get_crop_cycle_weather(farm_id: int, cycle_id: int, db: Session = Depends(get_db)   ):
    location = fetch_farm_location(
        farm_id=farm_id,
        db=db
    )

    if not location:
        raise HTTPException(
            status_code=404,
            detail="Farm location not found"
        )

    cycle = fetch_crop_cycle(
        db=db,
        cycle_id=cycle_id
    )

    if not cycle:
        raise HTTPException(
            status_code=404,
            detail="Crop cycle not found"
        )

    if cycle["farm_id"] != farm_id:
        raise HTTPException(
            status_code=400,
            detail="Crop cycle does not belong to this farm"
        )

    weather = get_daily_weather(
        latitude=location["latitude"],
        longitude=location["longitude"],
        start_date=cycle["planting_date"].strftime("%Y%m%d"),
        end_date=cycle["harvest_date"].strftime("%Y%m%d")
    )

    features = extract_weather_features(weather)

    return {
        "farm_id": farm_id,
        "cycle_id": cycle_id,
        "planting_date": cycle["planting_date"],
        "harvest_date": cycle["harvest_date"],
        "features": features
    }