"""Crop suitability using ML model and dataset; slide-by-slide reasons and recommendations."""
import os
import pickle
import aiosqlite
from typing import List, Optional, Tuple

from config import DB_PATH

MODEL_PATH = os.path.join(os.path.dirname(__file__), "crop_model.pkl")
ENCODERS_PATH = os.path.join(os.path.dirname(__file__), "encoders.pkl")

_model = None
_encoders = None


def _load_model():
    global _model, _encoders
    if _model is None and os.path.exists(MODEL_PATH):
        with open(MODEL_PATH, "rb") as f:
            _model = pickle.load(f)
        with open(ENCODERS_PATH, "rb") as f:
            _encoders = pickle.load(f)
    return _model, _encoders


async def get_crop_requirements(crop_name: str) -> Optional[dict]:
    """Get min/max temp, rainfall, humidity, soil types from dataset for a crop (suitable rows)."""
    conn = await aiosqlite.connect(DB_PATH)
    conn.row_factory = aiosqlite.Row
    try:
        cur = await conn.execute(
            """SELECT min_temp, max_temp, rainfall, humidity, wind_speed, soil_type, soil_ph
               FROM crop_data WHERE LOWER(TRIM(crop_name)) = LOWER(TRIM(?)) AND suitable = 'Y'""",
            (crop_name,),
        )
        rows = await cur.fetchall()
        if not rows:
            cur = await conn.execute(
                """SELECT min_temp, max_temp, rainfall, humidity, wind_speed, soil_type, soil_ph
                   FROM crop_data WHERE LOWER(TRIM(crop_name)) = LOWER(TRIM(?))""",
                (crop_name,),
            )
            rows = await cur.fetchall()
        if not rows:
            return None
        min_t = min(r["min_temp"] for r in rows)
        max_t = max(r["max_temp"] for r in rows)
        rain_lo = min(r["rainfall"] for r in rows)
        rain_hi = max(r["rainfall"] for r in rows)
        hum_lo = min(r["humidity"] for r in rows)
        hum_hi = max(r["humidity"] for r in rows)
        soils = list(set(r["soil_type"] for r in rows))
        ph_lo = min(r["soil_ph"] for r in rows)
        ph_hi = max(r["soil_ph"] for r in rows)
        return {
            "min_temp": min_t,
            "max_temp": max_t,
            "rainfall_min": rain_lo,
            "rainfall_max": rain_hi,
            "humidity_min": hum_lo,
            "humidity_max": hum_hi,
            "soil_types": soils,
            "soil_ph_min": ph_lo,
            "soil_ph_max": ph_hi,
        }
    finally:
        await conn.close()


def _build_reason_slides(
    crop_name: str,
    req: dict,
    actual: dict,
    suitable: bool,
) -> List[dict]:
    """Build slide-by-slide reasons (temperature, rainfall, humidity, soil)."""
    slides = []
    temp_ok = req["min_temp"] <= actual.get("temp", 0) <= req["max_temp"]
    slides.append({
        "title": "Temperature",
        "required": f"{req['min_temp']:.1f}°C - {req['max_temp']:.1f}°C",
        "actual": f"{actual.get('temp', 0):.1f}°C",
        "suitable": temp_ok,
        "message": f"Your location has {actual.get('temp', 0):.1f}°C. {crop_name} grows well between {req['min_temp']:.1f}°C and {req['max_temp']:.1f}°C."
        if temp_ok else f"Temperature at your location ({actual.get('temp', 0):.1f}°C) is outside the ideal range for {crop_name} ({req['min_temp']:.1f}°C - {req['max_temp']:.1f}°C).",
    })
    rain = actual.get("rainfall_mm", actual.get("rainfall", 800))
    rain_ok = req["rainfall_min"] <= rain <= req["rainfall_max"] * 1.2 or req["rainfall_min"] <= rain
    slides.append({
        "title": "Rainfall",
        "required": f"{req['rainfall_min']:.0f} - {req['rainfall_max']:.0f} mm",
        "actual": f"{rain:.0f} mm (annual estimate)",
        "suitable": rain_ok,
        "message": f"Rainfall is suitable for {crop_name} in your region."
        if rain_ok else f"Rainfall may be outside the ideal range for {crop_name}. Consider irrigation.",
    })
    hum = actual.get("humidity", 60)
    hum_ok = req["humidity_min"] <= hum <= req["humidity_max"] * 1.1
    slides.append({
        "title": "Humidity",
        "required": f"{req['humidity_min']:.0f}% - {req['humidity_max']:.0f}%",
        "actual": f"{hum:.0f}%",
        "suitable": hum_ok,
        "message": f"Humidity ({hum:.0f}%) is within the suitable range for {crop_name}."
        if hum_ok else f"Humidity may need to be considered for {crop_name}.",
    })
    soil_ok = actual.get("soil_type", "Loamy") in req["soil_types"]
    slides.append({
        "title": "Soil Type",
        "required": ", ".join(req["soil_types"]),
        "actual": actual.get("soil_type", "Loamy"),
        "suitable": soil_ok,
        "message": f"Soil type {actual.get('soil_type', 'Loamy')} is suitable for {crop_name}."
        if soil_ok else f"{crop_name} typically prefers {', '.join(req['soil_types'])}. Your area has {actual.get('soil_type', 'Loamy')}.",
    })
    return slides


async def predict_suitability(
    crop_name: str,
    temp: float,
    rainfall: float,
    humidity: float,
    wind_speed: float,
    soil_type: str,
    soil_ph: float = 7.0,
) -> Tuple[bool, List[dict], List[str]]:
    """
    Returns: (is_suitable, reason_slides, alternative_crops).
    Uses ML model if available, else rule-based from requirements.
    """
    model, encoders = _load_model()
    req = await get_crop_requirements(crop_name)
    actual = {
        "temp": temp,
        "rainfall": rainfall,
        "rainfall_mm": rainfall,
        "humidity": humidity,
        "soil_type": soil_type,
    }
    if not req:
        return False, [], await get_recommended_crops(temp, rainfall, humidity, soil_type)

    if model and encoders:
        try:
            le = encoders["soil"]
            soil_enc = le.transform([soil_type])[0] if soil_type in le.classes_ else 0
            import numpy as np
            X = np.array([[temp, temp + 5, rainfall, humidity, wind_speed, soil_ph, soil_enc]])
            pred = model.predict(X)
            suitable = bool(pred[0])
        except Exception:
            suitable = (
                req["min_temp"] <= temp <= req["max_temp"]
                and req["humidity_min"] <= humidity <= req["humidity_max"] * 1.2
                and soil_type in req["soil_types"]
            )
    else:
        suitable = (
            req["min_temp"] <= temp <= req["max_temp"]
            and req["humidity_min"] <= humidity <= req["humidity_max"] * 1.2
            and soil_type in req["soil_types"]
        )
    # Align with best crops: if crop is recommended for these conditions, treat as suitable
    recommended = await get_recommended_crops(temp, rainfall, humidity, soil_type, limit=50)
    if any((c or "").strip().lower() == crop_name.strip().lower() for c in recommended):
        suitable = True

    slides = _build_reason_slides(crop_name, req, actual, suitable)
    alternatives = await get_recommended_crops(temp, rainfall, humidity, soil_type, exclude_crop=crop_name) if not suitable else []
    return suitable, slides, alternatives


async def get_recommended_crops(
    temp: float,
    rainfall: float,
    humidity: float,
    soil_type: str,
    exclude_crop: Optional[str] = None,
    limit: int = 10,
) -> List[str]:
    """Recommend crops suitable for given conditions from dataset (Suitable=Y)."""
    conn = await aiosqlite.connect(DB_PATH)
    try:
        sql = """SELECT DISTINCT crop_name FROM crop_data
                 WHERE suitable = 'Y'
                 AND min_temp <= ? AND max_temp >= ?
                 AND rainfall <= ? AND rainfall >= ?
                 AND humidity <= ? AND humidity >= ?
                 AND soil_type = ?
                 LIMIT ?"""
        params = [temp + 5, temp - 5, rainfall + 400, rainfall - 400, humidity + 25, humidity - 25, soil_type, limit + 20]
        cur = await conn.execute(sql, params)
        rows = await cur.fetchall()
        names = [r[0] for r in rows]
        if exclude_crop:
            names = [n for n in names if n.strip().lower() != exclude_crop.strip().lower()]
        return names[:limit]
    finally:
        await conn.close()


def _infer_season_from_month(month: int) -> tuple:
    """India: Kharif Jun-Oct, Rabi Nov-Mar, Zaid Apr-May. Returns (season_name, description)."""
    if month >= 6 and month <= 10:
        return ("Kharif", "Monsoon season (Jun–Oct). Suitable for rice, maize, cotton, etc.")
    if month >= 11 or month <= 3:
        return ("Rabi", "Winter season (Nov–Mar). Suitable for wheat, barley, mustard, etc.")
    return ("Zaid", "Summer season (Apr–May). Short-duration crops like watermelon, cucumber.")


async def get_best_crops(
    lat: float,
    lon: float,
    state: Optional[str],
    district: Optional[str],
    limit: int = 15,
) -> dict:
    """Best crops for location + current season/forecast. Returns crops, season, location_data."""
    from weather import get_weather, get_soil_type_for_region
    import datetime
    weather = await get_weather(lat, lon)
    soil_type = await get_soil_type_for_region(state, district)
    rainfall_mm = weather.get("rain_1h_mm", 0) * 24 * 365 if weather.get("rain_1h_mm") else 800.0
    temp = weather.get("temp", 25)
    humidity = weather.get("humidity", 60)
    month = datetime.datetime.utcnow().month
    season_name, season_description = _infer_season_from_month(month)
    crops = await get_recommended_crops(temp, rainfall_mm, humidity, soil_type, limit=limit)
    # Prefer crops that match current season in dataset
    conn = await aiosqlite.connect(DB_PATH)
    try:
        cur = await conn.execute(
            """SELECT DISTINCT crop_name FROM crop_data
               WHERE suitable = 'Y' AND season IN (?, 'Annual')
               AND min_temp <= ? AND max_temp >= ?
               AND soil_type = ?
               LIMIT ?""",
            (season_name, temp + 5, temp - 5, soil_type, limit),
        )
        rows = await cur.fetchall()
        season_crops = [r[0] for r in rows]
        if season_crops:
            # Put season-matching crops first, then fill with rest
            rest = [c for c in crops if c not in season_crops]
            crops = season_crops[:limit] + rest
            crops = list(dict.fromkeys(crops))[:limit]
    finally:
        await conn.close()
    return {
        "crops": crops,
        "season": season_name,
        "season_description": season_description,
        "location_data": {
            "temperature_c": temp,
            "rainfall_mm": rainfall_mm,
            "humidity_percent": humidity,
            "soil_type": soil_type,
        },
    }

