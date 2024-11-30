from fastapi import Form, Request, APIRouter
from fastapi.params import Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session
from sqlalchemy.sql.functions import func

from app.api.models.models import Product
from app.api.login import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/frontend")

# прогноз продуктов
@router.post("/products_forecast")
async def check_products_amount():
    pass


async def give_forecast():
    pass

@router.get("/products_amount", response_class=HTMLResponse)
async def show_products_page(request: Request):
    return templates.TemplateResponse("products_list.html", {"request": request})


# выдача количества продукта и прогноза
@router.post("/products_amount", response_class=HTMLResponse)
async def give_products_amount(request: Request, product_name: str = Form(), db: Session = Depends(get_db)):
    product = db.query(Product).filter(
        (product_name == Product.name) | (func.upper(Product.name) == product_name.upper())
    ).first()

    if product is None:
        return templates.TemplateResponse(
            "products_list.html",
            {
                "request": request,
                "error_message": "The product was not found. Try again!",
                "product_name": None,
                "amount": None,
            }
        )

    return templates.TemplateResponse(
        "products_list.html",
        {
            "request": request,
            "error_message": None,
            "product_name": product.name,
            "amount": product.quantity,
        }
    )