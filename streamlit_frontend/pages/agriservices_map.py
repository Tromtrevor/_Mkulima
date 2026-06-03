import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# API Configuration
API_BASE_URL = st.session_state.get("api_base_url", "http://localhost:8000")

county_name = st.session_state.get('location', '')
st.title(f"AgroServices in {county_name.capitalize()}")

if not county_name:
    st.warning("No location selected. Please go back to crop recommendation.")
else:
    try:
        # Fetch agroservices from API
        response = requests.get(
            f"{API_BASE_URL}/api/agroservices",
            params={"county": county_name}
        )
        
        if response.status_code == 200:
            services_data = response.json().get("data", [])
            
            if not services_data:
                st.warning("No agrovets found for this county.")
            else:
                # Convert to DataFrame
                county_data = pd.DataFrame(services_data)
                
                # Check if required columns exist
                if "latitude" in county_data.columns and "longitude" in county_data.columns:
                    fig = px.scatter_map(
                        county_data,
                        lat="latitude",
                        lon="longitude",
                        hover_name="name",
                        hover_data=["category"] if "category" in county_data.columns else [],
                        color="category" if "category" in county_data.columns else None,
                        zoom=9,
                        height=500,
                        size_max=20,
                    )

                    fig.update_layout(
                        mapbox_style="open-street-map",
                        margin={"r":0,"t":0,"l":0,"b":0}
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Agroservices data available but map display not available")
                    st.dataframe(county_data)
        else:
            st.error(f"Failed to fetch agroservices: {response.json().get('detail', 'Unknown error')}")
            
    except Exception as e:
        st.error(f"Connection error: {str(e)}")
