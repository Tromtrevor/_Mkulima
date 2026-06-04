# app/api/routes/data.py
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from current_data.current_data import fetch_realtime_data
from profit_calculation.profit_calc import calculate_profit, CROP_DATA
from mkulima_ai.insight_generator import generate_crop_insight
from mkulima_ai.chatbot import chatbot
import joblib
import pandas as pd
import geopandas as gpd
from pathlib import Path




current_dir = Path(__file__).resolve().parent
router = APIRouter()

models= {
    'maize': joblib.load(current_dir.parent.parent / "data" / "models" / "models" / "maize_model.pkl"),
    'beans': joblib.load(current_dir.parent.parent / "data" / "models" / "models" / "beans_model.pkl"),
    'potato': joblib.load(current_dir.parent.parent / "data" / "models" / "models" / "potato_model.pkl")
}

SHAPEFILE_PATH = Path(__file__).resolve().parent.parent.parent / "data" / "counties" / "counties.shp"
AGROVETS_PATH = current_dir.parent.parent.parent / "data" / "predictor" / "full_data_agrovets.csv"

if SHAPEFILE_PATH.exists():
    _gdf = gpd.read_file(SHAPEFILE_PATH)
    CACHED_COUNTIES = sorted(_gdf['county'].unique().tolist())
else:
    CACHED_COUNTIES = []

AGROVETS_DF = pd.read_csv(AGROVETS_PATH) if AGROVETS_PATH.exists() else None

prediction_cache = {}

class CropRequest(BaseModel):
    county: str = Field(..., example="Nakuru") # type: ignore
    farm_size: float = Field(..., gt=0, description="Farm size in acres", example=2.5) # type: ignore

class CropSelectionOwn(BaseModel):
    crop_name: str
    seed_cost_per_acre: Optional[float] = None
    fertilizer_cost_per_acre: Optional[float] = None
    labor_cost_per_acre: Optional[float] = None

class CropSelectionDefault(BaseModel):
    crop_name: str

class ChatRequest(BaseModel):
    message: str
    history: List[Dict] = []

class ProfitCalculationRequest(BaseModel):
    county: str
    farm_size: float
    crop_name: str
    predicted_yield_acres: float
    seed_cost_per_acre: Optional[float] = None
    fertilizer_cost_per_acre: Optional[float] = None
    labor_cost_per_acre: Optional[float] = None


@router.post("/crop/predict-yield", tags=["Prediction & Analysis"])
def predict_yield(request: CropRequest):
    location = request.county.strip()

    #Fetch environmental data
    data = fetch_realtime_data(location)
    if data is None or data.empty:
        raise HTTPException(status_code=404, detail=f"No environmental data found for county: {location}")

    data_indexed = data.set_index("County")
    #Predict yield
    predictions = {}
    for crop_name, model in models.items():
        prediction_in_ha = float(model.predict(data_indexed)[0])
        # Convert t/ha to t/acre
        prediction_in_acres = prediction_in_ha * 0.404686
        market_price = CROP_DATA.get(crop_name, {}).get("market_price", None)

        predictions[crop_name] = {
            "prediction_in_acres": round(prediction_in_acres, 2),
            "market_price": market_price
        }

    prediction_cache["latest"] = {
    "county": location,
    "farm_size": request.farm_size,
    "predictions": predictions,
    "input_data": data_indexed.to_dict(orient="records")[0],
    }

    return {
        "message": "Predictions generated successfully.",
        "data": prediction_cache["latest"],
    }


@router.post("/crop/calculate-own-profit", tags=["Prediction & Analysis"])
def calculate_own_profit(request: CropSelectionOwn):
    cache = prediction_cache.get('latest')
    if not cache:
        raise HTTPException(status_code=400, detail="No previous prediction found. Run /crop/predict-yield first.")

    crop_name = request.crop_name.lower()
    if crop_name not in cache["predictions"]:
        raise HTTPException(status_code=404, detail=f"No prediction data found for crop: {crop_name}")

    predicted_yield_acres = cache["predictions"][crop_name]["prediction_in_acres"]

    predicted_yield_acres = cache["predictions"][crop_name]["prediction_in_acres"]

    # Use the previously predicted yield
    profit = calculate_profit(
        crop_name,
        cache["farm_size"],
        predicted_yield_acres,
        seed_cost=request.seed_cost_per_acre,
        fertilizer_cost=request.fertilizer_cost_per_acre,
        labor_cost=request.labor_cost_per_acre
    )
    # Ensure values are numeric
    total_profit = float(profit["total_profit"])
    total_revenue = float(profit["total_revenue"])
    profit_margin = ((total_profit / total_revenue) * 100 if total_revenue > 0 else 0)

    prediction_cache["profit_analysis"] = {
        "crop": crop_name,
        "predicted_yield": predicted_yield_acres,
        "profit": profit,
        "profit_margin": round(profit_margin, 2),
        "market_price": CROP_DATA[crop_name]["market_price"],
    }

    return {
        "county": cache["county"],
        "farm_size": cache["farm_size"],
        "crop": crop_name,
        "profit": profit,
        "profit_margin": round(profit_margin, 2),
        "prediction": predicted_yield_acres,
        "market_price": CROP_DATA[crop_name]["market_price"],
        "cache": prediction_cache
    }


@router.post("/crop/calculate-default-profit", tags=["Prediction & Analysis"])
def calculate_default_profit(request: CropSelectionDefault):
    """Calculate profit using default/AI-optimized costs"""
    cache = prediction_cache.get('latest')
    if not cache:
        raise HTTPException(status_code=400, detail="No previous prediction found. Run /crop/predict-yield first.")

    crop_name = request.crop_name.lower()
    if crop_name not in cache["predictions"]:
        raise HTTPException(status_code=404, detail=f"No prediction found for {crop_name}.")

    predicted_yield_acres = cache["predictions"][crop_name]["prediction_in_acres"]

    # Use default costs from CROP_DATA
    profit = calculate_profit(
        crop_name,
        cache["farm_size"],
        predicted_yield_acres,
    )

    total_profit = float(profit["total_profit"])
    total_revenue = float(profit["total_revenue"])
    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0

    prediction_cache["profit_analysis"] = {
        "crop": crop_name,
        "predicted_yield": predicted_yield_acres,
        "profit": profit,
        "profit_margin": round(profit_margin, 2),
        "market_price": CROP_DATA[crop_name]["market_price"],
    }

    return {
        "county": cache["county"],
        "farm_size": cache["farm_size"],
        "crop": crop_name,
        "profit": profit,
        "profit_margin": round(profit_margin, 2),
        "prediction": predicted_yield_acres,
        "market_price": CROP_DATA[crop_name]["market_price"],
        "cache": prediction_cache
    }

@router.get("/crop/insight", tags=["Crop Management"])
def crop_insight():
    if not prediction_cache:
        raise HTTPException(status_code=400, detail="Cache empty. Please execute structural tasks first.")

    return {"Insights": generate_crop_insight(prediction_cache)}


@router.post("/crop/ai-chat", tags = ["AI Features"])
def chat_endpoint(request: ChatRequest):
    # System prompt
    messages = [
        {
            "role": "system",
            "content": "You are MkuliMA, an expert agronomist AI assistant helping Kenyan farmers with crop planning, soil health, and profitability, part of the Mkulima app."
        }
    ]

    # Add chat history
    for entry in request.history:
        messages.append({"role": "user", "content": entry.get("request", "")})
        messages.append({"role": "assistant", "content": entry.get("response", "")})

    # Current user message
    messages.append({"role": "user", "content": request.message})
    # Call your chatbot function
    reply = chatbot(messages)

    return {
        "reply": reply,
        "messages": messages + [{"role": "assistant", "content": reply}]
    }


@router.get("/crop/list", tags = ["Crop Management"])
def list_crops():
    return {"crops": list(models.keys())}


@router.get("/counties", tags = ["Location"])
def list_counties():
    if not CACHED_COUNTIES:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, 
            detail="Counties geospatial database is unavailable."
        )
    return {"counties": CACHED_COUNTIES}


# New endpoint for AgroServices
@router.get("/agroservices", tags = ["Location"])
def get_agroservices(county: str):
    if AGROVETS_DF is None:
        raise HTTPException(status_code=500, detail="Agrovet database lookup file is missing.")

    county_data = AGROVETS_DF[AGROVETS_DF["county"].str.lower() == county.lower().strip()]

    if county_data.empty:
        return {"message": f"No agrovets found for {county}."}

    # Convert to list of dicts for JSON response
    agrovets_list = county_data[["Title", "Category", "Latitude", "Longitude"]].to_dict(orient="records")
    return {"county": county, "agrovets": agrovets_list}