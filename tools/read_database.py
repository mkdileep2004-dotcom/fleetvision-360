import getpass
import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.engine import URL


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

query = """
SELECT *
FROM public.orders
LIMIT 10;
"""

df = pd.read_sql(query, engine)

print("\nOrders data:")
print(df)

print("\nNumber of rows:", len(df))
print("Number of columns:", len(df.columns))

engine.dispose()