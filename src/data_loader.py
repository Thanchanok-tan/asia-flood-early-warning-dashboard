import os
import json
import joblib
import pandas as pd
import streamlit as st
from src.config import (
    PROCESSED_DATA_PATH,
    FALLBACK_DATA_PATH,
    ALERT_CONFIG_PATH,
    MODEL_PATH,
    FALLBACK_MODEL_PATH,
    HISTORICAL_BASELINES
)

@st.cache_data(ttl=3600)
def load_dataset():
    """Load the hydro-meteorological 25-year dataset."""
    path = PROCESSED_DATA_PATH if os.path.exists(PROCESSED_DATA_PATH) else FALLBACK_DATA_PATH
    if not os.path.exists(path):
        st.error(f"Dataset not found at {path}. Please run `python scripts/generate_data_and_model.py` first.")
        return pd.DataFrame()
    
    df = pd.read_csv(path)
    df["date"] = pd.to_datetime(df["date"])
    return df

@st.cache_resource
def load_model():
    """Load trained Scikit-learn flood early warning pipeline model."""
    path = MODEL_PATH if os.path.exists(MODEL_PATH) else FALLBACK_MODEL_PATH
    if not os.path.exists(path):
        st.error(f"Model file not found at {path}.")
        return None
    try:
        model = joblib.load(path)
        return model
    except Exception as e:
        st.error(f"Failed to load joblib model: {e}")
        return None

@st.cache_data
def load_alert_config():
    """Load alert thresholds and severity configuration."""
    if os.path.exists(ALERT_CONFIG_PATH):
        with open(ALERT_CONFIG_PATH, "r") as f:
            return json.load(f)
    return {
        "model_name": "Logistic Regression",
        "optimal_threshold": 0.70,
        "alert_levels": {
            "Normal (Green)": [0.0, 0.46],
            "Warning (Yellow)": [0.46, 0.70],
            "Severe (Orange)": [0.70, 0.92],
            "Critical (Red)": [0.92, 1.0]
        }
    }

def filter_dataset(df, basin=None, country=None, station=None, start_date=None, end_date=None):
    """Filter dataframe by basin, country, station, and date range."""
    if df.empty:
        return df

    filtered = df.copy()

    if basin and basin != "All Basins / Countries" and basin != "ลุ่มน้ำ/ประเทศ ทั้งหมด":
        filtered = filtered[filtered["basin"] == basin]

    if country and country != "All Basins / Countries" and country != "ลุ่มน้ำ/ประเทศ ทั้งหมด":
        filtered = filtered[filtered["country"] == country]

    if station and station != "All Stations" and station != "สถานี ทั้งหมด":
        filtered = filtered[filtered["station_name"] == station]

    if start_date:
        filtered = filtered[filtered["date"] >= pd.to_datetime(start_date)]

    if end_date:
        filtered = filtered[filtered["date"] <= pd.to_datetime(end_date)]

    return filtered

def compute_kpis(df):
    """Compute executive summary KPI metrics and delta percentages vs baseline."""
    if df.empty:
        return {
            "total_stations": 0,
            "critical_alerts": 0,
            "avg_rainfall": 0.0,
            "rainfall_delta": 0.0,
            "avg_river_level": 0.0,
            "river_delta": 0.0,
            "mean_risk_score": 0.0,
            "risk_delta": 0.0
        }

    latest_date = df["date"].max()
    # Focus latest status on the most recent sampled time slice
    latest_df = df[df["date"] == latest_date]

    total_stations = latest_df["station_id"].nunique()
    critical_alerts = latest_df[latest_df["severity_level"].isin(["Severe (Orange)", "Critical (Red)"])]["station_id"].nunique()

    avg_rainfall = round(df["rainfall_mm"].mean(), 1)
    avg_river_level = round(df["river_level_m"].mean(), 2)
    mean_risk_score = round(df["flood_risk_score"].mean(), 3)

    rainfall_delta = round(((avg_rainfall - HISTORICAL_BASELINES["rainfall_mm"]) / HISTORICAL_BASELINES["rainfall_mm"]) * 100, 1)
    river_delta = round(((avg_river_level - HISTORICAL_BASELINES["river_level_m"]) / HISTORICAL_BASELINES["river_level_m"]) * 100, 1)
    risk_delta = round(((mean_risk_score - HISTORICAL_BASELINES["flood_risk_score"]) / HISTORICAL_BASELINES["flood_risk_score"]) * 100, 1)

    return {
        "total_stations": total_stations,
        "critical_alerts": critical_alerts,
        "avg_rainfall": avg_rainfall,
        "rainfall_delta": rainfall_delta,
        "avg_river_level": avg_river_level,
        "river_delta": river_delta,
        "mean_risk_score": mean_risk_score,
        "risk_delta": risk_delta
    }
