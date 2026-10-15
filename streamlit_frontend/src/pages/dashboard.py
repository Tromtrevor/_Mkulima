from datetime import date

import streamlit as st

from src.components.metrics import render_metric_cards
from src.services.api import (
    BackendAPIError,
    get_farm,
    get_farm_location,
    get_farm_predictions,
    remember_farm,
)

st.markdown(
    """
    <section class="mkulima-hero">
      <span class="mkulima-hero-kicker">Precision agriculture</span>
      <h1>Better farm data. Smarter decisions.</h1>
      <p>Explore farm conditions, collect environmental and soil features, and
      generate maize yield estimates using your farm's geospatial data.</p>
    </section>
    """,
    unsafe_allow_html=True,
)
st.write("")

with st.container(border=True):
    st.subheader("Open your farm workspace")
    with st.form("load_farm_form"):
        farm_id = st.number_input(
            "Farm ID",
            min_value=1,
            step=1,
            value=int(st.session_state.get("farm_id", 1)),
        )
        submitted = st.form_submit_button("Load farm")

    if submitted:
        try:
            farm = get_farm(int(farm_id))
            try:
                location = get_farm_location(int(farm_id))
            except BackendAPIError:
                location = None
            remember_farm(farm, location)
            try:
                history_data = get_farm_predictions(int(farm_id))
                st.session_state["prediction_history"] = (history_data or {}).get(
                    "predictions", []
                )
            except BackendAPIError:
                st.session_state["prediction_history"] = []
                st.success(f"Loaded {(farm or {}).get('farm_name') or f'Farm {farm_id}'}.")
        except BackendAPIError as exc:
            st.error(str(exc))

farm = st.session_state.get("farm")
if farm:
    st.write("")
    st.subheader(farm.get("farm_name") or f"Farm {farm['farm_id']}")
    location = st.session_state.get("farm_location") or {}
    render_metric_cards(
        [
            ("Farm ID", farm.get("farm_id", "—"), "Farm record identifier"),
            (
                "Farm area",
                f"{farm['area_ha']} ha" if farm.get("area_ha") is not None else "—",
                "Registered area",
            ),
            (
                "Latitude",
                f"{location['latitude']:.5f}"
                if location.get("latitude") is not None
                else "—",
                "Farm centroid",
            ),
            (
                "Longitude",
                f"{location['longitude']:.5f}"
                if location.get("longitude") is not None
                else "—",
                "Farm centroid",
            ),
        ]
    )

features = st.session_state.get("farm_features")
prediction = st.session_state.get("latest_prediction")
if farm:
    st.write("")
    st.subheader("Latest farm insights")
    feature_values = [
        (
            "Rainfall",
            f"{features['weather'].get('rainfall_mm')} mm"
            if features and features.get("weather", {}).get("rainfall_mm") is not None
            else "—",
            "Weather collected for the crop cycle",
        ),
        (
            "Mean NDVI",
            features.get("ndvi", {}).get("mean", "—") if features else "—",
            "Satellite vegetation indicator",
        ),
        (
            "Soil pH",
            features.get("soil", {}).get("pH", "—") if features else "—",
            "Soil acidity measurement",
        ),
        (
            "Predicted yield",
            (
                f"{prediction.get('predicted_yield')} {prediction.get('unit') or 'kg/ha'}"
                if prediction and prediction.get("predicted_yield") is not None
                else "Not predicted"
            ),
            "Most recent model estimate",
        ),
    ]
    render_metric_cards(feature_values)

    if features:
        observed = features.get("observation_date")
        st.caption(
            f"Features last collected for crop cycle {features.get('cycle_id', '—')}"
            + (f" on {str(observed)[:10]}." if observed else ".")
        )
    else:
        st.info(
            "No feature set is loaded in this session. Open Farm analysis to "
            "collect weather, satellite, soil, and elevation data."
        )

    st.write("")
    st.subheader("Recent predictions")
    history = st.session_state.get("prediction_history", [])
    if history:
        st.dataframe(
            [
                {
                    "Prediction": item.get("prediction_id"),
                    "Crop cycle": item.get("cycle_id"),
                    "Yield": item.get("predicted_yield"),
                    "Model": item.get("model_version"),
                    "Date": str(item.get("prediction_date", ""))[:10],
                }
                for item in history[:5]
            ],
            use_container_width=True,
            hide_index=True,
        )
    else:
        st.caption("No saved predictions have been loaded for this farm.")
else:
    st.write("")
    st.info(
        "Enter a farm ID above to load registered farm details. You can find "
        "farm and crop cycle IDs in your Mkulima database."
    )

st.caption(f"Observation date default: {date.today().isoformat()}")
