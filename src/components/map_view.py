import plotly.express as px
import pandas as pd
import streamlit as st
from src.config import SEVERITY_COLORS
from src.i18n import get_text

def render_map_view(df: pd.DataFrame, lang: str):
    """Render interactive Plotly geospatial early warning map."""
    st.subheader(get_text(lang, "map_title"))

    if df.empty:
        st.info("No monitoring station data available for current selection.")
        return

    # Focus map on the latest status per station
    latest_df = df.sort_values("date").groupby("station_id", as_index=False).last()

    # Create size metric proportional to risk score & river level
    latest_df["marker_size"] = latest_df["river_level_m"] * 2.5 + latest_df["flood_risk_score"] * 15

    # Hover text styling
    latest_df["hover_info"] = (
        "<b>" + latest_df["station_name"] + "</b><br>" +
        get_text(lang, "hover_basin") + ": " + latest_df["basin"] + "<br>" +
        get_text(lang, "hover_country") + ": " + latest_df["country"] + "<br>" +
        "-----------------------------<br>" +
        get_text(lang, "hover_risk") + f": <b>" + (latest_df["flood_risk_score"] * 100).round(1).astype(str) + "%</b><br>" +
        get_text(lang, "hover_severity") + ": " + latest_df["severity_level"] + "<br>" +
        get_text(lang, "hover_rainfall") + ": " + latest_df["rainfall_mm"].astype(str) + " mm<br>" +
        get_text(lang, "hover_river") + ": " + latest_df["river_level_m"].astype(str) + " m<br>" +
        get_text(lang, "hover_soil") + ": " + latest_df["soil_moisture_percent"].astype(str) + " %<br>" +
        get_text(lang, "hover_date") + ": " + latest_df["date"].dt.strftime("%Y-%m-%d")
    )

    fig = px.scatter_mapbox(
        latest_df,
        lat="latitude",
        lon="longitude",
        color="severity_level",
        size="marker_size",
        color_discrete_map=SEVERITY_COLORS,
        hover_name="station_name",
        hover_data={"hover_info": True, "latitude": False, "longitude": False, "marker_size": False, "severity_level": False},
        zoom=3.8,
        center={"lat": 20.0, "lon": 98.0},
        mapbox_style="open-street-map",
        height=580
    )

    fig.update_traces(
        hovertemplate="%{customdata[0]}<extra></extra>",
        marker=dict(opacity=0.88)
    )

    fig.update_layout(
        margin={"r": 0, "t": 10, "l": 0, "b": 0},
        legend=dict(
            title=get_text(lang, "map_legend"),
            orientation="h",
            yanchor="bottom",
            y=0.02,
            xanchor="left",
            x=0.02,
            bgcolor="rgba(255, 255, 255, 0.85)"
        )
    )

    st.plotly_chart(fig, use_container_width=True)
