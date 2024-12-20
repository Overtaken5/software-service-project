import pytest
import psycopg2

# Тестовые параметры для подключения
conn_params = {
    "host": "127.0.0.1",
    "database": "service_db",
    "user": "postgres",
    "password": "sanji"
}

@pytest.fixture(scope="module")
def db_connection():
    conn = psycopg2.connect(**conn_params)
    yield conn
    conn.rollback()  # Откат изменений после теста
    conn.close()

def test_insert_order_with_foreign_keys(db_connection):
    cur = db_connection.cursor()

    # Вставляем продукт в таблицу Products (актуальные данные о товаре)
    cur.execute("""
        INSERT INTO public."Products" ("Name", "CurrentStock", "Price")
        VALUES ('Test Product', 100, 50) RETURNING "Id"
    """)
    product_id = cur.fetchone()[0]

    # Вставляем запись о количестве товара в таблицу Product (исторические данные)
    cur.execute("""
        INSERT INTO public."Product" ("ProductId", "Date", "Quantity")
        VALUES (%s, CURRENT_DATE, 100) RETURNING "Id"
    """, (product_id,))
    product_history_id = cur.fetchone()[0]

    # Вставляем заказ
    cur.execute("""
        INSERT INTO public."Orders" ("CreationDate")
        VALUES (CURRENT_DATE) RETURNING "Id"
    """)
    order_id = cur.fetchone()[0]

    # Проверка успешного добавления заказа
    assert order_id is not None

    # Проверка наличия заказа в БД
    cur.execute('SELECT * FROM public."Orders" WHERE "Id" = %s', (order_id,))
    order = cur.fetchone()
    assert order is not None

def test_insert_orderdetails_with_foreign_keys(db_connection):
    cur = db_connection.cursor()

    # Вставляем продукт в таблицу Products (актуальные данные о товаре)
    cur.execute("""
        INSERT INTO public."Products" ("Name", "CurrentStock", "Price")
        VALUES ('Test Product', 100, 50) RETURNING "Id"
    """)
    product_id = cur.fetchone()[0]

    # Вставляем запись о количестве товара в таблицу Product (исторические данные)
    cur.execute("""
        INSERT INTO public."Product" ("ProductId", "Date", "Quantity")
        VALUES (%s, CURRENT_DATE, 100) RETURNING "Id"
    """, (product_id,))
    product_history_id = cur.fetchone()[0]

    # Вставляем заказ
    cur.execute("""
        INSERT INTO public."Orders" ("CreationDate")
        VALUES (CURRENT_DATE) RETURNING "Id"
    """)
    order_id = cur.fetchone()[0]

    # Вставляем детали заказа (связь заказа с продуктом)
    cur.execute("""
        INSERT INTO public."OrderDetails" ("OrderId", "ProductId", "Quantity")
        VALUES (%s, %s, 2) RETURNING "Id"
    """, (order_id, product_id))

    order_details_id = cur.fetchone()[0]

    # Проверка успешного добавления записи в OrderDetails
    assert order_details_id is not None

    # Проверка наличия записи в БД
    cur.execute('SELECT * FROM public."OrderDetails" WHERE "Id" = %s', (order_details_id,))
    order_details = cur.fetchone()
    assert order_details is not None
