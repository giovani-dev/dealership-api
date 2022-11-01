from sqlalchemy import Column, Enum, ForeignKey, Integer
from dealership.app.enum.claims import DefaultClaims
from dealership.infra.database.models._base import Base


class Claim(Base):
    __tablename__ = "Claim"

    id = Column("Id", Integer, primary_key=True)
    name = Column("Name", Enum(DefaultClaims))
    user_id = Column("User", Integer, ForeignKey("User.Id"), nullable=False)
