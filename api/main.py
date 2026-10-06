from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib


# ==========================================
# 1. CREATE FASTAPI APP
# ==========================================

app = FastAPI(
    title="FleetVision 360 API",
    description="Fleet management and ETA prediction API",
    version="1.0.0"
)


# ==========================================
# 2. LOAD ML MODEL
# ==========================================

model = joblib.load(
    "ml/models/eta_model_v2.pkl"
)


# ==========================================
# 3. INPUT DATA MODEL
# ==========================================

class ETAPredictionRequest(BaseModel):

    distance_km: float
    route_distance_km: float
    estimated_time_minutes: float
    capacity_kg: float
    age: int
    experience_years: float
    order_month: int
    order_day_of_week: int
    is_weekend: int
    vehicle_type: str
    manufacturer: str
    fuel_type: str


# ==========================================
# 4. HOME ENDPOINT
# ==========================================

@app.get("/")
def home():

    return {
        "message": "FleetVision 360 API is running"
    }


# ==========================================
# 5. ETA PREDICTION ENDPOINT
# ==========================================

@app.post("/predict-eta")
def predict_eta(
    request: ETAPredictionRequest
):

    input_data = pd.DataFrame([
        {
            "distance_km": request.distance_km,
            "route_distance_km": request.route_distance_km,
            "estimated_time_minutes": request.estimated_time_minutes,
            "capacity_kg": request.capacity_kg,
            "age": request.age,
            "experience_years": request.experience_years,
            "order_month": request.order_month,
            "order_day_of_week": request.order_day_of_week,
            "is_weekend": request.is_weekend,
            "vehicle_type": request.vehicle_type,
            "manufacturer": request.manufacturer,
            "fuel_type": request.fuel_type
        }
    ])


    prediction = model.predict(
        input_data
    )[0]


    return {
        "predicted_delivery_days": round(
            float(prediction),
            2
        )
    }