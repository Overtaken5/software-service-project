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

from app.api.models.models import Products, Product
from app.api.db_connection import get_db
from app.product_quantity_forecast.quantity_forecast import Prognosis, Tovar
from datetime import datetime, timedelta
from app.product_quantity_forecast.grafik import plot_prognosis
from shortage_date_prediction.shortage_date_prognosis import ShortagePrognosis, ProductShortage

amount_router = APIRouter()

@amount_router.post("/product_shortage_date")
async def get_product_shortage_date(
        product_name: str = Form(...),
        min_interval_l: int = Form(7),  # Минимальная длина интервала, по умолчанию 7 дней
        db: Session = Depends(get_db)
):
    product = db.query(Products).filter(
        (product_name == Products.Name) | (Products.Name.ilike(f"%{product_name}%"))
    ).first()

    if product is None:
        raise HTTPException(status_code=404, detail=f"Product '{product_name}' not found.")

    product_instance = ProductShortage(product.Id, product.Name)
    prognosis = ShortagePrognosis(product_instance, min_interval_l=min_interval_l)

    try:
        success, shortage_date = prognosis.get_shortage_date()
        if not success:
            raise HTTPException(status_code=400, detail="Unable to calculate shortage date with the given parameters.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating shortage date: {str(e)}")

    return {
        "product_id": product.Id,
        "product_name": product.Name,
        "shortage_date": shortage_date
    }


