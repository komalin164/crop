"""Price prediction placeholder - returns trend based on crop (mock until e-NAM/real data)."""
import random
from typing import Optional
import random

# Mock MSP and typical mandi range (Rs/quintal) for AP/TG
CROP_PRICES = {
    "rice": {"msp": 2183, "min": 2000, "max": 2800},
    "wheat": {"msp": 2125, "min": 1900, "max": 2600},
    "maize": {"msp": 2090, "min": 1800, "max": 2400},
    "cotton": {"msp": 6620, "min": 5500, "max": 7500},
    "chilli": {"msp": 0, "min": 8000, "max": 15000},
    "groundnut": {"msp": 5850, "min": 5000, "max": 7000},
    "tomato": {"msp": 0, "min": 500, "max": 3000},
    "sugarcane": {"msp": 315, "min": 280, "max": 350},
}


def get_price_prediction(crop_name: str, district: Optional[str] = None) -> dict:
    crop_key = crop_name.strip().lower()
    prices = CROP_PRICES.get(crop_key, {"msp": 0, "min": 1000, "max": 3000})
    base = (prices["min"] + prices["max"]) // 2
    trend = random.uniform(-0.05, 0.08)
    pred_30 = int(base * (1 + trend))
    pred_60 = int(base * (1 + trend * 1.5))
    return {
        "crop": crop_name,
        "current_estimate": base,
        "prediction_30_days": pred_30,
        "prediction_60_days": pred_60,
        "msp": prices.get("msp"),
        "advice": "Sell when price is above MSP. Monitor mandi prices. Use e-NAM for better price discovery.",
        "note": "Placeholder. Integrate e-NAM/AGMARKNET API for real-time prices.",
    }
