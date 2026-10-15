import streamlit as st

from src.components.metrics import render_metric_cards
from src.services.api import (
    BackendAPIError,
    create_prediction,
    get_farm_predictions,
)

st.title("Yield predictions")
st.caption("Generate and review maize yield estimates for a farm crop cycle.")

with st.form("prediction_form"):
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
    submitted = st.form_submit_button("Generate yield prediction")

if submitted:
    try:
        prediction = create_prediction(int(farm_id), int(cycle_id))
        st.session_state["latest_prediction"] = prediction
        st.session_state["farm_id"] = int(farm_id)
        st.session_state["cycle_id"] = int(cycle_id)
        st.success("Yield prediction generated and saved.")
        try:
            history_data = get_farm_predictions(int(farm_id))
            st.session_state["prediction_history"] = history_data.get(
                "predictions", []
            )
        except BackendAPIError as exc:
            st.warning(f"Prediction saved, but history could not be refreshed: {exc}")
    except BackendAPIError as exc:
        st.error(str(exc))

prediction = st.session_state.get("latest_prediction")
if prediction:
    st.write("")
    yield_value = prediction.get("predicted_yield")
    render_metric_cards(
        [
            (
                "Estimated yield",
                f"{yield_value} {prediction.get('unit') or 'kg/ha'}"
                if yield_value is not None
                else "Unavailable",
                "Model estimate; actual harvest may differ",
            ),
            ("Prediction ID", prediction.get("prediction_id", "—"), "Saved result"),
            ("Crop cycle", prediction.get("cycle_id", "—"), "Crop cycle used"),
            ("Model version", prediction.get("model_version", "—"), "Model metadata"),
        ]
    )
    st.caption(
        "This is a model estimate, not a guaranteed harvest outcome. "
        "Accuracy depends on the quality and suitability of the collected inputs."
    )

st.write("")
st.subheader("Prediction history")
if st.button("Refresh history"):
    try:
        history_data = get_farm_predictions(int(st.session_state.get("farm_id", 1)))
        st.session_state["prediction_history"] = history_data.get(
            "predictions", []
        )
    except BackendAPIError as exc:
        st.error(str(exc))

history = st.session_state.get("prediction_history", [])
if history:
    st.dataframe(
        [
            {
                "Prediction ID": item.get("prediction_id"),
                "Crop cycle": item.get("cycle_id"),
                "Estimated yield": item.get("predicted_yield"),
                "Confidence": item.get("confidence"),
                "Model": item.get("model_version"),
                "Date": str(item.get("prediction_date", ""))[:10],
            }
            for item in history
        ],
        use_container_width=True,
        hide_index=True,
    )
else:
    st.info("No prediction history is loaded. Generate a prediction or refresh history.")
