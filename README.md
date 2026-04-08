# Crop Suitability System

**A Location-Based Crop Recommendation System for Farmers** (Andhra Pradesh & Telangana)

Flutter mobile + web app and React web app with a Python backend for crop recommendations based on location (temperature, rainfall, humidity, soil). Uses `dataset.csv` and OpenWeather API for live weather. Farming-themed UI with location name display.

## Features

- **Auth**: Email OTP only (no mobile, no password). Enter email → receive OTP → verify to access.
- **Home**: Two options — (1) **Get best crops for my location** (no crop selection; uses location + current season), (2) **Check if a specific crop is suitable** (enter crop name)
- **Location**: App asks for location permission; uses GPS for live location
- **Best crops**: Season-based (Kharif/Rabi/Zaid) and forecast-based recommendations for your area
- **Suitability**: Based on location → temperature, rainfall, humidity, soil type (from OpenWeather + dataset)
- **Slide-by-slide reasons**: Temperature, rainfall, humidity, soil type with required vs actual
- **Recommendations**: If the chosen crop is not suitable, other crops for your area are suggested (requested crop excluded)
- **UI**: Farming-themed backgrounds, location name with lat/lon

## Backend (Python)

### Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate   # Windows
# pip install -r requirements.txt
pip install fastapi uvicorn python-jose[cryptography] passlib[bcrypt] python-multipart httpx pandas scikit-learn aiosqlite pydantic
```

### Load dataset and train model (run once)

```bash
cd backend
python load_dataset.py
```

This creates `crop.db` (SQLite), fills it from `dataset.csv`, and trains the RandomForest model (`crop_model.pkl`).

### Optional: OpenWeather API

For live weather, get a free API key from [OpenWeatherMap](https://openweathermap.org/api) and set:

```bash
set OPENWEATHER_API_KEY=your_key_here
```

If not set, the API uses default values (e.g. 25°C, 60% humidity, 800 mm rainfall). Use a `.env` file in `backend/` with `OPENWEATHER_API_KEY=your_key` (see `.env.example`).

### Email (OTP)

For OTP verification, set in `backend/.env`:

```
MAIL_SERVER=mail.heeltech.in
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=ai@heeltech.in
MAIL_PASSWORD=your_password
MAIL_DEFAULT_SENDER=ai@heeltech.in
```

### Run API

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

## Flutter app (mobile + web)

### Install Flutter (if needed)

1. Download: https://docs.flutter.dev/get-started/install/windows  
2. Extract and add `flutter\bin` to your PATH.  
3. Run `flutter doctor` and fix any issues. For Android: `flutter doctor --android-licenses`.

See **crop_app/ANDROID_SETUP.md** for detailed Android device/emulator and run steps.

### Setup

```bash
cd crop_app
flutter pub get
```

### Run on Android

```bash
cd crop_app
flutter run -d android
```

Use a connected device or a running emulator. To build an APK: `flutter build apk`.

### Run on Web

```bash
flutter run -d chrome
```

### Backend URL

Edit `crop_app/lib/services/api.dart` and set `baseUrl`:

- **Emulator**: `http://10.0.2.2:8000` (Android emulator’s alias for host)
- **Physical device**: Your PC’s LAN IP, e.g. `http://192.168.1.5:8000` (same Wi‑Fi as phone)
- **Web (same machine)**: `http://localhost:8000`

## React app (Vite + Tailwind)

Same features as Flutter: login/register, best crops for location, check crop suitability.

```bash
cd react-crop
npm install
npm run dev
```

Open http://localhost:5173. Set `VITE_API_URL` in `.env` if the backend is not on localhost:8000. See **react-crop/README.md**.

## Project structure

```
crop/
├── dataset.csv
├── backend/
│   ├── main.py           # FastAPI (auth, /crop/check, /crop/best, /crop/recommendations)
│   ├── auth.py
│   ├── weather.py
│   ├── crop_service.py   # ML + best crops (season-aware) + reasons
│   ├── load_dataset.py
│   ├── database.py
│   ├── config.py
│   └── requirements.txt
├── crop_app/             # Flutter (mobile + web)
│   ├── lib/screens/      # login, register, home, crop_result, best_crops_screen
│   ├── lib/widgets/      # FarmingBackground
│   └── ...
├── react-crop/           # React + Vite + Tailwind
│   └── src/pages/        # Login, Register, Home, CropResult, BestCrops
├── PROJECT_REPORT.md     # Project report
└── SMART_AGRI_PLATFORM.md # Upgrade design (25+ features, AI/ML, cloud)
```

## API summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/send-otp` | Send OTP to email |
| POST | `/auth/register` | Verify OTP and register (email + otp) |
| GET | `/crop/check?crop_name=&lat=&lon=&state=&district=` | Suitability + reasons + alternatives |
| GET | `/crop/best?lat=&lon=&state=&district=` | Best crops for location + current season |
| GET | `/crop/recommendations?lat=&lon=&state=&district=` | List of recommended crops |
| GET | `/fertilizer/recommend?crop_name=&soil_type=&acreage=` | NPK recommendation |
| GET | `/irrigation/recommend?crop_name=&rainfall_mm=&soil_type=` | Irrigation schedule |
| GET | `/schemes?lang=en` | Government schemes (en/te/hi) |
| GET | `/analytics` | Admin analytics |
| POST | `/disease/detect` | Disease detection (image base64) |
| GET | `/price/predict?crop_name=` | Price trend |
| GET | `/yield/predict?crop_name=&rainfall_mm=` | Yield prediction |

## Documentation

| Document | Description |
|----------|-------------|
| [PROJECT_REPORT.md](PROJECT_REPORT.md) | Full project report (abstract, architecture, modules, API, dataset) |
| [SMART_AGRI_PLATFORM.md](SMART_AGRI_PLATFORM.md) | Upgrade design: 25+ features, AI/ML enhancements, cloud architecture, business model, deployment |
