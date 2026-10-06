import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"

print("==============================================")
print("FleetVision 360 - Dataset Profiling")
print("==============================================")
print()

csv_files = sorted(RAW_DIR.glob("*.csv"))

for file_path in csv_files:
    with open(file_path, "r", encoding="utf-8", newline="") as file:
        reader = csv.reader(file)
        header = next(reader)

        rows = 0
        missing = [0] * len(header)

        for row in reader:
            rows += 1
            for i, value in enumerate(row):
                if not value.strip():
                    missing[i] += 1

    print("----------------------------------------------")
    print(f"File: {file_path.name}")
    print(f"Rows: {rows}")
    print(f"Columns: {len(header)}")

    for i, column in enumerate(header):
        print(f"  {column}: missing={missing[i]}")

print()
print("==============================================")
print("PROFILING COMPLETED SUCCESSFULLY!")
print("==============================================")
