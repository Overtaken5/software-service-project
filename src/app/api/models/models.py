# pydantic models for API
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date

Base = declarative_base()


class Products(Base):
    __tablename__ = "Products"

    Id = Column(Integer, primary_key=True, index=True, nullable=False)
    Name = Column(String, nullable=False)
    CurrentStock = Column(Integer, nullable=False)
    Price = Column(Integer, nullable=False)


class Product(Base):
    __tablename__ = "Product"

    Id = Column(Integer, primary_key=True, index=True, nullable=False)
    ProductId = Column(Integer, nullable=False)
    Date = Column(Date, nullable=False)
    Quantity = Column(Integer, nullable=False)
