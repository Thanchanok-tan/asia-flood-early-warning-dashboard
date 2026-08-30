# pyrefly: ignore [missing-import]
import streamlit as st
from src.i18n import get_text

def render_kpi_cards(kpi_data: dict, lang: str):
    """Render 5 executive metric summary cards with trend deltas."""
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">{get_text(lang, 'kpi_total_stations')}</div>
                <div class="kpi-value">{kpi_data['total_stations']}</div>
                <div class="kpi-delta-neutral">Active Basins Tracked</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col2:
        critical_count = kpi_data['critical_alerts']
        delta_class = "kpi-delta-up" if critical_count > 0 else "kpi-delta-neutral"
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">{get_text(lang, 'kpi_critical_alerts')}</div>
                <div class="kpi-value" style="color: {'#ef4444' if critical_count > 0 else '#10b981'};">{critical_count}</div>
                <div class="{delta_class}">Orange / Red Alert Level</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col3:
        rain_val = kpi_data['avg_rainfall']
        rain_delta = kpi_data['rainfall_delta']
        rain_class = "kpi-delta-up" if rain_delta > 0 else "kpi-delta-down"
        arrow = "▲" if rain_delta > 0 else "▼"
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">{get_text(lang, 'kpi_avg_rainfall')}</div>
                <div class="kpi-value">{rain_val} <span style="font-size: 1rem;">mm</span></div>
                <div class="{rain_class}">{arrow} {abs(rain_delta)}% {get_text(lang, 'vs_baseline')}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col4:
        river_val = kpi_data['avg_river_level']
        river_delta = kpi_data['river_delta']
        river_class = "kpi-delta-up" if river_delta > 0 else "kpi-delta-down"
        arrow = "▲" if river_delta > 0 else "▼"
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">{get_text(lang, 'kpi_avg_river_level')}</div>
                <div class="kpi-value">{river_val} <span style="font-size: 1rem;">m</span></div>
                <div class="{river_class}">{arrow} {abs(river_delta)}% {get_text(lang, 'vs_baseline')}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

    with col5:
        risk_val = kpi_data['mean_risk_score']
        risk_delta = kpi_data['risk_delta']
        risk_class = "kpi-delta-up" if risk_delta > 0 else "kpi-delta-down"
        arrow = "▲" if risk_delta > 0 else "▼"
        st.markdown(
            f"""
            <div class="kpi-card">
                <div class="kpi-title">{get_text(lang, 'kpi_mean_risk_score')}</div>
                <div class="kpi-value">{risk_val}</div>
                <div class="{risk_class}">{arrow} {abs(risk_delta)}% {get_text(lang, 'vs_baseline')}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
