
import os

import joblib
import pandas as pd


MODEL_PATH = os.path.join("..", "ml_models", "maize_yield_baseline.joblib")

FEATURES = [
    "elev",
    "avg_season_tavg",
    "season_prec",
    "soil_clay",
    "soil_pH",
    "soil_ECEC",
    "soil_orgC",
]


def load_model():
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Maize model not found: {MODEL_PATH}"
        )

    return joblib.load(MODEL_PATH)


def predict_yield(features: dict) -> dict:
    missing_features = [
        feature
        for feature in FEATURES
        if features.get(feature) is None
    ]

    if missing_features:
        raise ValueError(
            "Missing required prediction features: "
            + ", ".join(missing_features)
        )

    input_data = pd.DataFrame(
        [
            {
                feature: float(features[feature])
                for feature in FEATURES
            }
        ],
        columns=FEATURES,
    )

    model = load_model()
    predicted_yield = float(model.predict(input_data)[0])

    if not pd.notna(predicted_yield):
        raise ValueError("Model returned an invalid prediction")

    return {
        "predicted_yield": max(0.0, predicted_yield),
        "unit": "kg/ha",
        "model_version": "maize-v2",
        "features_used": FEATURES,
    }
