import os

import ee
from dotenv import load_dotenv

load_dotenv()

EE_PROJECT_ID = os.getenv("EE_PROJECT_ID")


def initialize_earth_engine():
    if not EE_PROJECT_ID:
        raise ValueError("EE_PROJECT_ID is missing from .env")

    try:
        ee.Initialize(project=EE_PROJECT_ID)
        print("✅ Google Earth Engine initialized successfully.")
    except Exception as e:
        #Log the error and safely re-raise
        print(f"⚠️ GEE Initialization failed: {e}. App is running but Earth Engine features will fail.")
        raise e