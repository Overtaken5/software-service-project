import pytest
import psycopg2

# Тестовые параметры для подключения
conn_params = {
    "host": "localhost",
    "database": "service_db",
    "user": "postgres",
    "password": "123456"
}

@pytest.fixture(scope="module")
def db_connection():
    conn = psycopg2.connect(**conn_params)
    yield conn
    conn.rollback()  # Откат изменений после теста
    conn.close()

def test_insert_order_with_foreign_keys(db_connection):
    cur = db_connection.cursor()

    # Вставляем пользователя
    cur.execute("""
        INSERT INTO public."Users" (username, hashed_password, token)
        VALUES ('testuser', 'password123', 'token123') RETURNING id
    """)
    user_id = cur.fetchone()[0]

    # Вставляем точку самовывоза
    cur.execute("""
        INSERT INTO public."PickUpPoint" (location)
        VALUES ('Test Location') RETURNING id
    """)
    pickup_point_id = cur.fetchone()[0]

    # Вставляем заказ с привязкой к существующему пользователю и точке самовывоза
    cur.execute("""
        INSERT INTO public."Orders" (user_id, "date", pickup_point_id)
        VALUES (%s, CURRENT_DATE, %s) RETURNING id
    """, (user_id, pickup_point_id))

    order_id = cur.fetchone()[0]

    # Проверка успешного добавления заказа
    assert order_id is not None

    # Проверка наличия заказа в БД
    cur.execute("SELECT * FROM public.\"Orders\" WHERE id = %s", (order_id,))
    order = cur.fetchone()
    assert order is not None

def test_insert_orderproduct_with_foreign_keys(db_connection):
    cur = db_connection.cursor()

    # Вставляем продукт
    cur.execute("""
        INSERT INTO public."Product" ("name", quantity, price)
        VALUES ('Test Product', 10, 100) RETURNING id
    """)
    product_id = cur.fetchone()[0]

    # Вставляем пользователя
    cur.execute("""
        INSERT INTO public."Users" (username, hashed_password, token)
        VALUES ('testuser2', 'password123', 'token123') RETURNING id
    """)
    user_id = cur.fetchone()[0]

    # Вставляем точку самовывоза
    cur.execute("""
        INSERT INTO public."PickUpPoint" (location)
        VALUES ('Test Location 2') RETURNING id
    """)
    pickup_point_id = cur.fetchone()[0]

    # Вставляем заказ
    cur.execute("""
        INSERT INTO public."Orders" (user_id, "date", pickup_point_id)
        VALUES (%s, CURRENT_DATE, %s) RETURNING id
    """, (user_id, pickup_point_id))
    order_id = cur.fetchone()[0]

    # Вставляем товар в заказ
    cur.execute("""
        INSERT INTO public."OrderProduct" (id, product_id, quantity, price)
        VALUES (%s, %s, 2, 200) RETURNING id
    """, (order_id, product_id))

    order_product_id = cur.fetchone()[0]

    # Проверка успешного добавления записи в OrderProduct
    assert order_product_id is not None

    # Проверка наличия записи в БД
    cur.execute("SELECT * FROM public.\"OrderProduct\" WHERE id = %s", (order_product_id,))
    order_product = cur.fetchone()
    assert order_product is not None
