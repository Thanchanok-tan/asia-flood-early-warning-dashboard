import os

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
PROCESSED_DATA_PATH = os.path.join(DATA_DIR, "processed", "asia_flood_dashboard_data.csv")
ALERT_CONFIG_PATH = os.path.join(DATA_DIR, "processed", "alert_config.json")
MODEL_PATH = os.path.join(BASE_DIR, "models", "flood_early_warning_pipeline.joblib")

# Fallback paths
FALLBACK_DATA_PATH = os.path.join(DATA_DIR, "asia_flood_dashboard_data.csv")
FALLBACK_MODEL_PATH = os.path.join(DATA_DIR, "flood_early_warning_pipeline.joblib")

# Color palette mapping for severity levels
SEVERITY_COLORS = {
    "Normal (Green)": "#10B981",    # Emerald Green
    "Warning (Yellow)": "#F59E0B",   # Amber Gold
    "Severe (Orange)": "#F97316",    # Warm Orange
    "Critical (Red)": "#EF4444"      # Crimson Red
}

SEVERITY_BG_LIGHT = {
    "Normal (Green)": "#D1FAE5",
    "Warning (Yellow)": "#FEF3C7",
    "Severe (Orange)": "#FFEDD5",
    "Critical (Red)": "#FEE2E2"
}

# Basins list
BASINS = [
    "Mekong Basin",
    "Chao Phraya Basin",
    "Ganges-Brahmaputra",
    "Yangtze River",
    "Indus River",
    "Irrawaddy Basin",
    "Red River Basin"
]

# Baseline historical metrics for delta comparisons
HISTORICAL_BASELINES = {
    "rainfall_mm": 48.5,
    "river_level_m": 6.80,
    "soil_moisture_percent": 65.2,
    "flood_risk_score": 0.38
}
