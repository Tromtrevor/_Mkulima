import requests


NASA_POWER_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"


def get_daily_weather(latitude: float, longitude: float, start_date: str, end_date: str):
    params = {
        "parameters": "PRECTOTCORR,T2M,T2M_MAX,T2M_MIN",
        "community": "AG",
        "longitude": longitude,
        "latitude": latitude,
        "start": start_date,
        "end": end_date,
        "format": "JSON"
    }

    response = requests.get(
        NASA_POWER_URL,
        params=params,
        timeout=30
    )

    response.raise_for_status()

    return response.json()