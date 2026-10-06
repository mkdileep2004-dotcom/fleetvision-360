import pandas as pd
import numpy as np
import os


# ==========================================
# 1. LOAD FEATURE DATA
# ==========================================

input_file = "data/ml/eta_training_data.csv"

df = pd.read_csv(input_file)

print("\n========== DATA LOADED ==========")
print("Rows:", len(df))


# ==========================================
# 2. CONVERT DATE
# ==========================================

df["order_date"] = pd.to_datetime(df["order_date"])


# ==========================================
# 3. CREATE WEEKEND FEATURE
# ==========================================

df["is_weekend"] = (
    df["order_date"].dt.dayofweek >= 5
).astype(int)


# ==========================================
# 4. CREATE REALISTIC DELIVERY TIME
# ==========================================

np.random.seed(42)

# Base delivery time from route travel estimate
base_days = df["estimated_time_minutes"] / 480

# Distance effect
distance_effect = df["distance_km"] / 1000

# Driver experience effect
experience_effect = np.maximum(
    0,
    3 - df["experience_years"] * 0.05
)

# Weekend effect
weekend_effect = df["is_weekend"] * 0.25

# Random variation
random_effect = np.random.normal(
    loc=0,
    scale=0.5,
    size=len(df)
)

delivery_days = (
    base_days
    + distance_effect
    + experience_effect
    + weekend_effect
    + random_effect
)


# ==========================================
# 5. KEEP TARGET WITHIN REALISTIC RANGE
# ==========================================

df["delivery_days"] = np.clip(
    delivery_days,
    1,
    7
)

# Round to 2 decimal places
df["delivery_days"] = df["delivery_days"].round(2)


# ==========================================
# 6. DISPLAY TARGET
# ==========================================

print("\n========== NEW DELIVERY DAYS ==========")

print(
    df["delivery_days"].describe()
)


# ==========================================
# 7. CHECK CORRELATION
# ==========================================

print("\n========== CORRELATION ==========")

correlation_columns = [
    "distance_km",
    "route_distance_km",
    "estimated_time_minutes",
    "capacity_kg",
    "age",
    "experience_years",
    "delivery_days"
]

print(
    df[correlation_columns]
    .corr()["delivery_days"]
    .sort_values(ascending=False)
)


# ==========================================
# 8. SAVE IMPROVED DATASET
# ==========================================

os.makedirs("data/ml", exist_ok=True)

output_file = "data/ml/eta_training_data_realistic.csv"

df.to_csv(
    output_file,
    index=False
)

print("\n=========================================")
print("REALISTIC ETA DATASET CREATED!")
print("File:", output_file)
print("Rows:", len(df))
print("=========================================")