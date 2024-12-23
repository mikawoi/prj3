import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/forecast"

def get_weather_forecast(lat, lon):
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": "metric",
        "lang": "ru",
    }
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

def get_coordinates(location):
    """
    Получение координат (широта и долгота) по названию местоположения.
    """
    params = {
        "q": location,
        "appid": API_KEY
    }
    try:
        response = requests.get("http://api.openweathermap.org/geo/1.0/direct", params=params)
        response.raise_for_status()
        data = response.json()
        if data:
            return data[0]["lat"], data[0]["lon"]
        else:
            return "error", f"Местоположение '{location}' не найдено."
    except requests.RequestException as e:
        return "error", str(e)