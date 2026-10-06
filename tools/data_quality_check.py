import csv
from pathlib import Path
from collections import Counter
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"


def read_csv(filename):
    file_path = RAW_DIR / filename

    with open(file_path, "r", encoding="utf-8", newline="") as file:
        return list(csv.DictReader(file))


def check_duplicate_ids(filename, id_column):
    rows = read_csv(filename)

    ids = [row[id_column] for row in rows]

    duplicates = [
        item
        for item, count in Counter(ids).items()
        if count > 1
    ]

    if len(duplicates) == 0:
        print(f"PASS: No duplicate {id_column} in {filename}")
    else:
        print(f"FAIL: Duplicate {id_column} found in {filename}")
        print(f"Duplicate count: {len(duplicates)}")


def check_missing_values(filename):
    rows = read_csv(filename)

    missing_count = 0

    for row in rows:
        for column, value in row.items():
            if value is None or value.strip() == "":
                missing_count += 1

    if missing_count == 0:
        print(f"PASS: No missing values in {filename}")
    else:
        print(f"FAIL: Missing values found in {filename}")
        print(f"Missing value count: {missing_count}")


def check_negative_values(filename, column):
    rows = read_csv(filename)

    negative_count = 0

    for row in rows:
        try:
            value = float(row[column])

            if value < 0:
                negative_count += 1

        except (ValueError, TypeError):
            pass

    if negative_count == 0:
        print(f"PASS: No negative values in {filename}.{column}")
    else:
        print(f"FAIL: Negative values found in {filename}.{column}")
        print(f"Negative count: {negative_count}")


def check_valid_range(filename, column, minimum, maximum):
    rows = read_csv(filename)

    invalid_count = 0

    for row in rows:
        try:
            value = float(row[column])

            if value < minimum or value > maximum:
                invalid_count += 1

        except (ValueError, TypeError):
            pass

    if invalid_count == 0:
        print(
            f"PASS: {filename}.{column} values are within "
            f"{minimum} to {maximum}"
        )
    else:
        print(f"FAIL: Invalid values in {filename}.{column}")
        print(f"Invalid count: {invalid_count}")


def check_date_format(filename, column):
    rows = read_csv(filename)

    invalid_count = 0

    for row in rows:
        date_value = row[column]

        try:
            datetime.fromisoformat(date_value)
        except (ValueError, TypeError):
            invalid_count += 1

    if invalid_count == 0:
        print(f"PASS: Valid dates in {filename}.{column}")
    else:
        print(f"FAIL: Invalid dates in {filename}.{column}")
        print(f"Invalid date count: {invalid_count}")


print("==============================================")
print("FleetVision 360 - Data Quality Validation")
print("==============================================")
print()


print("1. DUPLICATE ID CHECK")
print("----------------------------------------------")

check_duplicate_ids("vehicles.csv", "vehicle_id")
check_duplicate_ids("drivers.csv", "driver_id")
check_duplicate_ids("customers.csv", "customer_id")
check_duplicate_ids("routes.csv", "route_id")
check_duplicate_ids("orders.csv", "order_id")
check_duplicate_ids("gps_events.csv", "gps_event_id")
check_duplicate_ids("fuel_records.csv", "fuel_record_id")
check_duplicate_ids("maintenance.csv", "maintenance_id")
check_duplicate_ids("delivery_scans.csv", "scan_id")

print()


print("2. MISSING VALUE CHECK")
print("----------------------------------------------")

check_missing_values("vehicles.csv")
check_missing_values("drivers.csv")
check_missing_values("customers.csv")
check_missing_values("routes.csv")
check_missing_values("orders.csv")
check_missing_values("gps_events.csv")
check_missing_values("fuel_records.csv")
check_missing_values("maintenance.csv")
check_missing_values("delivery_scans.csv")

print()


print("3. NEGATIVE VALUE CHECK")
print("----------------------------------------------")

check_negative_values("orders.csv", "order_amount")
check_negative_values("fuel_records.csv", "litres")
check_negative_values("maintenance.csv", "cost")

print()


print("4. GPS RANGE CHECK")
print("----------------------------------------------")

check_valid_range(
    "gps_events.csv",
    "latitude",
    -90,
    90
)

check_valid_range(
    "gps_events.csv",
    "longitude",
    -180,
    180
)

print()


print("5. DATE FORMAT CHECK")
print("----------------------------------------------")

check_date_format(
    "orders.csv",
    "order_date"
)

check_date_format(
    "gps_events.csv",
    "timestamp"
)

print()


print("==============================================")
print("DATA QUALITY VALIDATION COMPLETED!")
print("==============================================")