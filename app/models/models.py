# pydantic models for API
from pydantic import BaseModel, PositiveInt, EmailStr, Field
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
Base = declarative_base()


class Person(Base):
    __tablename__= "Users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    hashed_password = Column(String)
    token = Column(String)
    role = Column(String)