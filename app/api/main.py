import uvicorn
from fastapi import FastAPI
from app.api.data_from_db import router
from app.api.db_connection import auth
from app.api.quantity_end_date import amount_router

app = FastAPI()
app.include_router(router)
app.include_router(auth)
app.include_router(amount_router)

# if __name__ == "__main__":
#     uvicorn.run(app, host='127.0.0.1', port=8120)