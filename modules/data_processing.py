import pandas as pd

def process_weather_data(weather_data):
    try:
        forecasts = weather_data["list"]
        processed_data = pd.DataFrame([{
            "datetime": forecast["dt_txt"],
            "temperature": forecast["main"]["temp"],
            "precipitation_probability": forecast.get("pop", 0) * 100,
            "wind_speed": forecast["wind"]["speed"],
            "weather": forecast["weather"][0]["description"]
        } for forecast in forecasts])
        return processed_data
    except KeyError:
        return pd.DataFrame()