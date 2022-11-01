from flask import Flask, jsonify, request
from dealership.app.enum.claims import DefaultClaims
from dealership.app.interface.start import Starter
from dealership.core.facade import ClientFacade
from dealership.presentation import auth


class ClientRouter(Starter):
    def __init__(self, app: Flask) -> None:
        self.app = app

    def start(self):
        @self.app.route("/client", methods=["POST"])
        @auth.claims([DefaultClaims.Seller.value])
        async def create_client():
            client = ClientFacade(request.get_json())
            callback = await client.create()
            try:
                return jsonify(callback.content.dict()), callback.status_code.value
            except AttributeError:
                return jsonify(callback.content), callback.status_code.value

        @self.app.route("/client", methods=["GET"])
        @auth.claims([DefaultClaims.Seller.value])
        async def get_clients():
            client = ClientFacade(request.args.to_dict())
            callback = await client.get_clients()
            try:
                return jsonify(callback.content.dict()), callback.status_code.value
            except AttributeError:
                return jsonify(callback.content), callback.status_code.value
