import csv
import random
from pathlib import Path
from datetime import date, timedelta

# ============================================================
# FleetVision 360 - Synthetic Dataset Generator
# ============================================================

random.seed(42)

# Project folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Output folder
RAW_DIR = BASE_DIR / "data" / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------
# Helper function
# ------------------------------------------------------------

def random_date(start_date, end_date):
    days = (end_date - start_date).days
    return start_date + timedelta(days=random.randint(0, days))


def write_csv(filename, columns, rows):
    file_path = RAW_DIR / filename

    with open(file_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(columns)
        writer.writerows(rows)

    print(f"Created: {filename} ({len(rows)} rows)")


START_DATE = date(2024, 1, 1)
END_DATE = date(2025, 12, 31)


# ============================================================
# 1. VEHICLES - 100
# ============================================================

vehicles = []

vehicle_types = ["Truck", "Van", "Mini Truck", "Tanker"]
manufacturers = ["Tata", "Ashok Leyland", "Mahindra", "Eicher"]
fuel_types = ["Diesel", "Petrol", "CNG"]

for i in range(1, 101):
    vehicles.append([
        f"V{i:04d}",
        f"KA01AB{i:04d}",
        random.choice(vehicle_types),
        random.choice(manufacturers),
        random.choice(fuel_types),
        random.randint(500, 10000),
        random.choice(["Active", "Active", "Active", "Inactive"])
    ])

write_csv(
    "vehicles.csv",
    [
        "vehicle_id",
        "registration_number",
        "vehicle_type",
        "manufacturer",
        "fuel_type",
        "capacity_kg",
        "status"
    ],
    vehicles
)


# ============================================================
# 2. DRIVERS - 150
# ============================================================

drivers = []

first_names = [
    "Rahul", "Kiran", "Arun", "Ravi", "Manoj",
    "Suresh", "Prakash", "Vijay", "Ramesh", "Ajay"
]

last_names = [
    "Kumar", "Sharma", "Patil", "Gowda", "Reddy",
    "Shetty", "Singh", "Naik", "Das", "Verma"
]

for i in range(1, 151):
    drivers.append([
        f"D{i:04d}",
        f"{random.choice(first_names)} {random.choice(last_names)}",
        random.randint(22, 58),
        random.choice(["Male", "Female"]),
        random.randint(1, 25),
        random.choice(["Active", "Active", "Inactive"])
    ])

write_csv(
    "drivers.csv",
    [
        "driver_id",
        "driver_name",
        "age",
        "gender",
        "experience_years",
        "status"
    ],
    drivers
)


# ============================================================
# 3. CUSTOMERS - 1,000
# ============================================================

customers = []

customer_names = [
    "Amit", "Priya", "Anil", "Sneha", "Deepa",
    "Rohan", "Pooja", "Naveen", "Swathi", "Vivek"
]

cities = [
    "Bengaluru",
    "Mysuru",
    "Mandya",
    "Ramanagara",
    "Tumakuru",
    "Hassan",
    "Mangaluru",
    "Hubballi",
    "Shivamogga",
    "Belagavi"
]

segments = ["Retail", "Corporate", "Wholesale", "Enterprise"]

for i in range(1, 1001):
    name = f"{random.choice(customer_names)} {random.choice(last_names)}"

    customers.append([
        f"C{i:05d}",
        name,
        f"customer{i}@example.com",
        random.choice(segments),
        random.choice(cities),
        random_date(date(2020, 1, 1), END_DATE)
    ])

write_csv(
    "customers.csv",
    [
        "customer_id",
        "customer_name",
        "email",
        "segment",
        "city",
        "signup_date"
    ],
    customers
)


# ============================================================
# 4. ROUTES - 100
# ============================================================

routes = []

route_cities = cities

for i in range(1, 101):
    origin = random.choice(route_cities)
    destination = random.choice(route_cities)

    while destination == origin:
        destination = random.choice(route_cities)

    distance = random.randint(20, 600)

    routes.append([
        f"R{i:04d}",
        f"Route {i}",
        origin,
        destination,
        distance,
        int(distance * 1.5)
    ])

write_csv(
    "routes.csv",
    [
        "route_id",
        "route_name",
        "origin",
        "destination",
        "distance_km",
        "estimated_time_minutes"
    ],
    routes
)


# ============================================================
# 5. ORDERS - 20,000
# ============================================================

orders = []

order_statuses = [
    "Delivered",
    "Delivered",
    "Delivered",
    "In Transit",
    "Cancelled",
    "Returned"
]

for i in range(1, 20001):

    order_date = random_date(START_DATE, END_DATE)

    delivery_date = order_date + timedelta(
        days=random.randint(1, 7)
    )

    orders.append([
        f"O{i:06d}",
        f"C{random.randint(1, 1000):05d}",
        f"R{random.randint(1, 100):04d}",
        f"V{random.randint(1, 100):04d}",
        f"D{random.randint(1, 150):04d}",
        order_date,
        delivery_date,
        random.choice(order_statuses),
        round(random.uniform(500, 50000), 2),
        random.randint(20, 600)
    ])

write_csv(
    "orders.csv",
    [
        "order_id",
        "customer_id",
        "route_id",
        "vehicle_id",
        "driver_id",
        "order_date",
        "delivery_date",
        "status",
        "order_amount",
        "distance_km"
    ],
    orders
)


# ============================================================
# 6. GPS EVENTS - 500,000
# ============================================================

gps_events = []

for i in range(1, 500001):

    vehicle_id = f"V{random.randint(1, 100):04d}"

    gps_date = random_date(START_DATE, END_DATE)

    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)

    timestamp = (
        f"{gps_date} "
        f"{hour:02d}:{minute:02d}:{second:02d}"
    )

    latitude = round(random.uniform(12.5, 15.5), 6)
    longitude = round(random.uniform(74.5, 78.5), 6)

    gps_events.append([
        f"G{i:07d}",
        vehicle_id,
        timestamp,
        latitude,
        longitude,
        random.randint(0, 100),
        round(random.uniform(5, 100), 2)
    ])

write_csv(
    "gps_events.csv",
    [
        "gps_event_id",
        "vehicle_id",
        "timestamp",
        "latitude",
        "longitude",
        "speed_kmph",
        "fuel_level_percent"
    ],
    gps_events
)


# ============================================================
# 7. FUEL RECORDS - 20,000
# ============================================================

fuel_records = []

for i in range(1, 20001):

    litres = round(random.uniform(20, 300), 2)
    fuel_price = random.uniform(85, 105)

    fuel_records.append([
        f"F{i:06d}",
        f"V{random.randint(1, 100):04d}",
        random_date(START_DATE, END_DATE),
        litres,
        random.randint(1000, 200000),
        round(litres * fuel_price, 2)
    ])

write_csv(
    "fuel_records.csv",
    [
        "fuel_record_id",
        "vehicle_id",
        "fuel_date",
        "litres",
        "odometer_km",
        "fuel_cost"
    ],
    fuel_records
)


# ============================================================
# 8. MAINTENANCE - 5,000
# ============================================================

maintenance = []

maintenance_types = [
    "Oil Change",
    "Brake Service",
    "Tyre Replacement",
    "Engine Service",
    "Battery Replacement",
    "General Service"
]

for i in range(1, 5001):

    maintenance.append([
        f"M{i:06d}",
        f"V{random.randint(1, 100):04d}",
        random_date(START_DATE, END_DATE),
        random.choice(maintenance_types),
        round(random.uniform(500, 50000), 2),
        random.choice(["Completed", "Completed", "Pending"])
    ])

write_csv(
    "maintenance.csv",
    [
        "maintenance_id",
        "vehicle_id",
        "maintenance_date",
        "maintenance_type",
        "cost",
        "status"
    ],
    maintenance
)


# ============================================================
# 9. DELIVERY SCANS - 20,000
# ============================================================

delivery_scans = []

scan_types = [
    "Pickup",
    "In Transit",
    "Out for Delivery",
    "Delivered"
]

for i in range(1, 20001):

    scan_date = random_date(START_DATE, END_DATE)

    delivery_scans.append([
        f"S{i:06d}",
        f"O{random.randint(1, 20000):06d}",
        random.choice(scan_types),
        f"{scan_date} "
        f"{random.randint(0, 23):02d}:"
        f"{random.randint(0, 59):02d}:"
        f"{random.randint(0, 59):02d}"
    ])

write_csv(
    "delivery_scans.csv",
    [
        "scan_id",
        "order_id",
        "scan_type",
        "scan_timestamp"
    ],
    delivery_scans
)


# ============================================================
# FINISHED
# ============================================================

print()
print("==============================================")
print("ALL DATASETS CREATED SUCCESSFULLY!")
print("==============================================")
print(f"Files are located in: {RAW_DIR}")
