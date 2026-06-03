
import streamlit as st
import requests

# API Configuration
API_BASE_URL = "http://localhost:8000"

# Store API base URL in session state for use in other pages
if "api_base_url" not in st.session_state:
    st.session_state.api_base_url = API_BASE_URL

st.sidebar.title('MKULIMA')
st.sidebar.page_link('app.py', label='Home')
st.sidebar.page_link('pages/crop_recommendation.py', label='Crop Recommendation')   
st.sidebar.page_link('pages/results.py', label = 'Results')

# -----------------------
# Page Setup
# -----------------------
st.set_page_config(page_title='MKULIMA', layout='centered')
st.title('MKULIMA')
    
st.markdown('''
Get optimum crop reccommendation based on yield prediction and soil data analysis along with available AgriServices across the country.
\nGet started with the best Agricultural Decisions!!

'''
)


if st.button('GET STARTED'):
    st.switch_page('pages/crop_recommendation.py')

