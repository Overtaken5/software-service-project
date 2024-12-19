import uvicorn
from fastapi import FastAPI
from app.api.data_from_db import router
from app.api.db_connection import auth

app = FastAPI()
app.include_router(router)
app.include_router(auth)

# if __name__ == "__main__":
#     uvicorn.run(app, host='127.0.0.1', port=8120)