# Это тестовый файл, миграцию БД допишем в отдельном
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

    cur = conn.cursor()
    cur.execute("SELECT * FROM your_table")
    rows = cur.fetchall()

    for row in rows:
        print(row)

except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)

finally:
    if conn:
        conn.close()
        print("Connection closed.")
