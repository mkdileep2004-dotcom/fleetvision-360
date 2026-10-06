import pandas as pd
import os

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ==========================================
# 1. LOAD DATA
# ==========================================

X = pd.read_csv("data/ml/eta_features.csv")

y = pd.read_csv("data/ml/eta_target.csv").squeeze()

print("\n========== DATA LOADED ==========")
print("Features:", X.shape)
print("Target:", y.shape)


# ==========================================
# 2. IDENTIFY COLUMNS
# ==========================================

categorical_features = [
    "vehicle_type",
    "manufacturer",
    "fuel_type"
]

numerical_features = [
    "distance_km",
    "route_distance_km",
    "estimated_time_minutes",
    "capacity_kg",
    "age",
    "experience_years",
    "order_month",
    "order_day_of_week",
    "is_weekend"
]


# ==========================================
# 3. PREPROCESSING
# ==========================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(handle_unknown="ignore"),
            categorical_features
        ),
        (
            "numerical",
            "passthrough",
            numerical_features
        )
    ]
)


# ==========================================
# 4. CREATE RANDOM FOREST MODEL
# ==========================================

model = RandomForestRegressor(
    n_estimators=200,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)


# ==========================================
# 5. CREATE PIPELINE
# ==========================================

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)


# ==========================================
# 6. TRAIN / TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)


print("\n========== TRAIN / TEST DATA ==========")

print("Training rows:", len(X_train))
print("Testing rows:", len(X_test))


# ==========================================
# 7. TRAIN MODEL
# ==========================================

print("\n========== TRAINING MODEL ==========")

pipeline.fit(X_train, y_train)

print("Model training completed!")


# ==========================================
# 8. MAKE PREDICTIONS
# ==========================================

y_pred = pipeline.predict(X_test)


# ==========================================
# 9. MODEL EVALUATION
# ==========================================

mae = mean_absolute_error(y_test, y_pred)

rmse = mean_squared_error(
    y_test,
    y_pred
) ** 0.5

r2 = r2_score(
    y_test,
    y_pred
)


print("\n========== MODEL PERFORMANCE ==========")

print("MAE :", round(mae, 4))
print("RMSE:", round(rmse, 4))
print("R²  :", round(r2, 4))


# ==========================================
# 10. SAVE MODEL
# ==========================================

import joblib

os.makedirs("ml/models", exist_ok=True)

model_file = "ml/models/eta_model.pkl"

joblib.dump(
    pipeline,
    model_file
)


print("\n=========================================")
print("ETA MODEL SAVED SUCCESSFULLY!")
print("Model:", model_file)
print("=========================================")