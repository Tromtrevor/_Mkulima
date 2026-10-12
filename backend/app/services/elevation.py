
import json

import ee
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.services.ndvi import initialize_earth_engine

initialize_earth_engine()

def get_farm_elevation(
    db: Session,
    farm_id: int
):
    result = db.execute(
        text("""
            SELECT ST_AsGeoJSON(boundary) AS boundary
            FROM farms
            WHERE farm_id = :farm_id
        """),
        {"farm_id": farm_id}
    ).mappings().first()

    if not result or not result["boundary"]:
        raise ValueError("Farm boundary not found")

    geometry = ee.Geometry(
        json.loads(result["boundary"])
    )

    elevation_image = (
        ee.Image("USGS/SRTMGL1_003")
        .select("elevation")
    )

    stats = elevation_image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=30,
        maxPixels=100000000,
        tileScale=4
    ).getInfo() or {}

    elevation = stats.get("elevation")

    if elevation is None:
        raise ValueError(
            "Could not calculate farm elevation"
        )

    return {
        "elevation_m": float(elevation),
        "source": "USGS/SRTMGL1_003",
        "resolution_m": 30,
        "unit": "m"
    }
