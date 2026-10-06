import getpass
import os
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


# ==========================================
# 1. DATABASE CONNECTION
# ==========================================

password = getpass.getpass("Enter PostgreSQL password: ")

connection_url = URL.create(
    drivername="postgresql+psycopg2",
    username="postgres",
    password=password,
    host="localhost",
    port=5432,
    database="fleetvision"
)

engine = create_engine(connection_url)


# ==========================================
# 2. LOAD REQUIRED TABLES
# ==========================================

orders_query = """
SELECT
    order_id,
    route_id,
    vehicle_id,
    driver_id,
    order_date,
    delivery_date,
    status,
    distance_km
FROM public.orders
WHERE status = 'Delivered'
  AND delivery_date IS NOT NULL;
"""

routes_query = """
SELECT
    route_id,
    distance_km AS route_distance_km,
    estimated_time_minutes
FROM public.routes;
"""

vehicles_query = """
SELECT
    vehicle_id,
    vehicle_type,
    manufacturer,
    fuel_type,
    capacity_kg
FROM public.vehicles;
"""

drivers_query = """
SELECT
    driver_id,
    age,
    experience_years
FROM public.drivers;
"""


orders = pd.read_sql(orders_query, engine)
routes = pd.read_sql(routes_query, engine)
vehicles = pd.read_sql(vehicles_query, engine)
drivers = pd.read_sql(drivers_query, engine)


print("\n========== DATA LOADED ==========")
print("Delivered orders:", len(orders))
print("Routes:", len(routes))
print("Vehicles:", len(vehicles))
print("Drivers:", len(drivers))


# ==========================================
# 3. CONVERT DATES
# ==========================================

orders["order_date"] = pd.to_datetime(orders["order_date"])
orders["delivery_date"] = pd.to_datetime(orders["delivery_date"])


# ==========================================
# 4. CALCULATE ACTUAL DELIVERY TIME
# ==========================================

orders["delivery_days"] = (
    orders["delivery_date"] - orders["order_date"]
).dt.total_seconds() / (24 * 60 * 60)


# ==========================================
# 5. JOIN ROUTES
# ==========================================

df = orders.merge(
    routes,
    on="route_id",
    how="left"
)


# ==========================================
# 6. JOIN VEHICLES
# ==========================================

df = df.merge(
    vehicles,
    on="vehicle_id",
    how="left"
)


# ==========================================
# 7. JOIN DRIVERS
# ==========================================

df = df.merge(
    drivers,
    on="driver_id",
    how="left"
)


# ==========================================
# 8. DISPLAY DATASET
# ==========================================

print("\n========== FINAL ML DATASET ==========")

print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nColumns:")
print(df.columns.tolist())


# ==========================================
# 9. CHECK MISSING VALUES
# ==========================================

print("\n========== MISSING VALUES ==========")

print(df.isnull().sum())


# ==========================================
# 10. CHECK TARGET VARIABLE
# ==========================================

print("\n========== DELIVERY DAYS ==========")

print(df["delivery_days"].describe())


# ==========================================
# 11. REMOVE INVALID TARGET VALUES
# ==========================================

df = df[df["delivery_days"] >= 0]

print("\nRows after target validation:", len(df))


# ==========================================
# 12. SAVE ML DATASET
# ==========================================

os.makedirs("data/ml", exist_ok=True)

output_file = "data/ml/eta_training_data.csv"

df.to_csv(
    output_file,
    index=False
)

print("\n=========================================")
print("ETA DATASET CREATED SUCCESSFULLY!")
print("File:", output_file)
print("Rows:", len(df))
print("=========================================")


# ==========================================
# 13. CLOSE DATABASE
# ==========================================

engine.dispose()