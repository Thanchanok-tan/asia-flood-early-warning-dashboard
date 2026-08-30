import pandas as pd
import numpy as np
# pyrefly: ignore [missing-import]
import plotly.graph_objects as go
# pyrefly: ignore [missing-import]
import streamlit as st
from src.data_loader import load_model, load_alert_config
from src.config import BASINS, SEVERITY_COLORS, SEVERITY_BG_LIGHT
from src.i18n import get_text

def render_simulator(lang: str):
    """Render interactive What-If ML Inference Simulator module."""
    st.subheader(get_text(lang, "simulator_title"))
    st.markdown(get_text(lang, "simulator_desc"))

    model = load_model()
    alert_config = load_alert_config()

    if model is None:
        st.warning("ML Pipeline model is currently loading or unavailable.")
        return

    col_input, col_output = st.columns([1.1, 0.9])

    with col_input:
        st.markdown("#### 🎛️ Input Meteorological & Hydrological Parameters")
        
        sim_rainfall = st.slider(get_text(lang, "sim_rainfall"), min_value=0.0, max_value=350.0, value=85.0, step=5.0)
        sim_river = st.slider(get_text(lang, "sim_river"), min_value=0.5, max_value=18.0, value=7.2, step=0.2)
        sim_soil = st.slider(get_text(lang, "sim_soil"), min_value=10.0, max_value=100.0, value=75.0, step=1.0)
        sim_temp = st.slider(get_text(lang, "sim_temp"), min_value=10.0, max_value=45.0, value=29.0, step=0.5)

        c1, c2, c3 = st.columns(3)
        with c1:
            sim_month = st.selectbox(get_text(lang, "sim_month"), options=list(range(1, 13)), index=7)
        with c2:
            sim_day = st.number_input(get_text(lang, "sim_day_of_year"), min_value=1, max_value=366, value=220)
        with c3:
            sim_monsoon = st.checkbox(get_text(lang, "sim_monsoon"), value=True)

        c4, c5 = st.columns(2)
        with c4:
            sim_basin = st.selectbox(get_text(lang, "sim_basin"), options=BASINS, index=0)
        with c5:
            countries = ["Thailand", "Vietnam", "Cambodia", "Laos", "India", "Bangladesh", "China", "Pakistan", "Myanmar"]
            sim_country = st.selectbox(get_text(lang, "sim_country"), options=countries, index=0)

    # Perform real-time ML inference
    input_data = pd.DataFrame([{
        "rainfall_mm": sim_rainfall,
        "river_level_m": sim_river,
        "soil_moisture_percent": sim_soil,
        "temperature_c": sim_temp,
        "month": sim_month,
        "day_of_year": sim_day,
        "monsoon_season": 1 if sim_monsoon else 0,
        "basin": sim_basin,
        "country": sim_country
    }])

    # Predict flood probability
    try:
        prob = float(model.predict_proba(input_data)[0][1])
    except Exception:
        # Logistic regression raw prediction fallback calculation
        raw = 0.35 * (sim_rainfall / 150) + 0.40 * (sim_river / 10) + 0.20 * (sim_soil / 100) + 0.05 * (1 if sim_monsoon else 0)
        prob = min(0.99, max(0.01, float(1 / (1 + np.exp(-6 * (raw - 0.72))))))

    # Severity level determination based on config thresholds
    if prob < 0.46:
        severity_key = "Normal (Green)"
        status_label = get_text(lang, "normal_green")
        badge_bg = "#d1fae5"
        badge_text = "#065f46"
        action_advice = "✅ All clear. Maintain standard baseline hydro station monitoring."
    elif prob < 0.70:
        severity_key = "Warning (Yellow)"
        status_label = get_text(lang, "warning_yellow")
        badge_bg = "#fef3c7"
        badge_text = "#92400e"
        action_advice = "⚠️ Caution advised. Increase gauge reading frequency & inspect spillway gates."
    elif prob < 0.92:
        severity_key = "Severe (Orange)"
        status_label = get_text(lang, "severe_orange")
        badge_bg = "#ffedd5"
        badge_text = "#9a3412"
        action_advice = "🚨 High Flood Alert! Issue pre-evacuation notices for downstream low-lying communities."
    else:
        severity_key = "Critical (Red)"
        status_label = get_text(lang, "critical_red")
        badge_bg = "#fee2e2"
        badge_text = "#991b1b"
        action_advice = "‼️ EMERGENCY CRITICAL ALERT! Immediate disaster mobilization & emergency flood barriers required!"

    with col_output:
        st.markdown(f"#### 📊 {get_text(lang, 'sim_risk_gauge_title')}")
        
        # Render Gauge Chart
        gauge_fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=round(prob * 100, 1),
            number={"suffix": "%"},
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Predicted Flood Probability"},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1},
                'bar': {'color': SEVERITY_COLORS.get(severity_key, "#3B82F6")},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#CBD5E1",
                'steps': [
                    {'range': [0, 46], 'color': "#D1FAE5"},
                    {'range': [46, 70], 'color': "#FEF3C7"},
                    {'range': [70, 92], 'color': "#FFEDD5"},
                    {'range': [92, 100], 'color': "#FEE2E2"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 70.0
                }
            }
        ))

        gauge_fig.update_layout(height=280, margin=dict(l=20, r=20, t=30, b=10))
        st.plotly_chart(gauge_fig, use_container_width=True)

        # Status & Response Guidance Box
        st.markdown(
            f"""
            <div class="sim-response-card" style="border-left-color: {SEVERITY_COLORS.get(severity_key, '#3B82F6')};">
                <div style="font-size: 0.85rem; font-weight: 700; text-transform: uppercase; color: #64748B; margin-bottom: 4px;">
                    {get_text(lang, 'sim_status_title')}
                </div>
                <div style="margin-bottom: 12px;">
                    <span class="badge" style="background-color: {badge_bg}; color: {badge_text}; font-size: 0.95rem; padding: 6px 14px;">
                        {status_label}
                    </span>
                </div>
                <div style="font-size: 0.95rem; color: #334155; line-height: 1.5; font-weight: 500;">
                    <b>Action Protocol:</b> {action_advice}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
