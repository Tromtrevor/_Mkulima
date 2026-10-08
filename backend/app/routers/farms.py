from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.farm import Farm
from app.schemas.farm import FarmResponse


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