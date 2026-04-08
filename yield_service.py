"""Yield prediction from dataset and location conditions."""
import aiosqlite
from typing import Optional
from config import DB_PATH

# Typical yield range (kg/acre) by crop for AP/TG
CROP_YIELD_BASE = {
    "rice": 2500,
    "wheat": 2000,
    "maize": 3000,
    "cotton": 400,
    "sugarcane": 40000,
    "chilli": 1500,
    "groundnut": 1200,
    "tomato": 15000,
    "onion": 12000,
    "potato": 15000,
    "pulses": 600,
    "soybean": 1200,
    "mustard": 800,
}


async def get_yield_prediction(
    crop_name: str,
    district: Optional[str] = None,
    state: Optional[str] = None,
    rainfall_mm: float = 800,
) -> dict:
    crop_key = crop_name.strip().lower()
    base_yield = CROP_YIELD_BASE.get(crop_key, 1500)
    conn = await aiosqlite.connect(DB_PATH)
    try:
        cur = await conn.execute(
            """SELECT AVG(rainfall) as avg_rain FROM crop_data 
               WHERE LOWER(crop_name) = ? AND suitable = 'Y'""",
            (crop_key,),
        )
        row = await cur.fetchone()
        avg_rain = row[0] if row and row[0] else 800
        rain_factor = min(1.2, max(0.7, rainfall_mm / avg_rain))
        pred_yield = int(base_yield * rain_factor)
        return {
            "crop": crop_name,
            "predicted_yield_kg_per_acre": pred_yield,
            "confidence": "medium",
            "factors": {"rainfall_factor": round(rain_factor, 2), "base_yield": base_yield},
            "advice": "Yield depends on timely sowing, pest management and irrigation. Use recommended practices.",
        }
    finally:
        await conn.close()
