import plotly.express as px


def create_weather_graph(data, y_column, title, y_label):
    fig = px.line(data, x="datetime", y=y_column, title=title)
    fig.update_layout(
        xaxis_title="Дата и время",
        yaxis_title=y_label,
        template="plotly_dark"
    )
    return fig
