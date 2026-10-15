import streamlit as st


def render_metric_cards(items):
    columns = st.columns(len(items))
    for column, (label, value, help_text) in zip(columns, items):
        with column:
            st.metric(label=label, value=value, help=help_text)


def render_data_panel(title, values):
    st.subheader(title)
    if not values:
        st.info("No data available yet.")
        return

    for label, value in values.items():
        if isinstance(value, dict):
            with st.expander(label.replace("_", " ").title(), expanded=True):
                render_data_panel("", value)
        else:
            display_value = "—" if value is None else value
            st.text(f"{label.replace('_', ' ').title()}: {display_value}")
