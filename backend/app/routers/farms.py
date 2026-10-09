from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.models.farm import Farm
from app.schemas.farm import FarmResponse
from app.services.location import fetch_farm_location
from app.services.nasa_power import get_daily_weather
from app.services.feature_extraction import extract_weather_features
from app.services.crop_cycle import fetch_crop_cycle
from app.services.feature_storage import save_features
from app.services.ndvi import initialize_earth_engine, get_farm_ndvi

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
def get_crop_cycle_weather(
    farm_id: int,
    cycle_id: int,
    db: Session = Depends(get_db),
    observation_date: date = Query(..., description="Date of observation in YYYY-MM-DD format")
):
    
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
    #Error handling for crop cycle
    if not cycle:
        raise HTTPException(
            status_code=404,
            detail="Crop cycle not found"
        )
    #Error handling for farm_id and cycle_id mismatch
    if cycle["farm_id"] != farm_id:
        raise HTTPException(
            status_code=400,
            detail="Crop cycle does not belong to this farm"
        )
    #Error handling for observation date
    if observation_date > date.today():
        raise HTTPException(
            status_code=400,
            detail="Observation date cannot be in the future"
        )
    
    if observation_date < cycle["planting_date"]:
        raise HTTPException(
            status_code=400,
            detail="Observation date cannot be before planting"
        )

    if (
        cycle["harvest_date"] is not None
        and observation_date > cycle["harvest_date"]
    ):
        raise HTTPException(
            status_code=400,
            detail="Observation date cannot be after harvest"
        )

    #Fetch weather data from NASA POWER API
    weather = get_daily_weather(
        latitude=location["latitude"],
        longitude=location["longitude"],
        start_date=cycle["planting_date"].strftime("%Y%m%d"),
        end_date=observation_date.strftime("%Y%m%d")
    )

    #Extract features from the weather data
    weather_features = extract_weather_features(weather)

    #Initialize Earth Engine for NDVI extraction
    initialize_earth_engine()
    #Fetch NDVI features from Earth Engine for the farm and crop cycle
    ndvi_features = get_farm_ndvi(
        db=db,
        farm_id=farm_id,
        observation_date=observation_date
    )

    #Combine weather and NDVI features
    features = {
        **weather_features,
        **ndvi_features
    }

    #Store the extracted features in the database
    feature_id = save_features(
        db=db,
        farm_id=farm_id,
        cycle_id=cycle_id,
        observation_date=observation_date,
        features=features
    )

    return {
        "feature_id": feature_id,
        "farm_id": farm_id,
        "cycle_id": cycle_id,
        "planting_date": cycle["planting_date"],
        "observation_date": observation_date,
        "weather": weather_features,
        "ndvi": {
            "mean": ndvi_features["ndvi_mean"],
            "min": ndvi_features["ndvi_min"],
            "max": ndvi_features["ndvi_max"],
            "image_count": ndvi_features["image_count"]
        }
    }