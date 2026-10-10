# Heart Disease Risk Prediction System

An educational heart-disease risk-screening web application using a Flask REST API, local SQLite storage by default, optional MongoDB Atlas support, and the supplied `heart_model.pkl` and `scaler.pkl` artifacts.

> This system provides an estimated risk category for educational/research screening only. It is not a medical diagnosis and must not replace advice from a qualified healthcare professional.

## Features

- Account registration, login, JWT authentication, and password hashing.
- Validated 13-feature heart-risk form.
- Existing model/scaler integration with fixed feature ordering.
- Configurable Low (0-39%), Medium (40-69%), and High (70-100%) categories.
- Prediction persistence and user-scoped history in local SQLite.
- Dashboard statistics and Chart.js risk distribution.
- Model feature-importance display when exposed by the selected estimator.
- Responsive static frontend and focused backend tests.

## Setup

1. Create and activate a Python 3.10+ virtual environment.
2. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

3. No MongoDB or `.env` setup is required for local mode.
4. Confirm that `MODEL_PATH` and `SCALER_PATH` point to compatible artifacts. The supplied artifacts are already in `models/`.

The default local mode stores users and predictions in `heart_risk_local.db`. MongoDB remains optional: set `MONGO_URI` in `.env` if you want to use Atlas.

## Run

### Easiest way on Windows

Double-click [start_project.bat](./start_project.bat). It opens the backend, frontend, and browser automatically.

### Manual way

From the `backend` directory:

```powershell
python run.py
```

The API runs at `http://127.0.0.1:5000`. Serve `frontend` with:

```powershell
python -m http.server 5500 --directory frontend
```

Open `http://127.0.0.1:5500`.

## API

- `POST /api/auth/register`
- `POST /api/auth/login`
- `POST /api/auth/logout`
- `GET /api/auth/me`
- `GET /api/user/profile`
- `PUT /api/user/profile`
- `POST /api/prediction/heart`
- `GET /api/prediction/history`
- `GET /api/prediction/<prediction_id>`
- `GET /api/health`

Protected endpoints require `Authorization: Bearer <token>`.

## ML integration

The API validates and orders features as:

`age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal`

It applies the supplied scaler before invoking the supplied model. Replace both artifacts together if they were trained with a different feature order or encoding. `backend/app/ml_engine/train.py` provides a comparison scaffold for Logistic Regression, Random Forest, and SVM using a UCI-style CSV with a `target` column. It reports accuracy, precision, recall, F1, and ROC-AUC and selects by ROC-AUC; no performance claims are made for the supplied artifacts.

Risk thresholds are application categories, not clinical thresholds, and can be changed with `LOW_RISK_MAX` and `MEDIUM_RISK_MAX`.

## MongoDB collections

- `users`: name, unique email, password hash, created timestamp.
- `health_profiles`: optional future profile data.
- `predictions`: user-scoped input, probability, risk level, model metadata, and timestamp.
- `model_logs`: aggregate model metrics only; do not store patient information.

Indexes are created automatically when MongoDB mode is enabled. Local mode uses SQLite tables in `heart_risk_local.db`.

## Testing

```powershell
pytest backend/tests
```

The tests cover input validation and the health endpoint without requiring a live MongoDB connection.

## Limitations

This is Version 1 for heart disease only. It does not establish clinical validity, replace clinician review, or guarantee model performance. Future disease predictors can be added behind separate service modules and endpoints without exposing MongoDB to the browser.