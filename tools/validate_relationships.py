import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"


def get_column_values(filename, column):
    file_path = RAW_DIR / filename

    values = set()

    with open(file_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            values.add(row[column])

    return values


def check_relationship(child_file, child_column, parent_file, parent_column):
    child_values = get_column_values(child_file, child_column)
    parent_values = get_column_values(parent_file, parent_column)

    invalid_values = child_values - parent_values

    relationship = f"{child_file}.{child_column} -> {parent_file}.{parent_column}"

    if len(invalid_values) == 0:
        print(f"PASS: {relationship}")
    else:
        print(f"FAIL: {relationship}")
        print(f"Invalid IDs: {len(invalid_values)}")


print("==============================================")
print("FleetVision 360 - Relationship Validation")
print("==============================================")
print()

check_relationship(
    "orders.csv",
    "customer_id",
    "customers.csv",
    "customer_id"
)

check_relationship(
    "orders.csv",
    "route_id",
    "routes.csv",
    "route_id"
)

check_relationship(
    "orders.csv",
    "vehicle_id",
    "vehicles.csv",
    "vehicle_id"
)

check_relationship(
    "orders.csv",
    "driver_id",
    "drivers.csv",
    "driver_id"
)

check_relationship(
    "gps_events.csv",
    "vehicle_id",
    "vehicles.csv",
    "vehicle_id"
)

check_relationship(
    "fuel_records.csv",
    "vehicle_id",
    "vehicles.csv",
    "vehicle_id"
)

check_relationship(
    "maintenance.csv",
    "vehicle_id",
    "vehicles.csv",
    "vehicle_id"
)

check_relationship(
    "delivery_scans.csv",
    "order_id",
    "orders.csv",
    "order_id"
)

print()
print("==============================================")
print("RELATIONSHIP VALIDATION COMPLETED!")
print("==============================================")