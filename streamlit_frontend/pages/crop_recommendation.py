import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# API Configuration
API_BASE_URL = st.session_state.get("api_base_url", "http://localhost:8000")

st.title('🌾 Crop Yield Prediction')

st.markdown('''
Enter your location and farm size to get best crop recommendation:
''')

# -----------------------
# Input Section
# -----------------------
st.header('Input Parameters')

col1, col2 = st.columns(2)

# Fetch counties from backend
try:
    counties_response = requests.get(f"{API_BASE_URL}/api/counties")
    if counties_response.status_code == 200:
        counties = counties_response.json().get("counties", [])
    else:
        st.error("Failed to fetch counties from backend")
        counties = []
except Exception as e:
    st.error(f"Connection error: {e}")
    counties = []

with col1:
    location = st.selectbox('Farm Location (County)', counties)
    
with col2:
    farm_size = st.number_input('Farm Size (Acres)', min_value=0.1, value=1.0)

st.session_state['location'] = location
st.session_state['farm_size'] = farm_size

# -----------------------
# Prediction Section
# -----------------------
if st.button('🔮 Predict Yield'):
    if not location:
        st.error("Please select a location")
    elif farm_size <= 0:
        st.error("Farm size must be greater than 0")
    else:
        with st.spinner('Predicting...'):
            try:
                # Call predict-yield endpoint
                predict_response = requests.post(
                    f"{API_BASE_URL}/api/crop/predict-yield",
                    json={"county": location, "farm_size": farm_size}
                )
                
                if predict_response.status_code == 200:
                    predictions_data = predict_response.json().get("data", {})
                    
                    predictions = predictions_data.get("predictions", {})
                    input_data = predictions_data.get("input_data", {})
                    
                    # Find best crop by default profit
                    best_crop = None
                    max_profit = float('-inf')
                    best_profit_data = None
                    
                    for crop_name in predictions.keys():
                        # Calculate default profit for each crop
                        profit_response = requests.post(
                            f"{API_BASE_URL}/api/crop/calculate-default-profit",
                            json={"crop_name": crop_name}
                        )
                        
                        if profit_response.status_code == 200:
                            profit_data = profit_response.json()
                            profit = float(profit_data.get("profit", {}).get("total_profit", 0))
                            
                            if profit > max_profit:
                                max_profit = profit
                                best_crop = crop_name
                                best_profit_data = profit_data
                    
                    if best_profit_data:
                        # Store results in session state for results page
                        st.session_state['best_crop'] = best_crop
                        st.session_state['total_yield'] = best_profit_data.get("profit", {}).get("total_yield", 0)
                        st.session_state['total_revenue'] = best_profit_data.get("profit", {}).get("total_revenue", 0)
                        st.session_state['total_cost'] = best_profit_data.get("profit", {}).get("total_cost", 0)
                        st.session_state['profit'] = best_profit_data.get("profit", {}).get("total_profit", 0)
                        st.session_state['profit_margin'] = best_profit_data.get("profit_margin", 0)
                        st.session_state['predictions'] = predictions
                        st.session_state['input_data'] = input_data
                        st.session_state['all_profits'] = {}
                        
                        # Store profit data for all crops
                        for crop_name in predictions.keys():
                            profit_response = requests.post(
                                f"{API_BASE_URL}/api/crop/calculate-default-profit",
                                json={"crop_name": crop_name}
                            )
                            if profit_response.status_code == 200:
                                st.session_state['all_profits'][crop_name] = profit_response.json()
                        
                        st.success(f"Prediction successful! Best crop: {best_crop}")
                        st.switch_page('pages/results.py')
                    else:
                        st.error("Failed to calculate profit for crops")
                else:
                    st.error(f"Prediction failed: {predict_response.json().get('detail', 'Unknown error')}")
                    
            except Exception as e:
                st.error(f'Prediction failed: {str(e)}')
