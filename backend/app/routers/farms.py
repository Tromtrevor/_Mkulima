from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.farm import Farm
from app.schemas.farm import FarmResponse
from app.services.location import get_farm_location as fetch_farm_location
from app.services.nasa_power import get_daily_weather


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

@router.get("/{farm_id}/weather")
def get_farm_weather(farm_id: int, db: Session = Depends(get_db)):

    location = fetch_farm_location(farm_id=farm_id, db=db)

    if not location:
        raise HTTPException(
            status_code=404,
            detail="Farm location not found"
        )

    weather = get_daily_weather(
        latitude=location["latitude"],
        longitude=location["longitude"],
        start_date="20260301",
        end_date="20260331"
    )

    return {
        "farm_id": location["farm_id"],
        "farm_name": location["farm_name"],
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "weather": weather
    }