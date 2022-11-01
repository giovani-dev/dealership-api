from sqlalchemy import Column, Enum, Float, Integer
from dealership.infra.database.models._base import Base
from dealership.app.enum import vehicle


class Vehicle(Base):
    __tablename__ = "Vehicle"

    id = Column("Id", Integer, primary_key=True)
    model = Column("Model", Enum(vehicle.Model))
    color = Column("Color", Enum(vehicle.Color))
