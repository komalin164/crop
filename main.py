"""FastAPI app: auth, crop check by location, slide-by-slide reasons, recommendations."""
import os
from contextlib import asynccontextmanager

import aiosqlite
from fastapi import Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, status
from pydantic import BaseModel
from typing import Optional

from config import DB_PATH
from database import init_db
from auth import send_otp, verify_otp_and_register, create_token, decode_token
from weather import get_weather, get_soil_type_for_region
from crop_service import predict_suitability, get_crop_requirements, get_best_crops
from fertilizer_service import get_fertilizer_recommendation
from irrigation_service import get_irrigation_recommendation
from schemes_service import get_schemes
from analytics_service import get_analytics
from disease_service import detect_disease_from_image
from price_service import get_price_prediction
from yield_service import get_yield_prediction


@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = await aiosqlite.connect(DB_PATH)
    await init_db(conn)
    await conn.close()
    yield
    # cleanup if any
    pass


app = FastAPI(title="Crop Suitability API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- Auth (email OTP only) ---
class SendOtpBody(BaseModel):
    email: str
    name: Optional[str] = None
    mobile: Optional[str] = None


class VerifyOtpBody(BaseModel):
    email: str
    otp: str
    name: Optional[str] = None
    mobile: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    email: Optional[str] = None
    mobile: Optional[str] = None
    name: Optional[str] = None


def get_current_user_id(authorization: Optional[str] = None) -> Optional[int]:
    if not authorization or not authorization.startswith("Bearer "):
        return None
    token = authorization.replace("Bearer ", "")
    payload = decode_token(token)
    if payload and "sub" in payload:
        return int(payload["sub"])
    return None


@app.post("/auth/send-otp")
async def auth_send_otp(body: SendOtpBody):
    result = await send_otp(body.email, name=body.name or "")
    if not result["sent"]:
        raise HTTPException(status_code=400, detail=result["message"])
    return result


@app.post("/auth/register", response_model=TokenResponse)
async def register(body: VerifyOtpBody):
    """Verify OTP and register/login. Creates user if new, returns token."""
    user = await verify_otp_and_register(
        body.email, body.otp, name=body.name or "", mobile=body.mobile or ""
    )
    if not user:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    token = create_token({"sub": str(user["id"])})
    return TokenResponse(
        access_token=token,
        user_id=user["id"],
        email=user.get("email"),
        mobile=user.get("mobile"),
        name=user.get("name"),
    )


# --- Crop check ---
class CropCheckQuery(BaseModel):
    crop_name: str
    lat: Optional[float] = None
    lon: Optional[float] = None
    state: Optional[str] = None
    district: Optional[str] = None


class CropCheckResponse(BaseModel):
    suitable: bool
    crop_name: str
    reasons: list  # slide-by-slide
    alternative_crops: list
    location_data: dict  # temp, rainfall, humidity, soil_type used


@app.get("/crop/check", response_model=CropCheckResponse)
async def crop_check(
    crop_name: str,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
):
    crop_name = (crop_name or "").strip()
    if not crop_name:
        raise HTTPException(status_code=400, detail="crop_name required")
    weather = await get_weather(lat or 0, lon or 0)
    soil_type = await get_soil_type_for_region(state, district)
    # Use annual rainfall estimate if we only have current weather (simplified: use 800 or from API)
    rainfall_mm = weather.get("rain_1h_mm", 0) * 24 * 365 if weather.get("rain_1h_mm") else 800.0
    temp = weather.get("temp", 25)
    humidity = weather.get("humidity", 60)
    wind_speed = weather.get("wind_speed_kmh", 10)
    suitable, reasons, alternatives = await predict_suitability(
        crop_name=crop_name,
        temp=temp,
        rainfall=rainfall_mm,
        humidity=humidity,
        wind_speed=wind_speed,
        soil_type=soil_type,
    )
    # Ensure the requested crop is never in alternatives (e.g. Tomato not suitable but was in list)
    crop_lower = crop_name.strip().lower()
    alternatives = [c for c in alternatives if (c or "").strip().lower() != crop_lower]
    return CropCheckResponse(
        suitable=suitable,
        crop_name=crop_name,
        reasons=reasons,
        alternative_crops=alternatives,
        location_data={
            "temperature_c": temp,
            "rainfall_mm": rainfall_mm,
            "humidity_percent": humidity,
            "soil_type": soil_type,
        },
    )


@app.get("/crop/recommendations")
async def recommendations(
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
):
    weather = await get_weather(lat or 0, lon or 0)
    soil_type = await get_soil_type_for_region(state, district)
    rainfall_mm = weather.get("rain_1h_mm", 0) * 24 * 365 if weather.get("rain_1h_mm") else 800.0
    from crop_service import get_recommended_crops
    crops = await get_recommended_crops(
        temp=weather.get("temp", 25),
        rainfall=rainfall_mm,
        humidity=weather.get("humidity", 60),
        soil_type=soil_type,
        limit=15,
    )
    return {"crops": crops}


@app.get("/crop/best")
async def best_crops(
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    state: Optional[str] = None,
    district: Optional[str] = None,
):
    """Best crops for your location and current season (forecast-based)."""
    data = await get_best_crops(
        lat=lat or 0,
        lon=lon or 0,
        state=state,
        district=district,
        limit=15,
    )
    return data


# --- Fertilizer ---
@app.get("/fertilizer/recommend")
async def fertilizer_recommend(
    crop_name: str,
    soil_type: str = "alluvial",
    soil_ph: Optional[float] = None,
    acreage: float = 1.0,
):
    return await get_fertilizer_recommendation(crop_name, soil_type, soil_ph, acreage)


# --- Irrigation ---
@app.get("/irrigation/recommend")
async def irrigation_recommend(
    crop_name: str,
    rainfall_mm: float = 800.0,
    soil_type: str = "alluvial",
    growth_stage: Optional[str] = None,
):
    return get_irrigation_recommendation(crop_name, rainfall_mm, soil_type, growth_stage)


# --- Government Schemes ---
@app.get("/schemes")
async def schemes(lang: str = "en"):
    """Get government schemes in en, te, or hi."""
    return {"schemes": get_schemes(lang)}


# --- Analytics (admin) ---
@app.get("/analytics")
async def analytics():
    return await get_analytics()


# --- Disease Detection ---
class DiseaseBody(BaseModel):
    image_base64: str
    crop_hint: Optional[str] = None


@app.post("/disease/detect")
async def disease_detect(body: DiseaseBody):
    return detect_disease_from_image(body.image_base64, body.crop_hint)


# --- Price Prediction ---
@app.get("/price/predict")
async def price_predict(crop_name: str, district: Optional[str] = None):
    return get_price_prediction(crop_name, district)


# --- Yield Prediction ---
@app.get("/yield/predict")
async def yield_predict(
    crop_name: str,
    district: Optional[str] = None,
    state: Optional[str] = None,
    rainfall_mm: float = 800.0,
):
    return await get_yield_prediction(crop_name, district, state, rainfall_mm)


@app.get("/geo/reverse")
async def geo_reverse(lat: float, lon: float):
    """Proxy for Nominatim reverse geocoding (avoids CORS when called from browser)."""
    import httpx
    url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json"
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers={"Accept-Language": "en", "User-Agent": "CropSuitability/1.0"})
        resp.raise_for_status()
        return resp.json()


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
