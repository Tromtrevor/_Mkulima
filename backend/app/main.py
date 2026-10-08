from fastapi import FastAPI

from app.routers import farms


app = FastAPI(
    title="Mkulima Backend",
    version="2.0.0"
)


app.include_router(farms.router)


@app.get("/")
def root():
    return {
        "message": "Mkulima backend is working"
    }