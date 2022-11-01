from typing import List
from flask import Flask
from dealership.app.interface.start import Starter
from dealership.app.settings import Settings
from dealership.presentation.router.auth import AuthRouter
from dealership.presentation.router.client import ClientRouter
from dealership.presentation.router.user import UserRouter
from dealership.presentation.router.vehicle import VehicleRouter


class ApiStarter(Starter):
    def __init__(self) -> None:
        self.app = Flask(__name__)
        self.routes = [
            AuthRouter(self.app),
            UserRouter(self.app),
            VehicleRouter(self.app),
            ClientRouter(self.app)
        ]

    def start(self):
        for route in self.routes:
            route.start()
        self.app.run(
            host=Settings.APP_HOST,
            port=Settings.APP_PORT,
            debug=False,
            load_dotenv=True,
        )
