
import json

import ee
from sqlalchemy import text
from sqlalchemy.orm import Session


def get_farm_soil(
    db: Session,
    farm_id: int
):
    cached_soil = db.execute(
        text("""
            SELECT
                "pH",
                "soil_clay",
                "soil_orgC",
                "soil_ECEC"
            FROM farm_features
            WHERE farm_id = :farm_id
                AND "pH" IS NOT NULL
                AND "soil_clay" IS NOT NULL
                AND "soil_orgC" IS NOT NULL
                AND "soil_ECEC" IS NOT NULL
            ORDER BY observation_date DESC
            LIMIT 1
        """),
        {"farm_id": farm_id},
    ).mappings().first()

    if cached_soil:
        return {
            "soil_rzpawhc": None,
            "soil_clay": float(cached_soil["soil_clay"]),
            "soil_pH": float(cached_soil["pH"]),
            "soil_orgC": float(cached_soil["soil_orgC"]),
            "soil_ECEC": float(cached_soil["soil_ECEC"]),
            "source": "farm_features_cache",
            "resolution_m": {
                "soil_rzpawhc": 1000,
                "soil_clay": 30,
                "soil_pH": 30,
                "soil_orgC": 30,
                "soil_ECEC": 30,
            },
        }

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

    # iSDA Africa soil datasets, using the 0-20 cm depth band.
    soil_layers = {
        "soil_clay": (
            "ISDASOIL/Africa/v1/clay_content",
            "mean_0_20",
            "exponential",
        ),
        "soil_pH": (
            "ISDASOIL/Africa/v1/ph",
            "mean_0_20",
            "divide_10",
        ),
        "soil_orgC": (
            "ISDASOIL/Africa/v1/carbon_organic",
            "mean_0_20",
            "exponential",
        ),
        "soil_ECEC": (
            "ISDASOIL/Africa/v1/cation_exchange_capacity",
            "mean_0_20",
            "exponential",
        ),
    }

    images = []

    for feature_name, (asset, band, transform) in soil_layers.items():
        image = (
            ee.Image(asset)
            .select(band)
            .rename(feature_name)
        )

        if transform == "exponential":
            image = image.divide(10).exp().subtract(1)

        elif transform == "divide_10":
            image = image.divide(10)

        images.append(image)

    soil_image = ee.Image.cat(images)

    stats = soil_image.reduceRegion(
        reducer=ee.Reducer.mean(),
        geometry=geometry,
        scale=30,
        maxPixels=100000000,
        tileScale=4
    ).getInfo() or {}

    return {
        "soil_rzpawhc": None,
        "soil_clay": stats.get("soil_clay"),
        "soil_pH": stats.get("soil_pH"),
        "soil_orgC": stats.get("soil_orgC"),
        "soil_ECEC": stats.get("soil_ECEC"),
        "source": "iSDA Africa",
        "resolution_m": {
            "soil_rzpawhc": 1000,
            "soil_clay": 30,
            "soil_pH": 30,
            "soil_orgC": 30,
            "soil_ECEC": 30,
        },
    }
