from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import farms
from app.routers import predictions

from app.services.earth_engine import initialize_earth_engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    #Initialize Google Earth Engine when the app starts
    initialize_earth_engine()
    yield

app = FastAPI(
    lifespan=lifespan,
    title="Mkulima Backend",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(farms.router)
app.include_router(predictions.router)

@app.get("/")
def root():
    return {
        "message": "Mkulima backend is working"
    }