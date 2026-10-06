import getpass
import psycopg2

password = getpass.getpass("Enter PostgreSQL password: ")

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="fleetvision",
    user="postgres",
    password=password
)

cursor = conn.cursor()

cursor.execute("SELECT current_database();")

result = cursor.fetchone()

print("Connected successfully!")
print("Database:", result[0])

cursor.close()
conn.close()