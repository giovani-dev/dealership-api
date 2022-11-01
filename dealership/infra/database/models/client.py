from sqlalchemy import Column, Integer, String
from dealership.infra.database.models._base import Base


class Client(Base):
    __tablename__ = "Client"

    id = Column("Id", Integer, primary_key=True)
    first_name = Column("Name", String(75))
    last_name = Column("LastName", String(50))
