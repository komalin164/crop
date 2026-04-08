"""Fetch weather from OpenWeatherMap and infer soil from dataset."""
from typing import Optional
import httpx
import aiosqlite

from config import OPENWEATHER_API_KEY, DB_PATH


async def get_weather(lat: float, lon: float) -> dict:
    """Get current weather from OpenWeatherMap. Returns temp (C), humidity (%), wind (m/s->km/h), rain (mm)."""
    if not lat or not lon:
        return _default_weather()
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": OPENWEATHER_API_KEY, "units": "metric"}
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(url, params=params)
            if r.status_code != 200:
                return _default_weather()
            d = r.json()
            main = d.get("main", {})
            wind = d.get("wind", {})
            rain = d.get("rain", {}) or {}
            return {
                "temp": main.get("temp", 25),
                "temp_min": main.get("temp_min", 20),
                "temp_max": main.get("temp_max", 30),
                "humidity": main.get("humidity", 60),
                "wind_speed_kmh": (wind.get("speed") or 0) * 3.6,
                "rain_1h_mm": rain.get("1h") or rain.get("3h") or 0,
            }
    except Exception:
        return _default_weather()


def _default_weather():
    return {
        "temp": 25,
        "temp_min": 20,
        "temp_max": 30,
        "humidity": 60,
        "wind_speed_kmh": 10,
        "rain_1h_mm": 0,
    }


async def get_rainfall_annual_estimate(lat: float, lon: float) -> float:
    """Rough annual rainfall from one call: use current rain as proxy or default."""
    w = await get_weather(lat, lon)
    return w.get("rain_1h_mm", 0) * 24 * 365 if w.get("rain_1h_mm") else 800.0


async def get_soil_type_for_region(state: Optional[str] = None, district: Optional[str] = None) -> str:
    """Get most common soil type for state/district from dataset."""
    if not state and not district:
        return "Loamy"
    conn = await aiosqlite.connect(DB_PATH)
    try:
        if state and district:
            cur = await conn.execute(
                "SELECT soil_type FROM crop_data WHERE state = ? AND district = ? LIMIT 50",
                (state, district),
            )
        elif state:
            cur = await conn.execute(
                "SELECT soil_type FROM crop_data WHERE state = ? LIMIT 100",
                (state,),
            )
        else:
            return "Loamy"
        rows = await cur.fetchall()
        if not rows:
            return "Loamy"
        from collections import Counter
        counts = Counter(r[0] for r in rows)
        return counts.most_common(1)[0][0]
    finally:
        await conn.close()
