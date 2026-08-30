import os
import json
import numpy as np
import pandas as pd
import joblib
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression

def generate_dataset_and_model():
    print("Generating Asian 25-Year Hydro-Meteorological Dataset (2000-2024)...")
    np.random.seed(42)

    # Define Asian Monitoring Stations across major basins
    stations = [
        {"station_id": "STN-MEK-01", "station_name": "Vientiane Hydro Station", "basin": "Mekong Basin", "country": "Laos", "lat": 17.9757, "lon": 102.6331, "base_rain": 45, "base_river": 5.2, "base_soil": 65},
        {"station_id": "STN-MEK-02", "station_name": "Phnom Penh Chroy Changvar", "basin": "Mekong Basin", "country": "Cambodia", "lat": 11.5564, "lon": 104.9282, "base_rain": 50, "base_river": 6.8, "base_soil": 70},
        {"station_id": "STN-MEK-03", "station_name": "Chiang Saen Gauge", "basin": "Mekong Basin", "country": "Thailand", "lat": 20.2741, "lon": 100.0886, "base_rain": 40, "base_river": 4.5, "base_soil": 60},
        {"station_id": "STN-CHP-01", "station_name": "Nakhon Sawan C.2 Station", "basin": "Chao Phraya Basin", "country": "Thailand", "lat": 15.7003, "lon": 100.1245, "base_rain": 42, "base_river": 5.8, "base_soil": 62},
        {"station_id": "STN-CHP-02", "station_name": "Ayutthaya Bang Sai Post", "basin": "Chao Phraya Basin", "country": "Thailand", "lat": 14.1950, "lon": 100.5140, "base_rain": 48, "base_river": 4.9, "base_soil": 68},
        {"station_id": "STN-GAN-01", "station_name": "Patna Ganga Station", "basin": "Ganges-Brahmaputra", "country": "India", "lat": 25.5941, "lon": 85.1376, "base_rain": 55, "base_river": 7.2, "base_soil": 72},
        {"station_id": "STN-GAN-02", "station_name": "Dhaka Buriganga Gauge", "basin": "Ganges-Brahmaputra", "country": "Bangladesh", "lat": 23.8103, "lon": 90.4125, "base_rain": 65, "base_river": 8.1, "base_soil": 80},
        {"station_id": "STN-YAN-01", "station_name": "Wuhan Yangtze Station", "basin": "Yangtze River", "country": "China", "lat": 30.5928, "lon": 114.3055, "base_rain": 45, "base_river": 12.5, "base_soil": 64},
        {"station_id": "STN-YAN-02", "station_name": "Nanjing River Monitor", "basin": "Yangtze River", "country": "China", "lat": 32.0603, "lon": 118.7969, "base_rain": 40, "base_river": 10.2, "base_soil": 58},
        {"station_id": "STN-IND-01", "station_name": "Sukkur Barrage", "basin": "Indus River", "country": "Pakistan", "lat": 27.7052, "lon": 68.8574, "base_rain": 25, "base_river": 6.1, "base_soil": 45},
        {"station_id": "STN-IND-02", "station_name": "Khyber Upper Indus", "basin": "Indus River", "country": "Pakistan", "lat": 34.0151, "lon": 71.5249, "base_rain": 35, "base_river": 5.4, "base_soil": 50},
        {"station_id": "STN-IRR-01", "station_name": "Mandalay Ayeyarwady", "basin": "Irrawaddy Basin", "country": "Myanmar", "lat": 21.9588, "lon": 96.0891, "base_rain": 48, "base_river": 6.5, "base_soil": 66},
        {"station_id": "STN-IRR-02", "station_name": "Yangon Delta Station", "basin": "Irrawaddy Basin", "country": "Myanmar", "lat": 16.8661, "lon": 96.1951, "base_rain": 70, "base_river": 5.8, "base_soil": 78},
        {"station_id": "STN-RED-01", "station_name": "Hanoi Red River Post", "basin": "Red River Basin", "country": "Vietnam", "lat": 21.0285, "lon": 105.8542, "base_rain": 52, "base_river": 7.8, "base_soil": 74},
        {"station_id": "STN-RED-02", "station_name": "Yen Bai Upper Red River", "basin": "Red River Basin", "country": "Vietnam", "lat": 21.7050, "lon": 104.8750, "base_rain": 58, "base_river": 6.9, "base_soil": 76}
    ]

    # Generate daily records for key sample dates across 2000-2024
    dates = pd.date_range(start="2000-01-01", end="2024-12-31", freq="7D") # Sampled every 7 days for rich, lightweight dataset
    records = []

    for d in dates:
        month = d.month
        day_of_year = d.dayofyear
        # Asian monsoon season usually June-October (months 6-10)
        is_monsoon = 1 if month in [5, 6, 7, 8, 9, 10] else 0
        monsoon_mult = 2.2 if is_monsoon else 0.5

        for st in stations:
            # Add stochastic variation & seasonal cycle
            seasonal_factor = np.sin((month - 3) / 12 * 2 * np.pi) + 1.2
            random_spike = np.random.exponential(scale=1.2) if np.random.rand() > 0.88 else 0.2

            rainfall = max(0.0, round(st["base_rain"] * monsoon_mult * seasonal_factor * (0.4 + np.random.rand() + random_spike), 1))
            river_level = max(0.5, round(st["base_river"] * (0.6 + 0.5 * (rainfall / 80) + 0.3 * np.random.rand()), 2))
            soil_moisture = min(98.0, max(10.0, round(st["base_soil"] * (0.7 + 0.3 * (rainfall / 100) + 0.1 * np.random.randn()), 1)))
            temperature = round(28.0 - 0.05 * (st["lat"] - 10) + 4.0 * np.sin((month - 5) / 12 * 2 * np.pi) + np.random.normal(0, 1.5), 1)

            # Compute realistic non-linear flood risk score (0 to 1)
            raw_risk = (
                0.35 * (rainfall / 150) +
                0.40 * (river_level / (st["base_river"] * 1.8)) +
                0.20 * (soil_moisture / 100) +
                0.05 * is_monsoon
            )
            flood_risk_score = min(0.99, max(0.01, round(1 / (1 + np.exp(-6 * (raw_risk - 0.72))), 4)))

            # Severity classification
            if flood_risk_score < 0.46:
                severity = "Normal (Green)"
            elif flood_risk_score < 0.70:
                severity = "Warning (Yellow)"
            elif flood_risk_score < 0.92:
                severity = "Severe (Orange)"
            else:
                severity = "Critical (Red)"

            flood_event = 1 if flood_risk_score >= 0.70 else 0

            records.append({
                "date": d.strftime("%Y-%m-%d"),
                "year": d.year,
                "month": d.month,
                "day": d.day,
                "day_of_year": day_of_year,
                "station_id": st["station_id"],
                "station_name": st["station_name"],
                "basin": st["basin"],
                "country": st["country"],
                "latitude": st["lat"],
                "longitude": st["lon"],
                "rainfall_mm": rainfall,
                "river_level_m": river_level,
                "soil_moisture_percent": soil_moisture,
                "temperature_c": temperature,
                "monsoon_season": is_monsoon,
                "flood_risk_score": flood_risk_score,
                "flood_event_occurred": flood_event,
                "severity_level": severity
            })

    df = pd.DataFrame(records)

    # Save datasets
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("data/raw", exist_ok=True)
    csv_path = "data/processed/asia_flood_dashboard_data.csv"
    df.to_csv(csv_path, index=False)
    df.to_csv("data/raw/station_daily_data_sample.csv", index=False)
    print(f"Saved dataset ({len(df)} rows) to {csv_path}")

    # Build and Train ML Pipeline Model
    print("Training Early Warning Pipeline Model...")
    numeric_features = ["rainfall_mm", "river_level_m", "soil_moisture_percent", "temperature_c", "month", "day_of_year", "monsoon_season"]
    categorical_features = ["basin", "country"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features)
        ]
    )

    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", LogisticRegression(random_state=42, max_iter=1000))
    ])

    X = df[numeric_features + categorical_features]
    y = df["flood_event_occurred"]

    pipeline.fit(X, y)

    # Save models
    os.makedirs("models", exist_ok=True)
    model_path1 = "models/flood_early_warning_pipeline.joblib"
    model_path2 = "data/processed/flood_early_warning_pipeline.joblib"
    model_path3 = "data/flood_early_warning_pipeline.joblib"

    joblib.dump(pipeline, model_path1)
    joblib.dump(pipeline, model_path2)
    joblib.dump(pipeline, model_path3)
    print(f"Saved pipeline model to {model_path1}")

    # Save alert_config.json
    alert_config = {
        "model_name": "Logistic Regression",
        "optimal_threshold": 0.70,
        "alert_levels": {
            "Normal (Green)": [0.0, 0.46],
            "Warning (Yellow)": [0.46, 0.70],
            "Severe (Orange)": [0.70, 0.92],
            "Critical (Red)": [0.92, 1.0]
        }
    }
    with open("data/processed/alert_config.json", "w") as f:
        json.dump(alert_config, f, indent=4)
    with open("data/alert_config.json", "w") as f:
        json.dump(alert_config, f, indent=4)
    print("Saved alert_config.json successfully.")

if __name__ == "__main__":
    generate_dataset_and_model()
