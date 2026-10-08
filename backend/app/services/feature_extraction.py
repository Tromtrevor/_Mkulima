import pandas as pd


def extract_weather_features(weather_data: dict) -> dict:
    parameters = weather_data["properties"]["parameter"]
    #Generate panda series for each parameter to facilitate calculations
    rainfall = pd.Series(
        parameters["PRECTOTCORR"],
        dtype="float64"
    )

    temperature = pd.Series(
        parameters["T2M"],
        dtype="float64"
    )

    temperature_max = pd.Series(
        parameters["T2M_MAX"],
        dtype="float64"
    )

    temperature_min = pd.Series(
        parameters["T2M_MIN"],
        dtype="float64"
    )

    # Replace NASA POWER's -999 values with pandas NA for proper handling
    rainfall = rainfall.replace(-999, pd.NA)
    temperature = temperature.replace(-999, pd.NA)
    temperature_max = temperature_max.replace(-999, pd.NA)
    temperature_min = temperature_min.replace(-999, pd.NA)

    return {
        "rainfall_mm": rainfall.sum(),
        "temperature_mean_c": temperature.mean(),
        "temperature_max_c": temperature_max.max(),
        "temperature_min_c": temperature_min.min()
    }