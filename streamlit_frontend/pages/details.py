import streamlit as st
import pandas as pd

# API Configuration
API_BASE_URL = st.session_state.get("api_base_url", "http://localhost:8000")

# Get crop and input data from session state
crop = st.session_state.get('best_crop', '')
input_data_dict = st.session_state.get('input_data', {})

if not crop:
    st.error("No crop prediction found. Please run a crop recommendation first.")
else:
    # Load crop suitability data
    df = pd.read_csv('./data/predictor/kenya_crop_suitability.csv')
    data = df[df['crop_name'].str.lower() == crop.lower()].reset_index()

    if data.empty:
        st.error(f"No suitability data found for {crop}")
    else:
        # Extract temperature, altitude, rainfall, pH from input data
        temp = (input_data_dict.get('mean Tmin', 0) + input_data_dict.get('mean Tmax', 0)) / 2
        altitude = input_data_dict.get('meanElev', 0)
        rainfall = input_data_dict.get('Precipitation', 0)
        ph = input_data_dict.get('pH', 0)
        county = input_data_dict.get('County', '')

        st.write(f'''
            ## {crop.capitalize()}\n

            ''')

        col1, col2, col3 = st.columns(3)

        with col1:
            st.write(f'''
                ***Temperature*** : {data.at[0, 'temperature_min']} - {data.at[0, 'temperature_max']} °C\n
                ***Altitude*** : {data.at[0, 'altitude_min']} - {data.at[0, 'altitude_max']} m
                ''')
        with col2:
            st.write(f'''
                ***Rainfall*** : {data.at[0, 'rainfall_min']} - {data.at[0, 'rainfall_max']} mm\n
                ***pH Range*** : {data.at[0, 'ph_min']} - {data.at[0, 'ph_max']}
                ''')
        with col3:
            if st.button("NEARBY AGRI-SERVICES"):
                st.switch_page("pages/agriservices_map.py")
        
        st.write(f'''
            ### Satisfied conditions by {county.capitalize()}
            ''')

        # Check altitude suitability
        if altitude < data.at[0, 'altitude_max'] and altitude > data.at[0, 'altitude_min']:
            st.write(f'''
                \nAltitude ✓\n
                {altitude:.2f} m falls within {data.at[0, 'altitude_min']} - {data.at[0, 'altitude_max']} m
                ''')
        else:
            st.write(f'''
                \nAltitude ✗\n
                {altitude:.2f} m is outside {data.at[0, 'altitude_min']} - {data.at[0, 'altitude_max']} m range
                ''')

        # Check rainfall suitability
        if rainfall < data.at[0, 'rainfall_max'] and rainfall > data.at[0, 'rainfall_min']:
            st.write(f'''
                \nRainfall ✓\n
                {rainfall:.2f} mm falls within {data.at[0, 'rainfall_min']} - {data.at[0, 'rainfall_max']} mm
                ''')
        else:
            st.write(f'''
                \nRainfall ✗\n
                {rainfall:.2f} mm is outside {data.at[0, 'rainfall_min']} - {data.at[0, 'rainfall_max']} mm range
                ''')

        # Check pH suitability
        if ph < data.at[0, 'ph_max'] and ph > data.at[0, 'ph_min']:
            st.write(f'''
                \npH Level ✓\n
                {ph:.2f} falls within {data.at[0, 'ph_min']} - {data.at[0, 'ph_max']} range
                ''')
        else:
            st.write(f'''
                \npH Level ✗\n
                {ph:.2f} is outside {data.at[0, 'ph_min']} - {data.at[0, 'ph_max']} range
                ''')


if temp < data.at[0, 'temperature_max'] and temp > data.at[0, 'temperature_min']:
	st.write(f'''
		\nTemperature\n 
		{temp:.2f} °C falls within {data.at[0, 'temperature_min']} - {data.at[0, 'temperature_max']} °C
		''')

if rainfall < data.at[0, 'rainfall_max'] and rainfall > data.at[0, 'rainfall_min']:
	st.write(f'''
		\nPrecipitation\n 
		{rainfall:.2f} mm falls within {data.at[0, 'rainfall_min']} - {data.at[0, 'rainfall_max']} mm
		''')

if ph < data.at[0, 'ph_max'] and ph > data.at[0, 'ph_min']:
	st.write(f'''
		\nsoil pH\n 
		{ph:.2f} falls within {data.at[0, 'ph_min']} - {data.at[0, 'ph_max']} 
		''')