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
    numeric_cols = [col for col in ["rainfall_mm", "river_level_m", "flood_risk_score"] if col in df.columns]
    ts_df = df.groupby("date")[numeric_cols].mean().reset_index()

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Bar chart for rainfall
    if "rainfall_mm" in ts_df.columns:
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
    if "river_level_m" in ts_df.columns:
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

    if df.empty or "basin" not in df.columns:
        return

    # Check which target/risk column is available
    y_col = "flood_risk_score" if "flood_risk_score" in df.columns else "predicted_flood_proba"
    if y_col not in df.columns:
        return

    fig = px.box(
        df,
        x="basin",
        y=y_col,
        color="basin",
        points="outliers",
        height=420,
        labels={"basin": "Basin", y_col: "Flood Risk"}
    )

    # Add alert threshold horizontal lines
    fig.add_hline(y=0.46, line_dash="dash", line_color="#F59E0B", annotation_text="Warning Threshold (0.46)", annotation_position="top left")
    fig.add_hline(y=0.70, line_dash="dash", line_color="#F97316", annotation_text="Severe Threshold (0.70)", annotation_position="top left")
    fig.add_hline(y=0.92, line_dash="dash", line_color="#EF4444", annotation_text="Critical Threshold (0.92)", annotation_position="top left")

    fig.update_layout(
        showlegend=False,
        margin=dict(l=20, r=20, t=30, b=40)
    )

    st.plotly_chart(fig, use_container_width=True)

def render_correlation_heatmap(df: pd.DataFrame, lang: str):
    """Render hydrological correlation matrix heatmap."""
    st.subheader(get_text(lang, "analytics_heatmap"))

    if df.empty:
        return

    # Map possible column names to labels dynamically to avoid KeyError
    col_mapping = {
        "rainfall_mm": "Rainfall (mm)",
        "river_level_m": "River Level (m)",
        "soil_moisture_percent": "Soil Moisture (%)",
        "temperature_celsius": "Temp (°C)",
        "temperature_c": "Temp (°C)",
        "flood_risk_score": "Flood Risk",
        "predicted_flood_proba": "Predicted Risk"
    }

    available_cols = [col for col in col_mapping.keys() if col in df.columns]

    if len(available_cols) < 2:
        available_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    if len(available_cols) < 2:
        st.info("Not enough numeric columns for correlation analysis.")
        return

    corr = df[available_cols].corr()
    labels = [col_mapping.get(c, c) for c in available_cols]

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

    # Extract month if not available
    plot_df = df.copy()
    if "month" not in plot_df.columns and "date" in plot_df.columns:
        plot_df["month"] = pd.to_datetime(plot_df["date"]).dt.month

    if "month" not in plot_df.columns:
        return

    num_cols = [col for col in ["rainfall_mm", "river_level_m", "soil_moisture_percent"] if col in plot_df.columns]
    monthly = plot_df.groupby("month")[num_cols].mean().reset_index()
    
    month_names = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    monthly["month_name"] = monthly["month"].apply(lambda m: month_names[int(m)-1] if 1 <= int(m) <= 12 else str(m))

    fig = go.Figure()

    if "rainfall_mm" in monthly.columns:
        fig.add_trace(go.Scatter(x=monthly["month_name"], y=monthly["rainfall_mm"], name="Avg Rainfall (mm)", mode="lines+markers", line=dict(color="#2563EB", width=3)))
    if "river_level_m" in monthly.columns:
        fig.add_trace(go.Scatter(x=monthly["month_name"], y=monthly["river_level_m"] * 10, name="River Gauge (m x10)", mode="lines+markers", line=dict(color="#DC2626", width=3, dash="dot")))
    if "soil_moisture_percent" in monthly.columns:
        fig.add_trace(go.Scatter(x=monthly["month_name"], y=monthly["soil_moisture_percent"], name="Soil Moisture (%)", mode="lines+markers", line=dict(color="#059669", width=2)))

    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=380,
        margin=dict(l=20, r=20, t=30, b=20)
    )

    st.plotly_chart(fig, use_container_width=True)
