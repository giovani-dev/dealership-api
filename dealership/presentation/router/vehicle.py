from flask import Flask, jsonify, request
from dealership.app.enum.claims import DefaultClaims
from dealership.app.interface.start import Starter
from dealership.core.facade import VehicleFacade
from dealership.presentation import auth


class VehicleRouter(Starter):
    def __init__(self, app: Flask) -> None:
        self.app = app

    def start(self):
        @self.app.route("/vehicle/buy", methods=["POST"])
        @auth.claims([DefaultClaims.Company.value])
        async def buy_vehicle():
            data = request.get_json()
            data.update({"user": request.user.dict()})
            vehicle = VehicleFacade(data)
            callback = await vehicle.buy()
            try:
                return jsonify(callback.content.dict()), callback.status_code.value
            except AttributeError:
                return jsonify(callback.content), callback.status_code.value

        @self.app.route("/vehicle/to-sell", methods=["GET"])
        @auth.claims([DefaultClaims.Seller.value])
        async def get_vehicles_to_sell():
            data = request.args.to_dict()
            data.update({"user": request.user})
            vehicle = VehicleFacade(data)
            callback = await vehicle.get_to_sell()
            try:
                return jsonify(callback.content.dict()), callback.status_code.value
            except AttributeError:
                return jsonify(callback.content), callback.status_code.value

        @self.app.route("/vehicle/sell", methods=["POST"])
        @auth.claims([DefaultClaims.Seller.value])
        async def sell_vehicle():
            data = request.get_json()
            data.update({"company_id": request.user.company_id})
            vehicle = VehicleFacade(data)
            callback = await vehicle.sell_vehicle()
            try:
                return jsonify(callback.content.dict()), callback.status_code.value
            except AttributeError:
                return jsonify(callback.content), callback.status_code.value
