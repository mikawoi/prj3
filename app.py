from flask import Flask, render_template, request
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
from modules.weather_api import get_weather_forecast
from modules.data_processing import process_weather_data
from modules.visualization import create_weather_graph

# Flask приложение
app = Flask(__name__)

# Dash приложение
dash_app = dash.Dash(
    __name__,
    server=app,
    url_base_pathname="/dash/"
)

# Глобальные переменные для хранения данных
processed_data = pd.DataFrame()


# Главная страница Flask
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/weather", methods=["POST"])
def weather():
    global processed_data
    lat = request.form.get("latitude")
    lon = request.form.get("longitude")

    # Получение и обработка данных
    weather_data = get_weather_forecast(lat, lon)
    if "error" in weather_data:
        return render_template("index.html", message="Ошибка получения данных.")

    processed_data = process_weather_data(weather_data)
    return render_template("dash.html")


# Dash приложение: отображение графиков
dash_app.layout = html.Div([
    html.H1("Прогноз погоды", style={"textAlign": "center"}),
    dcc.Dropdown(
        id="parameter-dropdown",
        options=[
            {"label": "Температура (°C)", "value": "temperature"},
            {"label": "Скорость ветра (м/с)", "value": "wind_speed"},
            {"label": "Вероятность осадков (%)", "value": "precipitation_probability"}
        ],
        value="temperature",
        clearable=False,
        style={"width": "50%", "margin": "auto"}
    ),
    dcc.Graph(id="weather-graph")
])


@dash_app.callback(
    Output("weather-graph", "figure"),
    [Input("parameter-dropdown", "value")]
)
def update_graph(selected_parameter):
    """Обновление графика на основе выбранного параметра."""
    titles = {
        "temperature": "Прогноз температуры",
        "wind_speed": "Скорость ветра",
        "precipitation_probability": "Вероятность осадков"
    }
    y_labels = {
        "temperature": "Температура (°C)",
        "wind_speed": "Скорость ветра (м/с)",
        "precipitation_probability": "Вероятность осадков (%)"
    }
    return create_weather_graph(
        processed_data,
        y_column=selected_parameter,
        title=titles[selected_parameter],
        y_label=y_labels[selected_parameter]
    )


if __name__ == "__main__":
    app.run(debug=True)
