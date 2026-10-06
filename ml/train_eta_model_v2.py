import pandas as pd
import os
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ==========================================
# 1. LOAD REALISTIC ETA DATA
# ==========================================

df = pd.read_csv(
    "data/ml/eta_training_data_realistic.csv"
)

print("\n========== DATA LOADED ==========")
print("Rows:", len(df))


# ==========================================
# 2. CREATE FEATURES
# ==========================================

df["order_date"] = pd.to_datetime(
    df["order_date"]
)

df["order_month"] = df["order_date"].dt.month

df["order_day_of_week"] = (
    df["order_date"].dt.dayofweek
)

df["is_weekend"] = (
    df["order_day_of_week"] >= 5
).astype(int)


features = [
    "distance_km",
    "route_distance_km",
    "estimated_time_minutes",
    "capacity_kg",
    "age",
    "experience_years",
    "order_month",
    "order_day_of_week",
    "is_weekend",
    "vehicle_type",
    "manufacturer",
    "fuel_type"
]

X = df[features]

y = df["delivery_days"]


# ==========================================
# 3. CATEGORICAL / NUMERICAL FEATURES
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
# 4. PREPROCESSING
# ==========================================

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
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
# 5. RANDOM FOREST
# ==========================================

model = RandomForestRegressor(
    n_estimators=200,
    max_depth=15,
    random_state=42,
    n_jobs=-1
)


# ==========================================
# 6. PIPELINE
# ==========================================

pipeline = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("model", model)
    ]
)


# ==========================================
# 7. TRAIN / TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print("\n========== TRAIN / TEST ==========")
print("Training rows:", len(X_train))
print("Testing rows:", len(X_test))


# ==========================================
# 8. TRAIN
# ==========================================

print("\n========== TRAINING ==========")

pipeline.fit(
    X_train,
    y_train
)

print("Training completed!")


# ==========================================
# 9. PREDICTIONS
# ==========================================

y_pred = pipeline.predict(X_test)


# ==========================================
# 10. EVALUATION
# ==========================================

mae = mean_absolute_error(
    y_test,
    y_pred
)

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
# 11. SAVE MODEL
# ==========================================

os.makedirs(
    "ml/models",
    exist_ok=True
)

model_file = "ml/models/eta_model_v2.pkl"

joblib.dump(
    pipeline,
    model_file
)


print("\n=========================================")
print("IMPROVED ETA MODEL SAVED!")
print("Model:", model_file)
print("=========================================")