from sqlalchemy import Column, Float, ForeignKey, Integer
from dealership.infra.database.models._base import Base


class Owner(Base):
    __tablename__ = "Owner"

    id = Column("Id", Integer, primary_key=True)
    company_id = Column("Company", Integer, ForeignKey("Company.Id"), nullable=True)
    client_id = Column("Client", Integer, ForeignKey("Client.Id"), nullable=True)
    vehicle_id = Column("Vehicle", Integer, ForeignKey("Vehicle.Id"), nullable=True)


class OwnerHistory(Base):
    __tablename__ = "OwnerHistory"

    id = Column("Id", Integer, primary_key=True)
    owner_id = Column("Owner", Integer, ForeignKey("Owner.Id"), nullable=False)
    owner_client_id = Column("OwnerClient", Integer, nullable=True)
    owner_company_id = Column("OwnerCompany", Integer, nullable=True)
