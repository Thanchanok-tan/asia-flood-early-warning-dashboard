import json
import pandas as pd
# pyrefly: ignore [missing-import]
import streamlit as st
from src.config import SEVERITY_COLORS
from src.i18n import get_text

def render_alert_feed_and_export(df: pd.DataFrame, lang: str):
    """Render live alert ticker feed, station status table, and data export features."""
    st.subheader(get_text(lang, "alert_feed_title"))

    if df.empty:
        st.info("No alert records available for selection.")
        return

    latest_date = df["date"].max()
    latest_df = df[df["date"] == latest_date].sort_values("flood_risk_score", ascending=False)

    # Critical / Severe station ticker
    high_alerts = latest_df[latest_df["severity_level"].isin(["Severe (Orange)", "Critical (Red)"])]

    if not high_alerts.empty:
        ticker_items = []
        for _, row in high_alerts.iterrows():
            ticker_items.append(
                f"🚨 <b>{row['station_name']} ({row['basin']})</b>: Flood Risk <b>{(row['flood_risk_score']*100):.1f}%</b> | Rainfall {row['rainfall_mm']}mm | River Gauge {row['river_level_m']}m"
            )
        ticker_html = " &nbsp;&nbsp;&nbsp; | &nbsp;&nbsp;&nbsp; ".join(ticker_items)

        st.markdown(
            f"""
            <div style="background-color: #FEE2E2; border: 1px solid #FCA5A5; border-radius: 8px; padding: 12px 18px; margin-bottom: 20px; color: #991B1B; font-size: 0.92rem;">
                <marquee scrollamount="6">{ticker_html}</marquee>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            """
            <div style="background-color: #D1FAE5; border: 1px solid #6EE7B7; border-radius: 8px; padding: 12px 18px; margin-bottom: 20px; color: #065F46; font-size: 0.92rem;">
                ✅ <b>All Active Basins Normal</b>: No critical flood alerts recorded in the latest telemetry cycle.
            </div>
            """,
            unsafe_allow_html=True
        )

    # Active Station Status Table
    st.markdown("#### 📋 Monitoring Station Status Table")
    display_cols = ["station_id", "station_name", "basin", "country", "severity_level", "flood_risk_score", "rainfall_mm", "river_level_m", "soil_moisture_percent", "date"]
    
    table_df = latest_df[display_cols].copy()
    table_df["date"] = pd.to_datetime(table_df["date"]).dt.strftime("%Y-%m-%d")
    table_df["flood_risk_score"] = (pd.to_numeric(table_df["flood_risk_score"], errors="coerce") * 100).round(1).astype(str) + "%"

    st.dataframe(table_df, use_container_width=True, height=280)

    # Data Export Section
    st.markdown("---")
    st.subheader(get_text(lang, "data_export_title"))
    st.markdown(f"**{get_text(lang, 'total_records')}:** `{len(df)}` rows")

    col1, col2 = st.columns(2)

    with col1:
        csv_data = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label=get_text(lang, "download_csv"),
            data=csv_data,
            file_name=f"asia_flood_data_filtered_{latest_date.strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

    with col2:
        # Generate summary statistics JSON export
        summary_stats = {
            "export_timestamp": pd.Timestamp.now().isoformat(),
            "total_records": len(df),
            "date_range": [df["date"].min().strftime("%Y-%m-%d"), df["date"].max().strftime("%Y-%m-%d")],
            "basins_covered": df["basin"].unique().tolist(),
            "stations_count": df["station_id"].nunique(),
            "mean_rainfall_mm": round(float(df["rainfall_mm"].mean()), 2),
            "mean_river_level_m": round(float(df["river_level_m"].mean()), 2),
            "mean_flood_risk": round(float(df["flood_risk_score"].mean()), 4),
            "severity_distribution": df["severity_level"].value_counts().to_dict()
        }
        json_data = json.dumps(summary_stats, indent=4).encode('utf-8')
        st.download_button(
            label=get_text(lang, "download_json"),
            data=json_data,
            file_name=f"asia_flood_summary_stats_{latest_date.strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )
