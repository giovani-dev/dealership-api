from dealership.infra.database.models._base import Base
from sqlalchemy import Column, ForeignKey, Integer, String


class User(Base):
    __tablename__ = "User"

    id = Column("Id", Integer, primary_key=True)
    name = Column("Name", String(75))
    email = Column("Email", String(100))
    password = Column("Password", String(255))
    company_id = Column("Company", Integer, ForeignKey("Company.Id"), nullable=True)
