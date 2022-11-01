from flask import Flask
from dealership.app.settings import Settings
from dealership.infra.database.connection import Database
from dealership.presentation.router.auth import AuthRouter
from dealership.presentation.router.client import ClientRouter
from dealership.presentation.router.user import UserRouter
from dealership.presentation.router.vehicle import VehicleRouter


database = Database()
database.start()


app = Flask(__name__)
routes = [AuthRouter(app), UserRouter(app), VehicleRouter(app), ClientRouter(app)]
for route in routes:
    route.start()


if __name__ == "__main__":
    app.run(
        host=Settings.APP_HOST,
        port=Settings.APP_PORT,
        debug=False,
        load_dotenv=True,
    )
