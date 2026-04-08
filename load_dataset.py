"""Load dataset.csv into SQLite and train the ML model."""
import csv
import os
import pickle
import sqlite3

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

DB_PATH = os.path.join(os.path.dirname(__file__), "crop.db")
DATASET_PATH = os.path.join(os.path.dirname(__file__), "..", "dataset.csv")
MODEL_PATH = os.path.join(os.path.dirname(__file__), "crop_model.pkl")
ENCODERS_PATH = os.path.join(os.path.dirname(__file__), "encoders.pkl")


def load_csv_to_db():
    if not os.path.exists(DATASET_PATH):
        print("dataset.csv not found at", DATASET_PATH)
        return
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE, mobile TEXT UNIQUE, password_hash TEXT NOT NULL,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP
    )""")
    conn.execute("DROP TABLE IF EXISTS crop_data")
    conn.execute("""
        CREATE TABLE crop_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            state TEXT, district TEXT, crop_name TEXT, season TEXT,
            min_temp REAL, max_temp REAL, rainfall REAL, humidity REAL,
            wind_speed REAL, soil_type TEXT, soil_ph REAL,
            irrigation_type TEXT, suitable TEXT
        )
    """)
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            conn.execute(
                """INSERT INTO crop_data (
                    state, district, crop_name, season,
                    min_temp, max_temp, rainfall, humidity, wind_speed,
                    soil_type, soil_ph, irrigation_type, suitable
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    row.get("State", ""),
                    row.get("District", ""),
                    row.get("Crop_Name", ""),
                    row.get("Season", ""),
                    float(row.get("Min_Temperature(C)", 0) or 0),
                    float(row.get("Max_Temperature(C)", 0) or 0),
                    float(row.get("Rainfall(mm)", 0) or 0),
                    float(row.get("Humidity(%)", 0) or 0),
                    float(row.get("Wind_Speed(km/h)", 0) or 0),
                    row.get("Soil_Type", ""),
                    float(row.get("Soil_pH", 7) or 7),
                    row.get("Irrigation_Type", ""),
                    row.get("Suitable(Y/N)", "N"),
                ),
            )
    conn.commit()
    conn.close()
    print("Dataset loaded into SQLite.")


def train_model():
    df = pd.read_csv(DATASET_PATH)
    df = df.rename(columns={
        "Min_Temperature(C)": "min_temp",
        "Max_Temperature(C)": "max_temp",
        "Rainfall(mm)": "rainfall",
        "Humidity(%)": "humidity",
        "Wind_Speed(km/h)": "wind_speed",
        "Soil_Type": "soil_type",
        "Soil_pH": "soil_ph",
        "Suitable(Y/N)": "suitable",
    })
    df["suitable"] = (df["suitable"] == "Y").astype(int)
    feature_cols = ["min_temp", "max_temp", "rainfall", "humidity", "wind_speed", "soil_ph"]
    le_soil = LabelEncoder()
    df["soil_encoded"] = le_soil.fit_transform(df["soil_type"].astype(str))
    feature_cols.append("soil_encoded")
    X = df[feature_cols]
    y = df["suitable"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    acc = model.score(X_test, y_test)
    print(f"Model accuracy: {acc:.2%}")
    with open(MODEL_PATH, "wb") as f:
        pickle.dump(model, f)
    with open(ENCODERS_PATH, "wb") as f:
        pickle.dump({"soil": le_soil, "feature_cols": feature_cols}, f)
    print("Model saved to crop_model.pkl")


if __name__ == "__main__":
    load_csv_to_db()
    train_model()
