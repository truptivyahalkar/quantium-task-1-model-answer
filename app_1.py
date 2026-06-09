import pandas as pd
import plotly.graph_objects as go
from dash import Dash, dcc, html, Input, Output

# ── Data ──────────────────────────────────────────────────────────────────────
df = pd.read_csv("pink_morsels_sales.csv")
df["date"] = pd.to_datetime(df["date"])

PRICE_INCREASE = "2021-01-15"

REGION_COLOURS = {
    "north": "#f4a261",
    "south": "#e76f51",
    "east":  "#2a9d8f",
    "west":  "#e9c46a",
    "all":   "#a78bfa",
}

# ── App ───────────────────────────────────────────────────────────────────────
app = Dash(__name__)

app.layout = html.Div(id="app-shell", children=[

    html.Div(id="header", children=[
        html.H1("Pink Morsels Sales Dashboard"),
        html.P(
            "Daily sales across all regions · Dashed line marks the price increase on 15 January 2021"
        ),
    ]),

    html.Div(id="card", children=[

        html.Div(id="filter-row", children=[
            html.Span("Filter by region", id="filter-label"),
            dcc.RadioItems(
                id="region-radio",
                options=[
                    {"label": "All",   "value": "all"},
                    {"label": "North", "value": "north"},
                    {"label": "South", "value": "south"},
                    {"label": "East",  "value": "east"},
                    {"label": "West",  "value": "west"},
                ],
                value="all",
                inline=True,
                className="region-radio",
            ),
        ]),

        html.Div(id="chart-container", children=[
            dcc.Graph(id="sales-chart", style={"height": "480px"}),
        ]),
    ]),

    html.Div(id="footer-note",
             children="Soul Foods · Pink Morsels · Internal Analytics"),
])


# ── Callback ──────────────────────────────────────────────────────────────────
@app.callback(Output("sales-chart", "figure"), Input("region-radio", "value"))
def update_chart(region):
    if region == "all":
        daily = df.groupby("date")["sales"].sum().reset_index()
        label = "All Regions (combined)"
    else:
        daily = (
            df[df["region"] == region]
            .groupby("date")["sales"].sum().reset_index()
        )
        label = region.capitalize()

    daily = daily.sort_values("date")
    colour = REGION_COLOURS[region]

    before = daily[daily["date"] <  PRICE_INCREASE]
    after  = daily[daily["date"] >= PRICE_INCREASE]

    fig = go.Figure()

    # Before segment
    fig.add_trace(go.Scatter(
        x=before["date"], y=before["sales"],
        mode="lines", name=f"{label} — Before",
        line=dict(color=colour, width=2),
        fill="tozeroy",
        fillcolor=colour.replace(")", ", 0.08)").replace("rgb", "rgba")
                  if colour.startswith("rgb") else colour + "14",
    ))

    # After segment
    fig.add_trace(go.Scatter(
        x=after["date"], y=after["sales"],
        mode="lines", name=f"{label} — After",
        line=dict(color=colour, width=2, dash="solid"),
        fill="tozeroy",
        fillcolor=colour + "28",
    ))

    # Price-increase marker
    fig.add_vline(
        x=PRICE_INCREASE,
        line_dash="dash", line_color="#e2e8f0", line_width=1.5,
        annotation_text="Price increase · Jan 15 2021",
        annotation_position="top right",
        annotation_font=dict(color="#94a3b8", size=11),
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", color="#cbd5e1"),
        xaxis=dict(
            title="Date",
            showgrid=True, gridcolor="rgba(255,255,255,0.06)",
            zeroline=False, tickfont=dict(size=11),
        ),
        yaxis=dict(
            title="Total Sales",
            showgrid=True, gridcolor="rgba(255,255,255,0.06)",
            zeroline=False, tickfont=dict(size=11),
        ),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02,
            xanchor="right", x=1,
            bgcolor="rgba(0,0,0,0)", font=dict(size=11),
        ),
        hovermode="x unified",
        margin=dict(l=60, r=20, t=40, b=60),
        transition=dict(duration=350, easing="cubic-in-out"),
    )

    return fig


if __name__ == "__main__":
    app.run(debug=True)
