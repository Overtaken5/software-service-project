import os
import pandas as pd
import psycopg2
from psycopg2 import sql


# Функция для подключения к базе данных PostgreSQL
def get_db_connection(db_url):
    try:
        conn = psycopg2.connect(db_url)
        return conn
    except Exception as e:
        print(f"Ошибка подключения к базе данных: {e}")
        return None


# Функция для проверки существования ProductId в таблице Products
def check_product_exists_in_products(conn, product_id):
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1 FROM public.\"Products\" WHERE \"Id\" = %s", (product_id,))
            return cursor.fetchone() is not None
    except Exception as e:
        print(f"Ошибка при проверке существования ProductId в таблице Products: {e}")
        return False


# Функция для добавления продукта в таблицу Products
def insert_product_in_products(conn, product_id):
    try:
        with conn.cursor() as cursor:
            # Не указываем столбец Id, он будет сгенерирован автоматически
            insert_query = """
                INSERT INTO public."Products" ("Name", "CurrentStock", "Price")
                VALUES (%s, %s, %s)
            """
            product_name = f"Product {product_id}"  # Генерация имени продукта
            current_stock = 0  # Начальное количество
            price = 100  # Начальная цена (например, 100)
            cursor.execute(insert_query, (product_name, current_stock, price))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при добавлении продукта в таблицу Products: {e}")


# Функция для вставки данных в таблицу Product
def insert_data(conn, product_id, data):
    try:
        with conn.cursor() as cursor:
            insert_query = """
                INSERT INTO public."Product" ("ProductId", "Date", "Quantity")
                VALUES (%s, %s, %s)
            """
            for index, row in data.iterrows():
                cursor.execute(insert_query, (product_id, row['date'], row['quantity']))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Ошибка при вставке данных в таблицу Product: {e}")


# Основной скрипт
def load_csv_to_db(db_url):
    # Подключаемся к базе данных
    conn = get_db_connection(db_url)
    if conn is None:
        return

    # Обрабатываем файлы от 1.csv до 7.csv
    for i in range(1, 8):
        csv_file = f"{i}.csv"

        # Проверяем, существует ли файл
        if not os.path.isfile(csv_file):
            print(os.path.curdir)
            print(f"Файл {csv_file} не найден.")
            continue

        # Загружаем CSV файл
        try:
            data = pd.read_csv(csv_file, header=0, dtype={'date': str, 'quantity': int})
            data['date'] = pd.to_datetime(data['date'], errors='coerce')  # Преобразование даты
            data = data.dropna(subset=['date'])  # Удаление строк с некорректной датой

            product_id = int(i)  # Определяем ProductId как имя файла

            # Проверяем, существует ли продукт с таким ProductId в таблице Products
            if not check_product_exists_in_products(conn, product_id):
                print(f"Продукт с ProductId={product_id} не найден в таблице Products.")
                print(f"Добавляем продукт с ProductId={product_id} в таблицу Products.")
                insert_product_in_products(conn, product_id)

            print(f"Загружаем данные из {csv_file} с ProductId={product_id}")

            # Вставляем данные в таблицу Product
            insert_data(conn, product_id, data)
        except Exception as e:
            print(f"Ошибка при обработке файла {csv_file}: {e}")

    # Закрываем соединение
    conn.close()
    print("Загрузка завершена.")


# Пример использования:
if __name__ == "__main__":
    # URL для подключения к базе данных PostgreSQL
    db_url = "postgresql://postgres:sanji@127.0.0.1/service_db"

    # Запускаем загрузку данных
    load_csv_to_db(db_url)
