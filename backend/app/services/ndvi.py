
import json
import os
from datetime import date, timedelta

import ee
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.orm import Session

load_dotenv()

EE_PROJECT_ID = os.getenv("EE_PROJECT_ID")


def initialize_earth_engine():
    if not EE_PROJECT_ID:
        raise ValueError("EE_PROJECT_ID is missing from .env")

    ee.Initialize(project=EE_PROJECT_ID)


def get_farm_ndvi(
    db: Session,
    farm_id: int,
    observation_date: date
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

    boundary_geojson = json.loads(result["boundary"])
    geometry = ee.Geometry(boundary_geojson)

    start_date = (
        observation_date - timedelta(days=30)
    ).isoformat()

    # Earth Engine's filterDate end date is exclusive.
    end_date = (
        observation_date + timedelta(days=1)
    ).isoformat()

    collection = (
        ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED")
        .filterBounds(geometry)
        .filterDate(start_date, end_date)
        .filter(
            ee.Filter.lte("CLOUDY_PIXEL_PERCENTAGE", 60)
        )
    )

    def calculate_ndvi(image):
        scl = image.select("SCL")

        clear_pixels = (
            scl.neq(3)     # Cloud shadow
            .And(scl.neq(8))   # Medium-probability cloud
            .And(scl.neq(9))   # High-probability cloud
            .And(scl.neq(10))  # Cirrus
            .And(scl.neq(11))  # Snow or ice
        )

        return (
            image.normalizedDifference(["B8", "B4"])
            .rename("NDVI")
            .updateMask(clear_pixels)
            .copyProperties(image, ["system:time_start"])
        )

    ndvi_collection = collection.map(calculate_ndvi)

    image_count = ndvi_collection.size().getInfo()

    if image_count == 0:
        return {
            "ndvi_mean": None,
            "ndvi_min": None,
            "ndvi_max": None,
            "image_count": 0,
            "window_start": start_date,
            "window_end": observation_date.isoformat()
        }

    composite = ndvi_collection.median()

    reducer = ee.Reducer.mean().combine(
        reducer2=ee.Reducer.minMax(),
        sharedInputs=True
    )

    statistics = composite.reduceRegion(
        reducer=reducer,
        geometry=geometry,
        scale=10,
        maxPixels=100000000,
        tileScale=4
    ).getInfo()

    return {
        "ndvi_mean": statistics.get("NDVI_mean"),
        "ndvi_min": statistics.get("NDVI_min"),
        "ndvi_max": statistics.get("NDVI_max"),
        "image_count": image_count,
        "window_start": start_date,
        "window_end": observation_date.isoformat()
    }