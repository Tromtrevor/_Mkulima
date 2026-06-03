import streamlit as st
import joblib
import pandas as pd
from datetime import datetime, date


#-----------------------
#Load Model
# -----------------------
@st.cache_resource
def load_model():
    model = joblib.load('../models/maize_model.pkl')
    return model
        
model = load_model()


st.title('🌾 Crop Yield Prediction')
    
st.markdown('''
Enter your location and farm size to get best crop recommendation:
'''
)
# -----------------------
# Input Section
# -----------------------
st.header('Input Parameters')
    
    
col1, col2 = st.columns(2)
    
year = datetime.now().year
    
with col1:
    location = st.selectbox('Select County', counties)
    with st.form('crop'):
        farm_size = st.number_input('Farm Size (Acres)', 0.0)

    