import getpass
import psycopg2


def get_connection():
    password = getpass.getpass("Enter PostgreSQL password: ")

    return psycopg2.connect(
        host="localhost",
        port=5432,
        database="fleetvision",
        user="postgres",
        password=password
    )


if __name__ == "__main__":
    conn = get_connection()

    cursor = conn.cursor()
    cursor.execute("SELECT current_database();")

    result = cursor.fetchone()

    print("Database connection successful!")
    print("Database:", result[0])

    cursor.close()
    conn.close()