import geopandas as gpd
import requests
import json
import pandas as pd
from shapely.geometry import mapping
from datetime import datetime, timedelta
from pathlib import Path

# --- PATHS ---
API_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc2MDEyMjI1MiwianRpIjoiMzEwNGJiMGQtYmVjMi00ZDYzLWJiM2MtMjQxMzZlNjBkNTIxIiwibmJmIjoxNzYwMTIyMjUyLCJ0eXBlIjoiYWNjZXNzIiwic3ViIjoiWTMxMXJuRGtYc1VhOUJicFFHdFBzZkJzeG1BMyIsImV4cCI6MTc2NTMwNjI1Miwicm9sZXMiOiJ1c2VyIiwidXNlcl9pZCI6IlkzMTFybkRrWHNVYTlCYnBRR3RQc2ZCc3htQTMifQ.yJChfnVBg0yMqhc-R9Ue7_hbUGGGYJbjo1K7Z5NNeOk"
BASE_URL = "https://api.climateengine.org"

current_dir = Path(__file__).resolve().parent

pH = current_dir.parent / "data" / "pH" / "Kenya_counties_pH.csv"
elevation = current_dir.parent / "data"/ "elevation" / "kenya_mean_elevation.csv"
SHAPEFILE_PATH = current_dir.parent / "data" / "counties" / "counties.shp"
yield_dataset = current_dir.parent / "data" / "predictor" / f"Yield Predicting Dataset {datetime.now().strftime('%Y-%m-%d')}.csv"
backup = current_dir.parent / "data" / "predictor" / "backup_means.csv"
    
data_var = {
    'ERA5': [
        {'variable':["minimum_2m_air_temperature","maximum_2m_air_temperature","peth","total_precipitation"], 'statistic': "mean"}
    ],
    'SENTINEL2_TOA': [
        {'variable':['NDVI'], 'statistic': "mean"},
        {'variable':['NDVI'], 'statistic': "max"}
    ]
}
def fetch_realtime_data(COUNTY_NAME):
    # --- DATE RANGE ---
    end_date = datetime.today()
    start_date = end_date - timedelta(days=31)
    START_DATE = start_date.strftime("%Y-%m-%d")
    END_DATE = end_date.strftime("%Y-%m-%d")
    
    
    gdf = gpd.read_file(SHAPEFILE_PATH)
    backup_data = pd.read_csv(backup)
    
    selected = gdf[gdf['county'].str.lower().replace(' ','').replace('-','') == COUNTY_NAME.lower().replace(' ','').replace('-','')]
    backup_county = backup_data[backup_data['County'].str.lower().replace([' ','-'],'')==COUNTY_NAME.lower().replace(' ','').replace('-','')]
    
    if selected.empty:
        print(f"❌ County '{COUNTY_NAME}' not found in shapefile.")
    else:
        row = selected.geometry.iloc[0]
        simplified_row = row.simplify(tolerance=0.035, preserve_topology=True)
        geometry_dict = mapping(simplified_row)
        coordinates = geometry_dict['coordinates']
        coords = json.dumps(coordinates)
    
        headers = {"Authorization": API_TOKEN}
        print(f"⏳ Downloading data for {COUNTY_NAME}...")
        url = f'{BASE_URL}/timeseries/native/coordinates'
        predictors = pd.DataFrame()
        
                
        for dataset, var_dict in data_var.items():
            for item in var_dict:
                statistic = item['statistic']
                for var in item['variable']:    
                    params = {
                        "coordinates": coords,
                        "area_reducer": statistic,
                        "dataset": dataset,
                        "variable": var,
                        "start_date": START_DATE,
                        "end_date": END_DATE,  
                        }
    
                    if dataset !='SENTINEL2_TOA':
                        var = var
                    else:
                        var = var + f"_{statistic}"
                    print(f'Requesting {dataset} for {var}')
                    response = requests.get(url, params=params, headers=headers)
    
                    if response.status_code == 200:
                        res = response.json().get('Data',[])
                        data = res[0]['Data']
                        if data:             
                           df = pd.DataFrame(data)
                           df = df.rename(columns={col: f'{var}' for col in df.columns if col != 'Date'}) 
                           if predictors.empty:
                               predictors = df             
                           else:
                               predictors = pd.merge(
                               left= predictors,
                               right= df,
                               on= 'Date',
                               how= 'outer'
                               )
                           print(f'✔ {var}')
                        else:
                            print(f"⚠ No data found for {var}")
                            predictors[var] = backup_county[var].values[0]
                    else:
                        print(f"❌ Error {response.status_code}: {response.text}...Using backup data for {var}")
                        predictors[var] = backup_county[var].values[0]
                        
    predict=predictors[predictors['NDVI_mean'] !=-9999]
    predict.set_index('Date', inplace=True)
    
    predict_data = {}
    
    for col in predict.columns:
        
        if col != 'total_precipitation':
            value = predict[col].mean()
        elif col == 'total_precipitation':
            filtered = backup_data[backup_data['County'] == COUNTY_NAME].reset_index()
            value = filtered.at[0, 'Precipitation']
        predict_data[col] = value
    
        predict_df = pd.DataFrame([predict_data])
    
    predict_df['Temp_range'] = predict_df['maximum_2m_air_temperature']-predict_df['minimum_2m_air_temperature']
    predict_df['County'] = COUNTY_NAME
    
    elev = pd.read_csv(elevation)
    
    full_predict_data  = pd.merge(
        left= predict_df,
        right= elev,
        left_on= 'County',
        right_on= 'county',
        how= 'left'
    )

    ph = pd.read_csv(pH)
    ph.drop(columns = ['system:index', '.geo'], axis=1, inplace=True)

    full_predict_data  = pd.merge(
        left= full_predict_data,
        right= ph,
        left_on= 'county',
        right_on= 'county',
        how= 'left'
        )
   
    full_predict_data.drop('county',axis=1, inplace=True)

    full_predict_data.columns = ['mean Tmin','mean Tmax','Hargreaves PET','Precipitation','Mean NDVI','Max NDVI','Temp_range','County','meanElev','pH']
    full_predict_data = full_predict_data[['County','meanElev','pH','Max NDVI', 'Mean NDVI', 'mean Tmax', 'mean Tmin', 'Hargreaves PET', 'Precipitation','Temp_range']]
    
    try:
        pd.read_csv(yield_dataset)
        full_predict_data.to_csv(yield_dataset, mode='a', header=False, index=False)
    except FileNotFoundError:
        full_predict_data.to_csv(yield_dataset, mode='w', header=True, index=False)
    
    return full_predict_data