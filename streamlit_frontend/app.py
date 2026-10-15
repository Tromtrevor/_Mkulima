import streamlit as st

from src.components.layout import apply_app_style, render_brand

st.set_page_config(
    page_title="Mkulima | Farm intelligence",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_app_style()
render_brand()

pages = [
    st.Page(
        "src/pages/dashboard.py",
        title="Dashboard",
        icon=":material/dashboard:",
        default=True,
    ),
    st.Page(
        "src/pages/farm_analysis.py",
        title="Farm analysis",
        icon=":material/map:",
    ),
    st.Page(
        "src/pages/predictions.py",
        title="Yield predictions",
        icon=":material/show_chart:",
    ),
]

navigation = st.navigation(pages, position="sidebar")
navigation.run()
