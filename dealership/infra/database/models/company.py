from sqlalchemy import Column, Integer, String
from dealership.infra.database.models._base import Base


class Company(Base):
    __tablename__ = "Company"

    id = Column("Id", Integer, primary_key=True)
    company_name = Column("CompanyName", String(75))
    owner_name = Column("OwnerName", String(125))
    cnpj = Column("CNPJ", String(20))
