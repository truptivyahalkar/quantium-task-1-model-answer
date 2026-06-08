import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html

# Load and prepare data
df = pd.read_csv("pink_morsels_sales.csv")
df["date"] = pd.to_datetime(df["date"])

# Aggregate total sales per day across all regions
daily_sales = df.groupby("date")["sales"].sum().reset_index()
daily_sales = daily_sales.sort_values("date")

PRICE_INCREASE_DATE = "2021-01-15"

# Split into before/after price increase
before = daily_sales[daily_sales["date"] < PRICE_INCREASE_DATE]
after = daily_sales[daily_sales["date"] >= PRICE_INCREASE_DATE]

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=before["date"],
    y=before["sales"],
    mode="lines",
    name="Before Price Increase",
    line=dict(color="#f4a261", width=1.5),
))

fig.add_trace(go.Scatter(
    x=after["date"],
    y=after["sales"],
    mode="lines",
    name="After Price Increase",
    line=dict(color="#e76f51", width=1.5),
))

fig.add_vline(
    x=PRICE_INCREASE_DATE,
    line_dash="dash",
    line_color="#264653",
    line_width=2,
    annotation_text="Price Increase (Jan 15, 2021)",
    annotation_position="top left",
    annotation_font=dict(color="#264653", size=12),
)

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Total Sales (All Regions)",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    plot_bgcolor="white",
    paper_bgcolor="white",
    hovermode="x unified",
    margin=dict(l=60, r=30, t=40, b=60),
    xaxis=dict(showgrid=True, gridcolor="#eeeeee"),
    yaxis=dict(showgrid=True, gridcolor="#eeeeee"),
)

app = Dash(__name__)

app.layout = html.Div(
    style={"fontFamily": "Arial, sans-serif", "maxWidth": "1100px", "margin": "0 auto", "padding": "24px"},
    children=[
        html.H1(
            "Pink Morsels — Daily Sales Visualiser",
            style={"textAlign": "center", "color": "#264653", "marginBottom": "4px"},
        ),
        html.P(
            "Comparing total daily sales across all regions before and after the price increase on 15 January 2021",
            style={"textAlign": "center", "color": "#6c757d", "marginBottom": "24px"},
        ),
        dcc.Graph(figure=fig, style={"height": "520px"}),
    ],
)

if __name__ == "__main__":
    app.run(debug=True)
