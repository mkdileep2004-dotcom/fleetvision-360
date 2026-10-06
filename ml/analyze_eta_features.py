import pandas as pd


# ==========================================
# 1. LOAD DATA
# ==========================================

df = pd.read_csv("data/ml/eta_training_data.csv")

print("\n========== DATA LOADED ==========")
print("Rows:", len(df))
print("Columns:", len(df.columns))


# ==========================================
# 2. CORRELATION WITH DELIVERY DAYS
# ==========================================

numeric_columns = [
    "distance_km",
    "route_distance_km",
    "estimated_time_minutes",
    "capacity_kg",
    "age",
    "experience_years",
    "delivery_days"
]

correlation = df[numeric_columns].corr()["delivery_days"]

correlation = correlation.sort_values(
    ascending=False
)

print("\n========== CORRELATION WITH DELIVERY DAYS ==========")
print(correlation)


# ==========================================
# 3. AVERAGE DELIVERY TIME BY DISTANCE
# ==========================================

df["distance_category"] = pd.cut(
    df["distance_km"],
    bins=[0, 100, 300, 500, 600],
    labels=[
        "0-100 km",
        "101-300 km",
        "301-500 km",
        "501-600 km"
    ]
)

print("\n========== DELIVERY DAYS BY DISTANCE ==========")

print(
    df.groupby(
        "distance_category",
        observed=True
    )["delivery_days"]
    .agg(["count", "mean", "min", "max"])
)


# ==========================================
# 4. AVERAGE DELIVERY TIME BY VEHICLE
# ==========================================

print("\n========== DELIVERY DAYS BY VEHICLE TYPE ==========")

print(
    df.groupby("vehicle_type")["delivery_days"]
    .agg(["count", "mean"])
    .sort_values("mean")
)


# ==========================================
# 5. AVERAGE DELIVERY TIME BY FUEL
# ==========================================

print("\n========== DELIVERY DAYS BY FUEL TYPE ==========")

print(
    df.groupby("fuel_type")["delivery_days"]
    .agg(["count", "mean"])
    .sort_values("mean")
)


# ==========================================
# 6. AVERAGE DELIVERY TIME BY WEEKEND
# ==========================================

df["order_date"] = pd.to_datetime(df["order_date"])

df["is_weekend"] = (
    df["order_date"].dt.dayofweek >= 5
).astype(int)

print("\n========== DELIVERY DAYS BY WEEKEND ==========")

print(
    df.groupby("is_weekend")["delivery_days"]
    .agg(["count", "mean"])
)


# ==========================================
# 7. SUMMARY
# ==========================================

print("\n=========================================")
print("ETA FEATURE ANALYSIS COMPLETED!")
print("=========================================")