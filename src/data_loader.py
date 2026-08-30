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
    """Load the hydro-meteorological 25-year dataset with auto format/path detection."""
    # รวม Path ที่เป็นไปได้ทั้งหมด
    candidate_paths = [
        PROCESSED_DATA_PATH,
        FALLBACK_DATA_PATH,
        "data/asia_flood_dashboard_data.parquet",
        "asia_flood_dashboard_data.parquet",
        "data/asia_flood_dashboard_data.csv",
        "asia_flood_dashboard_data.csv"
    ]
    
    valid_path = None
    for p in candidate_paths:
        if p and os.path.exists(p):
            valid_path = p
            break

    if not valid_path:
        st.error("❌ Dataset not found. Please verify that 'asia_flood_dashboard_data.parquet' or '.csv' is uploaded.")
        return pd.DataFrame()
    
    try:
        if valid_path.endswith('.parquet'):
            df = pd.read_parquet(valid_path)
        else:
            df = pd.read_csv(valid_path)
            
        df["date"] = pd.to_datetime(df["date"])
        return df
    except Exception as e:
        st.error(f"❌ Failed to read dataset from {valid_path}: {e}")
        return pd.DataFrame()


@st.cache_resource
def load_model():
    """Load trained Scikit-learn flood early warning pipeline model."""
    candidate_paths = [
        MODEL_PATH,
        FALLBACK_MODEL_PATH,
        "models/flood_early_warning_pipeline.joblib",
        "flood_early_warning_pipeline.joblib",
        "data/flood_early_warning_pipeline.joblib"
    ]
    
    valid_path = None
    for p in candidate_paths:
        if p and os.path.exists(p):
            valid_path = p
            break

    if not valid_path:
        st.error("❌ Model file 'flood_early_warning_pipeline.joblib' not found.")
        return None
    try:
        loaded_obj = joblib.load(valid_path)
        return loaded_obj
    except Exception as e:
        st.error(f"❌ Failed to load joblib model: {e}")
        return None


@st.cache_data
def load_alert_config():
    """Load alert thresholds and severity configuration."""
    candidate_paths = [
        ALERT_CONFIG_PATH,
        "data/alert_config.json",
        "alert_config.json"
    ]
    
    for p in candidate_paths:
        if p and os.path.exists(p):
            try:
                with open(p, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass

    # ค่าเริ่มต้นสำรอง (Fallback)
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

    # รองรับการเลือกทั้งภาษาอังกฤษและไทย
    all_filters = ["All", "All Basins", "All Countries", "All Basins / Countries", "ลุ่มน้ำ/ประเทศ ทั้งหมด", "ทั้งหมด"]

    if basin and basin not in all_filters:
        filtered = filtered[filtered["basin"] == basin]

    if country and country not in all_filters:
        filtered = filtered[filtered["country"] == country]

    if station and station not in ["All Stations", "สถานี ทั้งหมด", "ทั้งหมด"]:
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
    latest_df = df[df["date"] == latest_date]

    total_stations = latest_df["station_id"].nunique()

    # ตรวจสอบทั้งคอลัมน์ alert_level และ severity_level
    if "alert_level" in latest_df.columns:
        critical_mask = latest_df["alert_level"].isin(["Severe (Orange)", "Critical (Red)"])
    else:
        critical_mask = latest_df["severity_level"].isin(["High", "Extreme", "Severe (Orange)", "Critical (Red)"])[cite: 1]
    
    critical_alerts = latest_df[critical_mask]["station_id"].nunique()

    avg_rainfall = round(df["rainfall_mm"].mean(), 1)
    avg_river_level = round(df["river_level_m"].mean(), 2)
    mean_risk_score = round(df["flood_risk_score"].mean(), 3)

    # ฟังก์ชันช่วยคิด Delta อย่างปลอดภัย
    def calc_delta(current, baseline):
        if not baseline:
            return 0.0
        return round(((current - baseline) / baseline) * 100, 1)

    rainfall_delta = calc_delta(avg_rainfall, HISTORICAL_BASELINES.get("rainfall_mm", 20.28))
    river_delta = calc_delta(avg_river_level, HISTORICAL_BASELINES.get("river_level_m", 5.57))
    risk_delta = calc_delta(mean_risk_score, HISTORICAL_BASELINES.get("flood_risk_score", 3.44))

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
