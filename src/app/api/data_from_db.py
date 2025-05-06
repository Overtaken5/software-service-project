import base64
import json
import os

import pandas as pd
from dateutil.relativedelta import relativedelta
from fastapi import Form, Request, APIRouter, HTTPException
from fastapi.params import Depends
from fastapi.responses import FileResponse, JSONResponse
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import func

from src.app.api.models.models import Products, Product
from src.app.api.db_connection import get_db
from src.app.product_quantity_forecast.quantity_forecast import Prognosis, Tovar
from datetime import datetime, timedelta
from src.app.product_quantity_forecast.grafik import plot_prognosis

router = APIRouter()



# параметры продукта по названию
@router.get("/one_product_amount")
async def get_product_by_name(product_name: str, db: Session = Depends(get_db)):
    product = db.query(Products).filter(
        (product_name == Products.Name) | (func.upper(Products.Name) == product_name.upper())
    ).first()
    if product is None:
        return {"error": f"Tovar '{product_name}' was not found in the database."}
    return {"message": f"Tovar '{product_name}' exists in the database."}


@router.post("/one_product_amount")
async def get_product_details(product_name: str = Form(...), db: Session = Depends(get_db)):
    product = db.query(Products).filter(
        (product_name == Products.Name) | (func.upper(Products.Name) == product_name.upper())
    ).first()
    if product is None:
        return {"error": f"Tovar '{product_name}' was not found in the database."}
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


# прогноз количества товара(в формате название, период прогноза, конечная дата прогноза, количество на конечную дату)
@router.post("/product_forecast")
async def get_product_forecast(
        product_name: str = Form(...),
        months_ahead: int = Form(...),
        db: Session = Depends(get_db)
):
    product = db.query(Products).filter(
        (product_name == Products.Name) | (func.upper(Products.Name) == product_name.upper())
    ).first()

    if product is None:
        raise HTTPException(status_code=404, detail=f"Tovar '{product_name}' not found.")

    product_records = db.query(Product).filter(Product.ProductId == product.Id).all()
    if not product_records:
        raise HTTPException(status_code=404, detail=f"No records found for product '{product_name}'.")

    current_date = datetime.now()
    start_date = current_date.strftime("%Y-%m-%d")
    end_date = (current_date + relativedelta(months=months_ahead)).strftime("%Y-%m-%d")
    product_instance = Tovar(product.Id, product.Name)
    prognosis = Prognosis(product_instance, start_date, end_date)

    try:
        forecast = prognosis.get_json_prognosis()
        forecast_data = json.loads(forecast)  # Парсим строку JSON в список словарей
        latest_forecast = forecast_data[-1]
        result_forecast = {"date": latest_forecast["date"], "quantity": latest_forecast["quantity"]}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating forecast: {str(e)}")

    return {
        "product_price":product.Price,
        "product_id": product.Id,
        "product_name": product.Name,
        "forecast": [result_forecast]
    }


# выдача графика прогноза
@router.post("/product_forecast_graph")
async def get_product_forecast_graph(
        product_name: str = Form(...),
        months_ahead: int = Form(...),
        db: Session = Depends(get_db)
):
    product = db.query(Products).filter(
        (product_name == Products.Name) | (func.upper(Products.Name) == product_name.upper())
    ).first()

    if product is None:
        raise HTTPException(status_code=404, detail=f"Tovar '{product_name}' not found.")
    product_records = db.query(Product).filter(Product.ProductId == product.Id).all()
    if not product_records:
        raise HTTPException(status_code=404, detail=f"No records found for product '{product_name}'.")

    current_date = datetime.now()
    start_date = current_date.strftime("%Y-%m-%d")
    end_date = (current_date + relativedelta(months=months_ahead)).strftime("%Y-%m-%d")
    product_instance = Tovar(product.Id, product.Name)
    prognosis = Prognosis(product_instance, start_date, end_date)

    try:
        forecast = prognosis.get_json_prognosis()
        forecast_data = json.loads(forecast)  # Парсим строку JSON в список словарей
        graph_filename = plot_prognosis(forecast, start_date, end_date)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error generating forecast or graph: {str(e)}")

    return FileResponse(
        path=graph_filename,
        media_type="image/png",
        filename=graph_filename.split("/")[-1]
    )
