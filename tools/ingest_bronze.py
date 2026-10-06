import csv
from pathlib import Path
from datetime import datetime


# ------------------------------------------------
# PROJECT DIRECTORIES
# ------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

RAW_DIR = BASE_DIR / "data" / "raw"
BRONZE_DIR = BASE_DIR / "data" / "bronze"


# Create Bronze folder if it does not exist
BRONZE_DIR.mkdir(parents=True, exist_ok=True)


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
# INGEST ONE CSV FILE
# ------------------------------------------------

def ingest_file(filename):

    source_file = RAW_DIR / filename
    destination_file = BRONZE_DIR / filename

    row_count = 0

    with open(
        source_file,
        "r",
        encoding="utf-8",
        newline=""
    ) as source:

        reader = csv.DictReader(source)

        fieldnames = reader.fieldnames + [
            "_ingested_at",
            "_source_file"
        ]

        with open(
            destination_file,
            "w",
            encoding="utf-8",
            newline=""
        ) as destination:

            writer = csv.DictWriter(
                destination,
                fieldnames=fieldnames
            )

            writer.writeheader()

            for row in reader:

                row["_ingested_at"] = (
                    datetime.now().isoformat(timespec="seconds")
                )

                row["_source_file"] = filename

                writer.writerow(row)

                row_count += 1

    print(
        f"BRONZE CREATED: {filename} "
        f"({row_count} rows)"
    )


# ------------------------------------------------
# MAIN PROGRAM
# ------------------------------------------------

print("==============================================")
print("FleetVision 360 - Bronze Data Ingestion")
print("==============================================")
print()

for dataset in DATASETS:

    ingest_file(dataset)

print()
print("==============================================")
print("BRONZE INGESTION COMPLETED!")
print("==============================================")
print()
print(f"Bronze files are stored in:")
print(BRONZE_DIR)