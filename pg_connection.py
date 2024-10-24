import psycopg2

conn_params = {
    "host": "localhost",
    "database": "postgres",
    "user": "postgres",
    "password": "123456"
}

try:
    conn = psycopg2.connect(**conn_params)
    print("Connection successful!")
except Exception as e:
    print(f"Connection error: {e}")