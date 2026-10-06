import getpass
import pandas as pd
import matplotlib.pyplot as plt
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
# 2. LOAD ORDERS
# ==========================================

query = """
SELECT *
FROM public.orders;
"""

df = pd.read_sql(query, engine)


# ==========================================
# 3. BASIC ANALYSIS
# ==========================================

print("\n========== BASIC INFORMATION ==========")

print("Total Orders:", len(df))
print("Total Revenue:", round(df["order_amount"].sum(), 2))
print("Average Order Value:", round(df["order_amount"].mean(), 2))
print("Average Distance:", round(df["distance_km"].mean(), 2))


# ==========================================
# 4. ORDER STATUS ANALYSIS
# ==========================================

print("\n========== ORDER STATUS ==========")

status_counts = df["status"].value_counts()

print(status_counts)


# ==========================================
# 5. REVENUE BY STATUS
# ==========================================

print("\n========== REVENUE BY STATUS ==========")

revenue_by_status = (
    df.groupby("status")["order_amount"]
    .sum()
    .sort_values(ascending=False)
)

print(revenue_by_status)


# ==========================================
# 6. AVERAGE ORDER VALUE BY STATUS
# ==========================================

print("\n========== AVERAGE ORDER VALUE BY STATUS ==========")

avg_order_by_status = (
    df.groupby("status")["order_amount"]
    .mean()
    .sort_values(ascending=False)
)

print(avg_order_by_status)


# ==========================================
# 7. CREATE REPORT FOLDER
# ==========================================

import os

os.makedirs("ml/reports", exist_ok=True)


# ==========================================
# 8. CHART 1 - ORDER STATUS
# ==========================================

plt.figure(figsize=(8, 5))

status_counts.plot(kind="bar")

plt.title("Order Status Distribution")
plt.xlabel("Order Status")
plt.ylabel("Number of Orders")
plt.xticks(rotation=0)

plt.tight_layout()

plt.savefig("ml/reports/order_status.png")

plt.close()


# ==========================================
# 9. CHART 2 - ORDER AMOUNT
# ==========================================

plt.figure(figsize=(8, 5))

df["order_amount"].plot(kind="hist", bins=30)

plt.title("Order Amount Distribution")
plt.xlabel("Order Amount")
plt.ylabel("Number of Orders")

plt.tight_layout()

plt.savefig("ml/reports/order_amount_distribution.png")

plt.close()


# ==========================================
# 10. CHART 3 - DISTANCE
# ==========================================

plt.figure(figsize=(8, 5))

df["distance_km"].plot(kind="hist", bins=30)

plt.title("Delivery Distance Distribution")
plt.xlabel("Distance (km)")
plt.ylabel("Number of Orders")

plt.tight_layout()

plt.savefig("ml/reports/distance_distribution.png")

plt.close()


# ==========================================
# 11. CHART 4 - REVENUE BY STATUS
# ==========================================

plt.figure(figsize=(8, 5))

revenue_by_status.plot(kind="bar")

plt.title("Revenue by Order Status")
plt.xlabel("Order Status")
plt.ylabel("Revenue")
plt.xticks(rotation=0)

plt.tight_layout()

plt.savefig("ml/reports/revenue_by_status.png")

plt.close()


# ==========================================
# 12. CHART 5 - AVERAGE ORDER VALUE
# ==========================================

plt.figure(figsize=(8, 5))

avg_order_by_status.plot(kind="bar")

plt.title("Average Order Value by Status")
plt.xlabel("Order Status")
plt.ylabel("Average Order Value")
plt.xticks(rotation=0)

plt.tight_layout()

plt.savefig("ml/reports/average_order_by_status.png")

plt.close()


# ==========================================
# 13. DISTANCE CATEGORIES
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

distance_categories = df["distance_category"].value_counts().sort_index()

print("\n========== ORDERS BY DISTANCE ==========")

print(distance_categories)


# ==========================================
# 14. CHART 6 - DISTANCE CATEGORY
# ==========================================

plt.figure(figsize=(8, 5))

distance_categories.plot(kind="bar")

plt.title("Orders by Distance Range")
plt.xlabel("Distance Range")
plt.ylabel("Number of Orders")
plt.xticks(rotation=0)

plt.tight_layout()

plt.savefig("ml/reports/orders_by_distance.png")

plt.close()


# ==========================================
# 15. CLOSE DATABASE
# ==========================================

engine.dispose()

print("\n====================================")
print("EDA COMPLETED SUCCESSFULLY!")
print("Charts saved in: ml/reports/")
print("====================================")
