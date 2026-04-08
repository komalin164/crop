"""Fertilizer recommendation based on crop, soil type, and optional soil test."""
import aiosqlite
from typing import Optional
from config import DB_PATH

# NPK recommendations (kg/acre) by crop - simplified from FCO guidelines
CROP_NPK = {
    "rice": {"N": 80, "P": 40, "K": 40, "split": "3 splits: basal, tillering, panicle"},
    "wheat": {"N": 120, "P": 60, "K": 40, "split": "3 splits: basal, crown root, flowering"},
    "maize": {"N": 120, "P": 60, "K": 40, "split": "3 splits: basal, knee-high, tasseling"},
    "cotton": {"N": 80, "P": 40, "K": 40, "split": "4 splits: basal, squaring, flowering, boll"},
    "sugarcane": {"N": 250, "P": 80, "K": 80, "split": "4-5 splits through growth"},
    "soybean": {"N": 20, "P": 60, "K": 40, "split": "Basal P+K; N at flowering if needed"},
    "mustard": {"N": 80, "P": 40, "K": 40, "split": "2 splits: basal, rosette"},
    "potato": {"N": 120, "P": 80, "K": 120, "split": "Basal + top dressing at tuberization"},
    "onion": {"N": 60, "P": 40, "K": 40, "split": "3 splits: transplant, 30d, 60d"},
    "tomato": {"N": 100, "P": 80, "K": 80, "split": "Basal + top dress every 15d"},
    "chilli": {"N": 100, "P": 80, "K": 80, "split": "Basal + top dress at flowering"},
    "groundnut": {"N": 20, "P": 40, "K": 40, "split": "Basal; Rhizobium for N"},
    "pulses": {"N": 20, "P": 40, "K": 20, "split": "Basal; Rhizobium inoculation"},
    "millets": {"N": 40, "P": 40, "K": 20, "split": "Basal application"},
    "barley": {"N": 60, "P": 40, "K": 20, "split": "2 splits: basal, tillering"},
    "sunflower": {"N": 60, "P": 40, "K": 40, "split": "Basal + at 30d"},
    "turmeric": {"N": 60, "P": 40, "K": 80, "split": "3 splits during growth"},
    "tea": {"N": 100, "P": 40, "K": 60, "split": "Quarterly applications"},
    "coffee": {"N": 100, "P": 40, "K": 80, "split": "Pre-monsoon + post-monsoon"},
    "jute": {"N": 40, "P": 20, "K": 20, "split": "2 splits: 3 weeks, 6 weeks"},
}


async def get_fertilizer_recommendation(
    crop_name: str,
    soil_type: str,
    soil_ph: Optional[float] = None,
    acreage: float = 1.0,
) -> dict:
    crop_key = crop_name.strip().lower()
    rec = CROP_NPK.get(crop_key)
    if not rec:
        rec = {"N": 80, "P": 40, "K": 40, "split": "Apply as per local advisory"}
    n, p, k = rec["N"], rec["P"], rec["K"]
    if soil_ph:
        if soil_ph < 5.5:
            n, p, k = int(n * 0.9), int(p * 1.1), int(k * 1.1)
        elif soil_ph > 8.0:
            n, p, k = int(n * 1.1), int(p * 0.9), int(k * 0.9)
    n, p, k = int(n * acreage), int(p * acreage), int(k * acreage)
    return {
        "crop": crop_name,
        "soil_type": soil_type,
        "npk_kg_per_acre": {"N": n, "P": p, "K": k},
        "application_schedule": rec["split"],
        "products": [
            f"Urea (46% N): ~{int(n * 2.17)} kg for {acreage} acre",
            f"DAP (18-46-0): ~{int(p * 2.17)} kg for P",
            f"MOP (0-0-60): ~{int(k * 1.67)} kg for K",
        ],
    }
