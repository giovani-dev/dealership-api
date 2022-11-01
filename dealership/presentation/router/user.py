from flask import Flask, jsonify, request
from dealership.app.interface.start import Starter
from dealership.core.facade import UserFace
from dealership.presentation import auth


class UserRouter(Starter):
    def __init__(self, app: Flask) -> None:
        self.app = app

    def start(self):
        @self.app.route("/user/seller/<int:company_id>", methods=["POST"])
        async def create_seller_user(company_id: int):
            if not request.is_json:
                return None, 422
            content = request.get_json()
            content.update({"company_id": company_id})
            user = UserFace(content)
            callback = await user.create_seller()
            try:
                return jsonify(callback.content.dict()), callback.status_code.value
            except AttributeError:
                return jsonify(callback.content), callback.status_code.value

        @self.app.route("/user/company", methods=["POST"])
        async def create_company_user():
            if not request.is_json:
                return None, 422
            user = UserFace(request.get_json())
            callback = await user.create_company()
            try:
                return jsonify(callback.content.dict()), callback.status_code.value
            except AttributeError:
                return jsonify(callback.content), callback.status_code.value
