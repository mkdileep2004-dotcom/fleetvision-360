import csv
from pathlib import Path
from datetime import datetime


# ------------------------------------------------
# PROJECT DIRECTORIES
# ------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

BRONZE_DIR = BASE_DIR / "data" / "bronze"
SILVER_DIR = BASE_DIR / "data" / "silver"

# Create Silver folder
SILVER_DIR.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------
# DATASET FILES
# ------------------------------------------------

DATASETS = [
    "vehicles.csv",
    "drivers.csv",
    "customers.csv",
    "routes.csv",
    "orders.csv",
    "gps_events.csv",
    "fuel_records.csv",
    "maintenance.csv",
    "delivery_scans.csv"
]


# ------------------------------------------------
# CLEAN TEXT
# ------------------------------------------------

def clean_text(value):
    if value is None:
        return ""

    return value.strip()


# ------------------------------------------------
# TRANSFORM ONE CSV FILE
# ------------------------------------------------

def transform_file(filename):

    source_file = BRONZE_DIR / filename
    destination_file = SILVER_DIR / filename

    rows = []

    with open(
        source_file,
        "r",
        encoding="utf-8",
        newline=""
    ) as source:

        reader = csv.DictReader(source)

        fieldnames = reader.fieldnames

        for row in reader:

            # Clean text values
            cleaned_row = {}

            for column, value in row.items():
                cleaned_row[column] = clean_text(value)

            # Skip completely empty rows
            if all(value == "" for value in cleaned_row.values()):
                continue

            rows.append(cleaned_row)


    # ------------------------------------------------
    # REMOVE DUPLICATE ROWS
    # ------------------------------------------------

    unique_rows = []
    seen = set()

    for row in rows:

        row_key = tuple(row.values())

        if row_key not in seen:
            seen.add(row_key)
            unique_rows.append(row)


    # ------------------------------------------------
    # WRITE SILVER FILE
    # ------------------------------------------------

    silver_fieldnames = fieldnames + [
        "_transformed_at"
    ]

    with open(
        destination_file,
        "w",
        encoding="utf-8",
        newline=""
    ) as destination:

        writer = csv.DictWriter(
            destination,
            fieldnames=silver_fieldnames
        )

        writer.writeheader()

        for row in unique_rows:

            row["_transformed_at"] = (
                datetime.now().isoformat(timespec="seconds")
            )

            writer.writerow(row)


    removed_rows = len(rows) - len(unique_rows)

    print(
        f"SILVER CREATED: {filename} "
        f"({len(unique_rows)} rows, "
        f"{removed_rows} duplicates removed)"
    )


# ------------------------------------------------
# MAIN PROGRAM
# ------------------------------------------------

print("==============================================")
print("FleetVision 360 - Silver Transformation")
print("==============================================")
print()


for dataset in DATASETS:

    transform_file(dataset)


print()
print("==============================================")
print("SILVER TRANSFORMATION COMPLETED!")
print("==============================================")
print()
print("Silver files are stored in:")
print(SILVER_DIR)