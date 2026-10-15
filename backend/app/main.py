from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers import farms
from app.routers import predictions

from app.services.earth_engine import initialize_earth_engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        initialize_earth_engine()
        print("✅ Google Earth Engine initialized successfully.")
    except Exception as e:
        print(f"⚠️ GEE Initialization failed: {e}. App is running but Earth Engine features will fail.")

    yield

app = FastAPI(
    lifespan=lifespan,
    title="Mkulima Backend",
    version="2.0.0",
)

app.include_router(farms.router)
app.include_router(predictions.router)

@app.get("/")
def root():
    return {
        "message": "Mkulima backend is working"
    }