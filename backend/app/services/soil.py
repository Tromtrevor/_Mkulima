
import json

import ee
from sqlalchemy import text
from sqlalchemy.orm import Session


def get_farm_soil(
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

    # The dataset stores pH multiplied by 10.
    soil_image = (
        ee.Image(
            "OpenLandMap/SOL/SOL_PH-H2O_USDA-4C1A2A_M/v02"
        )
        .select("b0")
        .divide(10)
        .rename("ph")
    )

    stats = soil_image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=250,
        maxPixels=100000000,
        tileScale=4
    ).getInfo()

    return {
        "ph": stats.get("ph"),
        "source": "OpenLandMap",
        "resolution_m": 250
    }