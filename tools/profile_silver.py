import csv
from pathlib import Path

SILVER_DIR = Path("data/silver")

print("=" * 60)
print("FleetVision 360 - Silver Data Profiling")
print("=" * 60)

total_rows = 0

for file in sorted(SILVER_DIR.glob("*.csv")):

    with open(file, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    row_count = len(rows)
    column_count = len(reader.fieldnames)

    # Missing values
    missing_count = 0

    for row in rows:
        for value in row.values():
            if value is None or str(value).strip() == "":
                missing_count += 1

    # Duplicate rows
    duplicate_count = row_count - len(
        {tuple(row.values()) for row in rows}
    )

    # Metadata columns
    has_transformed_at = "_transformed_at" in reader.fieldnames

    print()
    print(f"File: {file.name}")
    print(f"Rows: {row_count}")
    print(f"Columns: {column_count}")
    print(f"Missing values: {missing_count}")
    print(f"Duplicate rows: {duplicate_count}")
    print(f"_transformed_at column: {has_transformed_at}")

    total_rows += row_count

print()
print("=" * 60)
print(f"TOTAL SILVER ROWS: {total_rows:,}")
print("=" * 60)

print()
print("SILVER PROFILING COMPLETED SUCCESSFULLY!")