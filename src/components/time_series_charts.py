# pyrefly: ignore [missing-import]
import plotly.graph_objects as go
# pyrefly: ignore [missing-import]
import plotly.express as px
import pandas as pd
import numpy as np
# pyrefly: ignore [missing-import]
import streamlit as st
# pyrefly: ignore [missing-import]
from plotly.subplots import make_subplots
from src.config import SEVERITY_COLORS
from src.i18n import get_text

def render_dual_axis_chart(df: pd.DataFrame, lang: str):
    """Render dual-axis chart: Rainfall (bar/area) vs River level (line)."""
    st.subheader(get_text(lang, "analytics_dual_axis"))

    if df.empty:
        st.info("No time series data available for selection.")
        return

    # Group by date for smooth aggregate trend
    ts_df = df.groupby("date")[["rainfall_mm", "river_level_m", "flood_risk_score"]].mean().reset_index()

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Bar chart for rainfall
    fig.add_trace(
        go.Bar(
            x=ts_df["date"],
            y=ts_df["rainfall_mm"],
            name=get_text(lang, "chart_rainfall_axis"),
            marker_color="rgba(59, 130, 246, 0.5)",
            hovertemplate="%{x|%Y-%m-%d}<br>Rainfall: %{y:.1f} mm<extra></extra>"
        ),
        secondary_y=False
    )

    # Line chart for river level
    fig.add_trace(
        go.Scatter(
            x=ts_df["date"],
            y=ts_df["river_level_m"],
            name=get_text(lang, "chart_river_axis"),
            mode="lines",
            line=dict(color="#EF4444", width=2.5),
            hovertemplate="%{x|%Y-%m-%d}<br>River Gauge: %{y:.2f} m<extra></extra>"
        ),
        secondary_y=True
    )

    fig.update_xaxes(title_text="Date")
    fig.update_yaxes(title_text=get_text(lang, "chart_rainfall_axis"), secondary_y=False, showgrid=True)
    fig.update_yaxes(title_text=get_text(lang, "chart_river_axis"), secondary_y=True, showgrid=False)

    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=420,
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode="x unified"
    )

    st.plotly_chart(fig, use_container_width=True)

def render_basin_boxplot(df: pd.DataFrame, lang: str):
    """Render basin-wise risk distribution boxplots with threshold lines."""
    st.subheader(get_text(lang, "analytics_boxplot"))

    if df.empty:
        return

    fig = px.box(
        df,
        x="basin",
        y="flood_risk_score",
        color="basin",
        points="outliers",
        height=420,
        labels={"basin": "Basin", "flood_risk_score": "Flood Risk Score"}
    )

    # Add alert threshold horizontal lines
    fig.add_hline(y=0.46, line_dash="dash", line_color="#F59E0B", annotation_text="Warning Threshold (0.46)", annotation_position="top left")
    fig.add_hline(y=0.70, line_dash="dash", line_color="#F97316", annotation_text="Severe Threshold (0.70)", annotation_position="top left")
    fig.add_hline(y=0.92, line_dash="dash", line_color="#EF4444", annotation_text="Critical Threshold (0.92)", annotation_position="top left")

    fig.update_layout(
        showlegend=False,
        margin=dict(l=20, r=20, t=30, b=40),
        yaxis=dict(range=[0, 1.05])
    )

    st.plotly_chart(fig, use_container_width=True)

def render_correlation_heatmap(df: pd.DataFrame, lang: str):
    """Render hydrological correlation matrix heatmap."""
    st.subheader(get_text(lang, "analytics_heatmap"))

    if df.empty:
        return

    num_cols = ["rainfall_mm", "river_level_m", "soil_moisture_percent", "temperature_c", "flood_risk_score"]
    corr = df[num_cols].corr()

    labels = ["Rainfall (mm)", "River Level (m)", "Soil Moisture (%)", "Temp (°C)", "Flood Risk"]

    fig = px.imshow(
        corr,
        x=labels,
        y=labels,
        color_continuous_scale="Blues",
        aspect="auto",
        text_auto=".2f",
        height=380
    )

    fig.update_layout(margin=dict(l=20, r=20, t=30, b=20))
    st.plotly_chart(fig, use_container_width=True)

def render_seasonal_lag_chart(df: pd.DataFrame, lang: str):
    """Render seasonal lag monthly profile."""
    st.subheader(get_text(lang, "analytics_lag"))

    if df.empty:
        return

    monthly = df.groupby("month")[["rainfall_mm", "river_level_m", "soil_moisture_percent"]].mean().reset_index()
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly["month_name"] = monthly["month"].apply(lambda m: month_names[m-1])

    fig = go.Figure()

    fig.add_trace(go.Scatter(x=monthly["month_name"], y=monthly["rainfall_mm"], name="Avg Rainfall (mm)", mode="lines+markers", line=dict(color="#2563EB", width=3)))
    fig.add_trace(go.Scatter(x=monthly["month_name"], y=monthly["river_level_m"] * 10, name="River Gauge (m x10)", mode="lines+markers", line=dict(color="#DC2626", width=3, dash="dot")))
    fig.add_trace(go.Scatter(x=monthly["month_name"], y=monthly["soil_moisture_percent"], name="Soil Moisture (%)", mode="lines+markers", line=dict(color="#059669", width=2)))

    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=380,
        margin=dict(l=20, r=20, t=30, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)
