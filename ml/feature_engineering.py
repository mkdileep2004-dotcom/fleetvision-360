import pandas as pd
import os


# ==========================================
# 1. LOAD ETA DATASET
# ==========================================

input_file = "data/ml/eta_training_data.csv"

df = pd.read_csv(input_file)

print("\n========== DATA LOADED ==========")
print("Rows:", len(df))
print("Columns:", len(df.columns))


# ==========================================
# 2. CONVERT DATES
# ==========================================

df["order_date"] = pd.to_datetime(df["order_date"])


# ==========================================
# 3. CREATE DATE FEATURES
# ==========================================

df["order_year"] = df["order_date"].dt.year

df["order_month"] = df["order_date"].dt.month

df["order_day"] = df["order_date"].dt.day

df["order_day_of_week"] = df["order_date"].dt.dayofweek


# ==========================================
# 4. CREATE WEEKEND FEATURE
# ==========================================

df["is_weekend"] = (
    df["order_day_of_week"] >= 5
).astype(int)


# ==========================================
# 5. SELECT ML FEATURES
# ==========================================

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
# 6. DISPLAY FEATURES
# ==========================================

print("\n========== FEATURES ==========")

print(X.head())

print("\nFeature columns:")
print(X.columns.tolist())


# ==========================================
# 7. TARGET VARIABLE
# ==========================================

print("\n========== TARGET ==========")

print(y.describe())


# ==========================================
# 8. CHECK MISSING VALUES
# ==========================================

print("\n========== MISSING VALUES ==========")

print(X.isnull().sum())


# ==========================================
# 9. SAVE FEATURE DATA
# ==========================================

os.makedirs("data/ml", exist_ok=True)

X.to_csv(
    "data/ml/eta_features.csv",
    index=False
)

y.to_csv(
    "data/ml/eta_target.csv",
    index=False
)


print("\n=========================================")
print("FEATURE ENGINEERING COMPLETED!")
print("Features: data/ml/eta_features.csv")
print("Target:   data/ml/eta_target.csv")
print("=========================================")