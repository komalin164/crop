# Project Report: Crop Suitability System

**A Location-Based Crop Recommendation System for Farmers**

---

## Abstract

Agriculture plays a crucial role in the Indian economy, especially in states like Andhra Pradesh and Telangana, where many farmers depend on crop production for their livelihood. Farmers often face challenges in selecting suitable crops due to changing weather conditions, soil variations, and lack of real-time information. To address this issue, the proposed system is a web and mobile application that provides crop recommendations based on the user's current geographical location.

The application automatically detects the farmer's location using GPS and collects environmental data such as temperature, rainfall, and humidity through APIs like OpenWeather, along with soil information from the dataset. By comparing these parameters with predefined crop requirements stored in the system, the application determines crop suitability for that region. The solution helps farmers make informed decisions, reduce crop failure risks, and improve agricultural productivity through a simple and user-friendly interface.

---

## 1. Introduction

### 1.1 Background

Farmers in India often struggle with crop selection due to:
- Unpredictable weather patterns
- Regional soil variations
- Lack of access to real-time agricultural advisory
- Limited awareness of season-appropriate crops (Kharif, Rabi, Zaid)

### 1.2 Objectives

- Provide location-based crop suitability analysis
- Recommend best crops for the user's area and current season
- Explain suitability with slide-by-slide reasons (temperature, rainfall, humidity, soil type)
- Suggest alternative crops when the chosen crop is not suitable
- Support multiple platforms: Flutter (mobile + web) and React (web)

---

## 2. System Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Flutter App    │     │   React App     │     │                 │
│  (Mobile/Web)   │     │   (Vite+Tailwind)│     │                 │
└────────┬────────┘     └────────┬────────┘     │                 │
         │                        │              │   Python        │
         │    HTTP/REST API       │              │   Backend       │
         └────────────────────────┼──────────────►  (FastAPI)      │
                                  │              │                 │
                                  │              │  - Auth (JWT)   │
                                  │              │  - Crop Check   │
                                  │              │  - Best Crops   │
                                  │              │  - ML Model     │
                                  │              └────────┬────────┘
                                  │                       │
                                  │              ┌───────▼───────┐
                                  │              │  SQLite DB     │
                                  │              │  (crop_data,   │
                                  │              │   users)       │
                                  │              └───────┬───────┘
                                  │                       │
                                  │              ┌───────▼───────┐
                                  │              │ OpenWeather   │
                                  │              │ API (weather) │
                                  │              └───────────────┘
```

---

## 3. Modules

### 3.1 Backend (Python / FastAPI)

| Component      | Description |
|----------------|-------------|
| **main.py**    | FastAPI app, CORS, routes for auth and crop endpoints |
| **auth.py**    | User registration/login, bcrypt password hashing, JWT tokens |
| **weather.py**| OpenWeather API integration, soil type inference from dataset |
| **crop_service.py** | ML model (RandomForest), crop requirements, best crops (season-aware), slide-by-slide reasons |
| **load_dataset.py** | Loads dataset.csv into SQLite, trains sklearn model |
| **database.py** | SQLite schema (users, crop_data) |

### 3.2 Flutter App (Mobile + Web)

| Screen           | Description |
|------------------|-------------|
| Register         | Email OTP only (no mobile, no login) |
| Home             | Best crops, crop check, Fertilizer, Irrigation, Schemes, Admin |
| BestCropsScreen  | Shows recommended crops, current season, location conditions |
| CropResultScreen | Suitability result, slide-by-slide reasons, alternative crops |
| FertilizerScreen | NPK recommendation by crop, soil type, acreage |
| IrrigationScreen | Irrigation schedule by crop, rainfall, soil |
| SchemesScreen    | Government schemes in English/Telugu/Hindi |
| AdminScreen      | Analytics (users, crop records, top crops) |

### 3.3 React App (Vite + Tailwind CSS)

Same functionality as Flutter: Register (OTP), Home, CropResult, BestCrops, Fertilizer, Irrigation, Schemes, Admin pages with responsive Tailwind UI.

---

## 4. Features

### 4.1 User Authentication

- **Email OTP only**: No mobile, no password login. Enter email → OTP sent via SMTP → verify OTP to register/login.
- JWT-based session; tokens stored securely (Flutter: secure storage / SharedPreferences; React: localStorage)

### 4.2 Location-Based Analysis

- Requests location permission on home screen
- Uses GPS (lat/lon) for live location
- Fetches temperature, rainfall, humidity from OpenWeather API
- Infers soil type from dataset by state/district

### 4.3 Best Crops for My Location

- **No crop selection required**
- Uses current location and **season** (Kharif: Jun–Oct, Rabi: Nov–Mar, Zaid: Apr–May)
- Returns top recommended crops for the area
- Shows season description and location conditions

### 4.4 Check Crop Suitability

- User enters a crop name (e.g., Rice, Wheat, Tomato)
- System evaluates suitability using ML model and dataset
- **Slide-by-slide reasons**: Temperature, Rainfall, Humidity, Soil Type (required vs actual)
- If not suitable: shows **alternative crops** (excluding the requested crop)

### 4.5 Alternative Crop Recommendations

- When a crop is marked "not suitable," the system suggests other crops that match the location
- The requested crop is **never** shown in alternatives (e.g., Tomato not suitable → Tomato excluded from list)

---

## 5. Data Flow

### 5.1 Crop Check Flow

1. User enters crop name and taps "Check if suitable"
2. App sends `GET /crop/check?crop_name=Tomato&lat=...&lon=...`
3. Backend fetches weather (OpenWeather) and soil (dataset)
4. ML model / rules predict suitability
5. Backend builds slide-by-slide reasons and alternative crops
6. **Filter**: Requested crop is removed from alternatives before response
7. App displays result with reasons and alternatives

### 5.2 Best Crops Flow

1. User taps "Show best crops for my location"
2. App sends `GET /crop/best?lat=...&lon=...`
3. Backend infers season from current month
4. Fetches weather and soil
5. Queries dataset for crops matching location + season
6. Returns crops, season description, location data

---

## 6. Technology Stack

| Layer    | Technologies |
|----------|--------------|
| Backend  | Python 3.x, FastAPI, SQLite, scikit-learn, bcrypt, python-jose, httpx |
| Flutter  | Dart, Flutter, Provider, geolocator, geocoding, http |
| React    | React 18, Vite 5, Tailwind CSS 3, React Router 6 |
| Data     | dataset.csv (State, District, Crop, Season, Temp, Rainfall, Humidity, Soil, Suitable Y/N) |
| External | OpenWeather API (optional) |

---

## 7. API Documentation

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/auth/send-otp` | Send OTP to email |
| POST   | `/auth/register` | Verify OTP and register/login (email + otp) |
| GET    | `/crop/check`   | Check if crop is suitable; returns reasons + alternatives |
| GET    | `/crop/best`    | Best crops for location and current season |
| GET    | `/crop/recommendations` | List of recommended crops |
| GET    | `/fertilizer/recommend` | NPK recommendation by crop, soil type, acreage |
| GET    | `/irrigation/recommend` | Irrigation schedule by crop, rainfall, soil |
| GET    | `/schemes`      | Government schemes (PM-KISAN, Rythu Bharosa, etc.) in en/te/hi |
| GET    | `/analytics`    | Admin analytics (users, crop records, top crops) |
| POST   | `/disease/detect` | Disease detection from image (base64, crop_hint) |
| GET    | `/price/predict` | Price trend by crop (placeholder) |
| GET    | `/yield/predict` | Yield prediction by crop, rainfall |
| GET    | `/health`       | Health check |

---

## 8. Dataset

- **Source**: dataset.csv
- **Columns**: State, District, Crop_Name, Season, Min_Temperature, Max_Temperature, Rainfall, Humidity, Wind_Speed, Soil_Type, Soil_pH, Irrigation_Type, Suitable(Y/N)
- **Regions**: Andhra Pradesh, Telangana, and other Indian states
- **Crops**: Rice, Wheat, Maize, Cotton, Sugarcane, Soybean, Mustard, Potato, Onion, Tomato, Barley, Millets, Groundnut, Sunflower, Turmeric, Chilli, Pulses, Tea, Coffee, Jute

---

## 9. Bug Fix: Tomato in Recommendations

**Issue**: When Tomato was marked "not suitable," it still appeared in the alternative crops list.

**Cause**: The crop could match location conditions in some dataset rows (Suitable=Y) and slip through the exclusion filter in edge cases.

**Fix**: Added an explicit filter in `main.py` before returning the response to ensure the requested crop is never included in `alternative_crops`:

```python
crop_lower = crop_name.strip().lower()
alternatives = [c for c in alternatives if (c or "").strip().lower() != crop_lower]
```

---

## 10. Platform Upgrade Roadmap

This project has an evolved design document: **Smart Agriculture Platform for India** (`SMART_AGRI_PLATFORM.md`), which outlines the transformation into a production-ready, AI-powered AgriTech platform. Key planned enhancements include:

- **25+ advanced features**: Disease detection (image), yield/price prediction, irrigation & fertilizer engines, government scheme integration, AI chatbot, farmer marketplace
- **ML upgrades**: CNN for disease, LSTM for prices, ensemble models for yield; model retraining pipeline
- **Multilingual**: Telugu, Hindi, English
- **Cloud-ready**: Microservices, AWS/Azure deployment, Kubernetes
- **Farmer-focused**: Offline mode, push notifications, district heatmaps, admin analytics
- **Business model**: Freemium, B2B (FPOs), B2G, marketplace commissions

See **SMART_AGRI_PLATFORM.md** for the full design (architecture, modules, security, deployment, future scope).

---

## 11. Conclusion

The Crop Suitability System provides farmers with location and season-aware crop recommendations through a simple interface. It combines real-time weather data, historical crop requirements, and machine learning to support better agricultural decisions. The system is available on mobile (Flutter), web (Flutter and React), and has a documented upgrade path to a full-scale Smart Agriculture Platform for Andhra Pradesh, Telangana, and beyond.

---

## 12. References

- OpenWeather API: https://openweathermap.org/api
- FastAPI: https://fastapi.tiangolo.com
- Flutter: https://flutter.dev
- scikit-learn: https://scikit-learn.org
- Indian crop seasons: Kharif (monsoon), Rabi (winter), Zaid (summer)
