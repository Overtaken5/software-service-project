from fastapi import Form, Request, APIRouter
from fastapi.params import Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import func

from app.api.models.models import Products, Product
from app.api.db_connection import get_db

router = APIRouter()


# # прогноз продуктов
# @router.post("/products_forecast")
# async def check_products_amount():
#     pass
#
#
# async def give_forecast():
#     pass


# параметры продукта по названию
@router.get("/one_product_amount")
async def get_product_by_name(product_name: str, db: Session = Depends(get_db)):
    product = db.query(Products).filter(
        (product_name == Products.Name) | (func.upper(Products.Name) == product_name.upper())
    ).first()
    if product is None:
        return {"error": f"Product '{product_name}' was not found in the database."}
    return {"message": f"Product '{product_name}' exists in the database."}


@router.post("/one_product_amount")
async def get_product_details(product_name: str = Form(...), db: Session = Depends(get_db)):
    product = db.query(Products).filter(
        (product_name == Products.Name) | (func.upper(Products.Name) == product_name.upper())
    ).first()
    if product is None:
        return {"error": f"Product '{product_name}' was not found in the database."}
    return {
        "name": product.Name,
        "quantity": product.CurrentStock,
        "price": product.Price
    }



# json всех продуктов в БД
@router.get("/all_products")
async def get_all_products(db: Session = Depends(get_db)):
    products = db.query(Products).all()
    product_list = [
        {"name": product.Name}
        for product in products
    ]
    if not product_list:
        return {"error": "No products found in the database."}
    return product_list
