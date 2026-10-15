import os

import requests
import streamlit as st


DEFAULT_API_URL = "http://localhost:8000"


class BackendAPIError(RuntimeError):
    """Raised when the Mkulima backend cannot complete a request."""


def get_api_base_url():
    configured_url = os.getenv("MUKULIMA_API_URL", DEFAULT_API_URL)
    return configured_url.rstrip("/")


def _request(method, path, **kwargs):
    url = f"{get_api_base_url()}{path}"
    try:
        response = requests.request(method, url, timeout=30, **kwargs)
    except requests.RequestException as exc:
        raise BackendAPIError(
            f"Could not connect to the Mkulima API at {get_api_base_url()}: {exc}"
        ) from exc

    try:
        payload = response.json()
    except ValueError:
        payload = None

    if not response.ok:
        detail = payload.get("detail") if isinstance(payload, dict) else None
        message = detail or response.text or f"HTTP {response.status_code}"
        raise BackendAPIError(f"API request failed ({response.status_code}): {message}")

    return payload


def get_farm(farm_id):
    return _request("GET", f"/farms/{farm_id}")


def get_farm_location(farm_id):
    return _request("GET", f"/farms/{farm_id}/location")


def collect_farm_features(farm_id, cycle_id, observation_date):
    return _request(
        "GET",
        f"/farms/{farm_id}/cycles/{cycle_id}/features",
        params={"observation_date": observation_date.isoformat()},
    )


def create_prediction(farm_id, cycle_id):
    return _request(
        "POST",
        f"/predictions/farms/{farm_id}/cycles/{cycle_id}/predict",
    )


def get_farm_predictions(farm_id):
    return _request("GET", f"/predictions/farms/{farm_id}/predictions")


def remember_farm(farm, location=None):
    st.session_state["farm"] = farm
    st.session_state["farm_id"] = farm["farm_id"]
    if location is not None:
        st.session_state["farm_location"] = location
