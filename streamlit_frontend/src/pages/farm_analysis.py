from datetime import date

import streamlit as st

from src.components.metrics import render_data_panel, render_metric_cards
from src.services.api import (
    BackendAPIError,
    collect_farm_features,
    get_farm,
    get_farm_location,
    remember_farm,
)

st.title("Farm analysis")
st.caption("Collect current weather, satellite vegetation, soil, and elevation data.")

with st.form("farm_analysis_form"):
    col_farm, col_cycle = st.columns(2)
    with col_farm:
        farm_id = st.number_input(
            "Farm ID",
            min_value=1,
            step=1,
            value=int(st.session_state.get("farm_id", 1)),
        )
    with col_cycle:
        cycle_id = st.number_input(
            "Crop cycle ID",
            min_value=1,
            step=1,
            value=int(st.session_state.get("cycle_id", 1)),
        )
    observation_date = st.date_input(
        "Observation date",
        value=date.today(),
        max_value=date.today(),
        help="Must fall on or after the selected crop cycle's planting date.",
    )
    submitted = st.form_submit_button("Collect farm features")

if submitted:
    try:
        farm = get_farm(int(farm_id))
        try:
            location = get_farm_location(int(farm_id))
        except BackendAPIError:
            location = None
        features = collect_farm_features(
            int(farm_id), int(cycle_id), observation_date
        )
        remember_farm(farm, location)
        st.session_state["cycle_id"] = int(cycle_id)
        st.session_state["farm_features"] = features
        st.session_state.pop("latest_prediction", None)
        st.success("Farm features collected and saved.")
    except BackendAPIError as exc:
        st.error(str(exc))

features = st.session_state.get("farm_features")
if features:
    st.write("")
    weather = features.get("weather", {})
    ndvi = features.get("ndvi", {})
    soil = features.get("soil", {})
    elevation = features.get("elevation", {})

    render_metric_cards(
        [
            (
                "Rainfall",
                f"{weather.get('rainfall_mm')} mm"
                if weather.get("rainfall_mm") is not None
                else "—",
                "Weather data for the crop cycle",
            ),
            (
                "Mean NDVI",
                ndvi.get("mean", "—"),
                "Satellite vegetation index",
            ),
            ("Soil pH", soil.get("pH", "—"), "Soil acidity"),
            (
                "Elevation",
                f"{elevation.get('elevation_m')} m"
                if elevation.get("elevation_m") is not None
                else "—",
                "Farm elevation",
            ),
        ]
    )

    st.caption(
        f"Farm {features.get('farm_id')} · Crop cycle {features.get('cycle_id')} · "
        f"Observed {str(features.get('observation_date', ''))[:10]}"
    )
    left, right = st.columns(2)
    with left:
        render_data_panel("Weather", weather)
        render_data_panel("Vegetation (NDVI)", ndvi)
    with right:
        render_data_panel("Soil characteristics", soil)
        render_data_panel("Elevation", elevation)
