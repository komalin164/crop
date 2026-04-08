"""Irrigation recommendation based on crop, stage, rainfall, and soil."""
from typing import Optional
from datetime import datetime

# Crop water need (mm) and critical stages
CROP_WATER = {
    "rice": {"total_mm": 1200, "critical": ["tillering", "flowering", "grain filling"], "interval_days": 3},
    "wheat": {"total_mm": 400, "critical": ["crown root", "flowering", "milking"], "interval_days": 7},
    "maize": {"total_mm": 500, "critical": ["knee-high", "tasseling", "grain fill"], "interval_days": 7},
    "cotton": {"total_mm": 700, "critical": ["squaring", "flowering", "boll"], "interval_days": 5},
    "sugarcane": {"total_mm": 1500, "critical": ["tillering", "grand growth"], "interval_days": 5},
    "tomato": {"total_mm": 600, "critical": ["flowering", "fruit set"], "interval_days": 4},
    "chilli": {"total_mm": 500, "critical": ["flowering", "fruit development"], "interval_days": 5},
    "groundnut": {"total_mm": 500, "critical": ["flowering", "peg penetration"], "interval_days": 7},
    "onion": {"total_mm": 350, "critical": ["bulb formation"], "interval_days": 5},
    "potato": {"total_mm": 500, "critical": ["tuberization", "bulking"], "interval_days": 5},
}


def get_irrigation_recommendation(
    crop_name: str,
    rainfall_mm: float,
    soil_type: str,
    growth_stage: Optional[str] = None,
) -> dict:
    crop_key = crop_name.strip().lower()
    rec = CROP_WATER.get(crop_key, {"total_mm": 500, "critical": ["flowering"], "interval_days": 7})
    total = rec["total_mm"]
    deficit = max(0, total - rainfall_mm)
    soil_factor = 1.2 if soil_type.lower() in ("sandy", "red") else 1.0
    irrigation_mm = int(deficit * soil_factor * 0.3)
    return {
        "crop": crop_name,
        "rainfall_received_mm": rainfall_mm,
        "estimated_deficit_mm": int(deficit),
        "recommended_irrigation_mm": irrigation_mm,
        "interval_days": rec["interval_days"],
        "critical_stages": rec["critical"],
        "advice": f"Apply {irrigation_mm} mm every {rec['interval_days']} days. Critical stages: {', '.join(rec['critical'])}. Use drip for water saving.",
    }
