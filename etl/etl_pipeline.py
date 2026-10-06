from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from getpass import getpass


# ==========================================================
# 1. PROJECT PATH
# ==========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DIR = PROJECT_ROOT / "data" / "raw"

PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ==========================================================
# 2. DATASET LIST
# ==========================================================

DATASETS = {
    "vehicles": "vehicles.csv",
    "drivers": "drivers.csv",
    "customers": "customers.csv",
    "routes": "routes.csv",
    "orders": "orders.csv",
    "gps_events": "gps_events.csv",
    "fuel_records": "fuel_records.csv",
    "maintenance": "maintenance.csv",
    "delivery_scans": "delivery_scans.csv"
}


# ==========================================================
# 3. GET POSTGRESQL PASSWORD
# ==========================================================

password = getpass(
    "Enter PostgreSQL password: "
)


# ==========================================================
# 4. CREATE DATABASE CONNECTION
# ==========================================================

database_url = URL.create(
    drivername="postgresql+psycopg2",
    username="postgres",
    password=password,
    host="localhost",
    port=5432,
    database="fleetvision"
)

engine = create_engine(
    database_url
)


# ==========================================================
# 5. TEST DATABASE CONNECTION
# ==========================================================

try:

    with engine.connect() as connection:

        connection.execute(
            text("SELECT 1")
        )

    print(
        "Database connection successful."
    )

except Exception as e:

    print(
        f"Database connection failed: {e}"
    )

    raise SystemExit


# ==========================================================
# 6. CREATE STAGING SCHEMA
# ==========================================================

with engine.begin() as connection:

    connection.execute(
        text(
            "CREATE SCHEMA IF NOT EXISTS staging"
        )
    )

print(
    "Staging schema ready."
)


# ==========================================================
# 7. ETL PROCESS
# ==========================================================

for table_name, file_name in DATASETS.items():

    print()
    print(
        "=========================================="
    )

    print(
        f"Processing: {file_name}"
    )

    print(
        "=========================================="
    )


    # ------------------------------------------------------
    # EXTRACT
    # ------------------------------------------------------

    file_path = RAW_DIR / file_name

    if not file_path.exists():

        print(
            f"ERROR: File not found: {file_path}"
        )

        continue

    print(
        "Extracting data..."
    )

    df = pd.read_csv(
        file_path
    )

    print(
        f"Rows extracted: {len(df):,}"
    )


    # ------------------------------------------------------
    # TRANSFORM
    # ------------------------------------------------------

    print(
        "Transforming data..."
    )


    # Remove duplicate rows

    df = df.drop_duplicates()


    # Clean column names

    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )


    # Clean text columns

    for column in df.select_dtypes(
        include="object"
    ).columns:

        df[column] = (
            df[column]
            .astype(str)
            .str.strip()
        )


    print(
        f"Rows after transformation: {len(df):,}"
    )
        # ------------------------------------------------------
    # DATA QUALITY VALIDATION
    # ------------------------------------------------------

    print(
        "Running data quality checks..."
    )


    # Check missing values

    missing_values = (
        df.isnull()
        .sum()
        .sum()
    )

    if missing_values == 0:

        print(
            "PASS: No missing values."
        )

    else:

        print(
            f"WARNING: {missing_values:,} missing values found."
        )


    # Check duplicate rows

    duplicate_rows = (
        df.duplicated()
        .sum()
    )

    if duplicate_rows == 0:

        print(
            "PASS: No duplicate rows."
        )

    else:

        print(
            f"WARNING: {duplicate_rows:,} duplicate rows found."
        )


    # ------------------------------------------------------
    # NUMERIC DATA CHECKS
    # ------------------------------------------------------

    negative_values = 0


    # Fuel litres

    if "litres" in df.columns:

        negative_values += (
            df["litres"]
            .lt(0)
            .sum()
        )


    # Fuel cost

    if "fuel_cost" in df.columns:

        negative_values += (
            df["fuel_cost"]
            .lt(0)
            .sum()
        )


    # Maintenance cost

    if "cost" in df.columns:

        negative_values += (
            df["cost"]
            .lt(0)
            .sum()
        )


    # Speed

    if "speed_kmph" in df.columns:

        negative_values += (
            df["speed_kmph"]
            .lt(0)
            .sum()
        )


    # Fuel level

    if "fuel_level_percent" in df.columns:

        invalid_fuel_level = (
            (df["fuel_level_percent"] < 0)
            |
            (df["fuel_level_percent"] > 100)
        ).sum()

        negative_values += invalid_fuel_level


    if negative_values == 0:

        print(
            "PASS: Numeric data checks passed."
        )

    else:

        print(
            f"WARNING: {negative_values:,} invalid numeric values found."
        )


    print(
        "Data quality validation completed."
    )


    # ------------------------------------------------------
    # SAVE PROCESSED DATA
    # ------------------------------------------------------

    processed_path = (
        PROCESSED_DIR / file_name
    )

    df.to_csv(
        processed_path,
        index=False
    )

    print(
        f"Processed file saved: {processed_path}"
    )


    # ------------------------------------------------------
    # LOAD
    # ------------------------------------------------------

    print(
        f"Loading into staging.{table_name}..."
    )

    df.to_sql(
        name=table_name,
        con=engine,
        schema="staging",
        if_exists="replace",
        index=False,
        chunksize=2000,
        method="multi"
    )

    print(
        f"Loaded successfully: staging.{table_name}"
    )


# ==========================================================
# 8. ETL COMPLETED
# ==========================================================

print()
print(
    "=========================================="
)
# ==========================================================
# 11. RELATIONSHIP VALIDATION
# ==========================================================

print()
print("==========================================")
print("RELATIONSHIP VALIDATION")
print("==========================================")


def check_relationship(
    child_df,
    child_column,
    parent_df,
    parent_column,
    relationship_name
):

    invalid_records = (
        ~child_df[child_column]
        .isin(parent_df[parent_column])
    ).sum()

    if invalid_records == 0:

        print(
            f"PASS: {relationship_name}"
        )

    else:

        print(
            f"FAIL: {relationship_name} "
            f"-> {invalid_records:,} invalid records"
        )


# ----------------------------------------------------------
# LOAD PROCESSED DATA FOR RELATIONSHIP CHECKS
# ----------------------------------------------------------

vehicles_df = pd.read_csv(
    PROCESSED_DIR / "vehicles.csv"
)

drivers_df = pd.read_csv(
    PROCESSED_DIR / "drivers.csv"
)

customers_df = pd.read_csv(
    PROCESSED_DIR / "customers.csv"
)

routes_df = pd.read_csv(
    PROCESSED_DIR / "routes.csv"
)

orders_df = pd.read_csv(
    PROCESSED_DIR / "orders.csv"
)

gps_df = pd.read_csv(
    PROCESSED_DIR / "gps_events.csv"
)

fuel_df = pd.read_csv(
    PROCESSED_DIR / "fuel_records.csv"
)

maintenance_df = pd.read_csv(
    PROCESSED_DIR / "maintenance.csv"
)

delivery_df = pd.read_csv(
    PROCESSED_DIR / "delivery_scans.csv"
)


# ----------------------------------------------------------
# ORDERS RELATIONSHIPS
# ----------------------------------------------------------

check_relationship(
    orders_df,
    "customer_id",
    customers_df,
    "customer_id",
    "orders.customer_id -> customers.customer_id"
)

check_relationship(
    orders_df,
    "vehicle_id",
    vehicles_df,
    "vehicle_id",
    "orders.vehicle_id -> vehicles.vehicle_id"
)

check_relationship(
    orders_df,
    "driver_id",
    drivers_df,
    "driver_id",
    "orders.driver_id -> drivers.driver_id"
)

check_relationship(
    orders_df,
    "route_id",
    routes_df,
    "route_id",
    "orders.route_id -> routes.route_id"
)


# ----------------------------------------------------------
# GPS RELATIONSHIP
# ----------------------------------------------------------

check_relationship(
    gps_df,
    "vehicle_id",
    vehicles_df,
    "vehicle_id",
    "gps_events.vehicle_id -> vehicles.vehicle_id"
)


# ----------------------------------------------------------
# FUEL RELATIONSHIP
# ----------------------------------------------------------

check_relationship(
    fuel_df,
    "vehicle_id",
    vehicles_df,
    "vehicle_id",
    "fuel_records.vehicle_id -> vehicles.vehicle_id"
)


# ----------------------------------------------------------
# MAINTENANCE RELATIONSHIP
# ----------------------------------------------------------

check_relationship(
    maintenance_df,
    "vehicle_id",
    vehicles_df,
    "vehicle_id",
    "maintenance.vehicle_id -> vehicles.vehicle_id"
)


# ----------------------------------------------------------
# DELIVERY SCAN RELATIONSHIP
# ----------------------------------------------------------

check_relationship(
    delivery_df,
    "order_id",
    orders_df,
    "order_id",
    "delivery_scans.order_id -> orders.order_id"
)


print()
print(
    "Relationship validation completed."
)

print(
    "ETL PIPELINE COMPLETED SUCCESSFULLY"
)

print(
    "=========================================="
)