from flask import Flask, render_template, request
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
from modules.weather_api import get_weather_forecast
from modules.data_processing import process_weather_data
import plotly.express as px

app = Flask(__name__)

dash_app = dash.Dash(
    __name__,
    server=app,
    url_base_pathname="/dash/"
)

processed_data = pd.DataFrame()

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/weather", methods=["POST"])
def weather():
    global processed_data, route_points

    processed_data = pd.DataFrame()

    lat = request.form.get("latitude")
    lon = request.form.get("longitude")

    if not lat or not lon:
        return render_template("index.html", message="Введите корректные координаты.")

    try:
        lat = float(lat)
        lon = float(lon)
    except ValueError:
        return render_template("index.html", message="Введите числовые координаты.")

    new_point = {"lat": lat, "lon": lon}
    if new_point not in route_points:
        route_points.append(new_point)

    # Получение и обработка данных
    weather_data = get_weather_forecast(lat, lon)
    if "error" in weather_data:
        return render_template("index.html", message="Ошибка получения данных от API.")

    processed_data = process_weather_data(weather_data)
    if processed_data.empty:
        return render_template("index.html", message="Нет данных для построения графика.")

    return render_template("dash.html")



route_points = []

dash_app.layout = html.Div([
    html.H1("Прогноз погоды", style={"textAlign": "center"}),

    html.Div([
        dcc.Input(id="latitude-input", type="number", placeholder="Широта", style={"marginRight": "10px"}),
        dcc.Input(id="longitude-input", type="number", placeholder="Долгота", style={"marginRight": "10px"}),
        html.Button("Добавить точку", id="add-point-btn", n_clicks=0, style={"marginRight": "10px"}),
        dcc.Dropdown(
            id="route-points-dropdown",
            options=[],
            placeholder="Выберите существующую точку",
            style={"width": "40%", "display": "inline-block"}
        )
    ], style={"textAlign": "center", "marginBottom": "20px"}),

    # Dropdown для параметра и график
    dcc.Dropdown(
        id="parameter-dropdown",
        options=[
            {"label": "Температура (°C)", "value": "temperature"},
            {"label": "Скорость ветра (м/с)", "value": "wind_speed"},
            {"label": "Вероятность осадков (%)", "value": "precipitation_probability"}
        ],
        value="temperature",
        clearable=False,
        style={"width": "50%", "margin": "auto", "marginBottom": "20px"}
    ),
    dcc.Graph(id="weather-graph")
])


@dash_app.callback(
    [Output("weather-graph", "figure"),
     Output("route-points-dropdown", "options")],
    [Input("add-point-btn", "n_clicks"),
     Input("parameter-dropdown", "value")],
    [State("latitude-input", "value"),
     State("longitude-input", "value"),
     State("route-points-dropdown", "value")]
)
def update_route_graph(n_clicks, selected_param, lat, lon, selected_point):
    global route_points, processed_data

    if n_clicks > 0 and lat is not None and lon is not None:
        new_point = {"lat": lat, "lon": lon}
        if new_point not in route_points:
            route_points.append(new_point)

    dropdown_options = [
        {"label": f"Точка {i + 1}: ({pt['lat']}, {pt['lon']})", "value": i}
        for i, pt in enumerate(route_points)
    ]

    # Получение данных погоды для всех точек
    all_data = []
    if not processed_data.empty:
        processed_data["route_point"] = f"Точка {len(route_points)}"
        all_data.append(processed_data)

    for i, point in enumerate(route_points[:-1]):
        weather_data = get_weather_forecast(point["lat"], point["lon"])
        point_data = process_weather_data(weather_data)
        if not point_data.empty:
            point_data["route_point"] = f"Точка {i + 1}"
            all_data.append(point_data)

    # Создание графика
    if all_data:
        combined_data = pd.concat(all_data)
        fig = px.line(
            combined_data,
            x="datetime",
            y=selected_param,
            color="route_point",
            title="Прогноз погоды для маршрута"
        )
        fig.update_layout(
            xaxis_title="Дата и время",
            yaxis_title={
                "temperature": "Температура (°C)",
                "wind_speed": "Скорость ветра (м/с)",
                "precipitation_probability": "Вероятность осадков (%)"
            }.get(selected_param, ""),
            template="plotly_white"
        )
    else:
        fig = px.line(title="Нет данных для отображения")

    return fig, dropdown_options


if __name__ == "__main__":
    app.run(debug=True)
