from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers import farms
from app.routers import predictions

from app.services.earth_engine import initialize_earth_engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_earth_engine()
    yield

app = FastAPI(
    title="Mkulima Backend",
    version="2.0.0",
    lifespan=lifespan
)


app.include_router(farms.router)
app.include_router(predictions.router)

@app.get("/")
def root():
    return {
        "message": "Mkulima backend is working"
    }