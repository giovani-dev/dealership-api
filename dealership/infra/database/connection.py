from __future__ import annotations
from dealership.app.interface.start import Starter
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine

from dealership.app.settings import Settings
from dealership.infra.database.models._base import Base


class Database(Starter):
    instance: Database | None = None
    engine: Engine

    def start(self):
        from dealership.infra.database.models.claim import Claim
        from dealership.infra.database.models.client import Client
        from dealership.infra.database.models.company import Company
        from dealership.infra.database.models.owner import Owner, OwnerHistory
        from dealership.infra.database.models.user import User
        from dealership.infra.database.models.vehicle import Vehicle

        self.engine = create_engine(
            f"mysql+mysqlconnector://{Settings.MYSQL_USER}:{Settings.MYSQL_PWD}@{Settings.MYSQL_HOST}:{Settings.MYSQL_PORT}/{Settings.MYSQL_DEFAULT_DB}",
            echo=True,
            future=True,
        )
        Base.metadata.create_all(self.engine)
        Database.instance = self
