from flask import Flask, jsonify, request
from dealership.app.interface.start import Starter
from dealership.core.facade import AuthFacade


class AuthRouter(Starter):
    def __init__(self, app: Flask) -> None:
        self.app = app

    def start(self):
        @self.app.route("/auth/login", methods=["POST"])
        async def login():
            auth = AuthFacade(request.get_json())
            callback = await auth.login()
            try:
                return jsonify(callback.content.dict()), callback.status_code.value
            except AttributeError:
                return jsonify(callback.content), callback.status_code.value

        @self.app.route("/auth/refresh", methods=["POST"])
        async def refresh():
            auth = AuthFacade(request.get_json())
            callback = await auth.refresh()
            try:
                return jsonify(callback.content.dict()), callback.status_code.value
            except AttributeError:
                return jsonify(callback.content), callback.status_code.value
