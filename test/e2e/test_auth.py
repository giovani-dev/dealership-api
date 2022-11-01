import os, sys
from typing import Any, Dict, Tuple
from jose import jwt
from jose.constants import ALGORITHMS


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.realpath(ROOT_DIR + "../../../"))


from main import app as flask_app
from dealership.infra.database.models.claim import Claim
from dealership.infra.database.models.company import Company
from dealership.infra.database.models.user import User
from dealership.app.enum.claims import DefaultClaims
from dealership.app.settings import Settings
from dealership.infra.database.connection import Database
from sqlalchemy.orm import Session
from passlib.hash import pbkdf2_sha256


class TestAuthE2E:
    @classmethod
    def create_company_user(
        cls, user_data: Dict[str, Any], company_data: Dict[str, Any]
    ) -> Tuple[int, int, int]:
        with Session(Database.instance.engine) as session:
            company = Company(
                company_name=company_data["name"],
                owner_name=company_data["cnpj"],
                cnpj=company_data["owner_name"],
            )
            session.add(company)
            session.commit()
            user = User(
                name=user_data["name"],
                email=f"{user_data['email']}",
                password=pbkdf2_sha256.hash(user_data["password"]),
                company_id=company.id,
            )
            session.add(user)
            session.commit()
            claim = Claim(name="Company", user_id=user.id)
            session.add(claim)
            session.commit()
            return company.id, user.id, claim.id

    @classmethod
    def create_seller_user(
        cls, company_id: int, user_data: Dict[str, Any]
    ) -> Tuple[int, int]:
        with Session(Database.instance.engine) as session:
            user = User(
                name=user_data["name"],
                email=f"{user_data['email']}",
                password=pbkdf2_sha256.hash(user_data["password"]),
                company_id=company_id,
            )
            session.add(user)
            session.commit()
            claim = Claim(name="Seller", user_id=user.id)
            session.add(claim)
            session.commit()
            return user.id, claim.id

    @classmethod
    def setup_class(cls):
        cls.company_data = {
            "name": "name test",
            "cnpj": "6166516165165",
            "owner_name": "owner name test",
        }
        cls.user_data = {
            "company": {
                "password": "abc123",
                "name": "++company++",
                "email": "company@gmail.com",
            },
            "seller": {
                "password": "abc123",
                "name": "__seller__",
                "email": "seller@gmail.com",
            },
        }
        company = cls.create_company_user(
            user_data=cls.user_data["company"], company_data=cls.company_data
        )
        cls.company_id, cls.company_user_id, cls.company_claim_id = company
        cls.seller_user_id, cls.seller_claim_id = cls.create_seller_user(
            company_id=cls.company_id, user_data=cls.user_data["seller"]
        )

    @classmethod
    def teardown_class(cls):
        with Session(Database.instance.engine) as session:
            session.query(Claim).filter(Claim.user_id == cls.company_user_id).delete()
            session.query(Claim).filter(Claim.user_id == cls.seller_user_id).delete()
            session.query(User).filter(User.id == cls.seller_user_id).delete()
            session.query(User).filter(User.id == cls.company_user_id).delete()
            session.query(Company).filter(Company.id == cls.company_id).delete()
            session.commit()

    def test_login__using_invalid_credentials__expected_unhautorized_status(self):
        with flask_app.test_client() as client:
            response = client.post(
                "/auth/login", json={"password": "123", "email": "email@email.ru"}
            )
        response_data = response.get_json()
        assert response.status_code == 401
        assert response_data == {
            "loc": [["email"], ["password"]],
            "msg": "Invalid user",
            "type": "validation.invalid_input",
        }

    def test_login__without_credentials__expected_unprocessable_status(self):
        with flask_app.test_client() as client:
            response = client.post("/auth/login", json={})
        response_data = response.get_json()
        assert response.status_code == 422
        assert {
            "loc": ["password"],
            "msg": "field required",
            "type": "value_error.missing",
        } in response_data
        assert {
            "loc": ["email"],
            "msg": "field required",
            "type": "value_error.missing",
        } in response_data

    def test_login__using_company_credentials__expected_token_and_refresh_token(self):
        with flask_app.test_client() as client:
            response = client.post(
                "/auth/login",
                json={
                    "email": self.user_data["company"]["email"],
                    "password": self.user_data["company"]["password"],
                },
            )
        response_data = response.get_json()
        token = jwt.decode(
            token=response_data["token"],
            key=Settings.JWT_SECRET_KEY,
            algorithms=ALGORITHMS.HS512,
        )
        refresh_token = jwt.decode(
            token=response_data["refresh_token"],
            key=Settings.JWT_SECRET_KEY,
            algorithms=ALGORITHMS.HS512,
        )

        assert response.status_code == 200
        assert token["token_id"] == refresh_token["token_id"]
        assert token["claims"] == [DefaultClaims.Company.value]
        assert refresh_token["type"] == "refresh"
        assert token["type"] == "token"

        time_diference = (refresh_token["exp"] - token["exp"]) / 3600
        settings_time_diference = (
            Settings.JWT_REFRESH_TOKEN_TIME_TO_EXPIRE
            - Settings.JWT_TOKEN_TIME_TO_EXPIRE
        )
        assert time_diference > (settings_time_diference - 0.01) and time_diference <= (
            settings_time_diference + 0.01
        )

    def test_login__using_seller_credentials__exprected_token_and_refresh_token(self):
        with flask_app.test_client() as client:
            response = client.post(
                "/auth/login",
                json={
                    "email": self.user_data["seller"]["email"],
                    "password": self.user_data["seller"]["password"],
                },
            )
        response_data = response.get_json()
        token = jwt.decode(
            token=response_data["token"],
            key=Settings.JWT_SECRET_KEY,
            algorithms=ALGORITHMS.HS512,
        )
        refresh_token = jwt.decode(
            token=response_data["refresh_token"],
            key=Settings.JWT_SECRET_KEY,
            algorithms=ALGORITHMS.HS512,
        )

        assert response.status_code == 200
        assert token["token_id"] == refresh_token["token_id"]
        assert token["claims"] == [DefaultClaims.Seller.value]
        assert refresh_token["type"] == "refresh"
        assert token["type"] == "token"

        time_diference = (refresh_token["exp"] - token["exp"]) / 3600
        settings_time_diference = (
            Settings.JWT_REFRESH_TOKEN_TIME_TO_EXPIRE
            - Settings.JWT_TOKEN_TIME_TO_EXPIRE
        )
        assert time_diference > (settings_time_diference - 0.01) and time_diference <= (
            settings_time_diference + 0.01
        )

    def test_refresh__seller_credentials__expected_refreshed_token(self):
        with flask_app.test_client() as client:
            seller_response = client.post(
                "/auth/login",
                json={
                    "email": self.user_data["seller"]["email"],
                    "password": self.user_data["seller"]["password"],
                },
            )
            seller_data = seller_response.get_json()
            refresh_respose = client.post(
                "/auth/refresh",
                json={
                    "token": seller_data["token"],
                    "refresh_token": seller_data["refresh_token"],
                },
            )
            refresh_data = refresh_respose.get_json()

        token_decoded = jwt.decode(
            token=refresh_data["token"],
            key=Settings.JWT_SECRET_KEY,
            algorithms=ALGORITHMS.HS512,
        )
        refresh_token_decoded = jwt.decode(
            token=refresh_data["refresh_token"],
            key=Settings.JWT_SECRET_KEY,
            algorithms=ALGORITHMS.HS512,
        )

        assert refresh_respose.status_code == 200
        assert seller_response.status_code == 200

        assert seller_data["token"] != refresh_data["token"]
        assert seller_data["refresh_token"] != refresh_data["refresh_token"]

        assert token_decoded["token_id"] == refresh_token_decoded["token_id"]
        assert token_decoded["claims"] == [DefaultClaims.Seller.value]
        assert refresh_token_decoded["type"] == "refresh"
        assert token_decoded["type"] == "token"

        time_diference = (refresh_token_decoded["exp"] - token_decoded["exp"]) / 3600
        settings_time_diference = (
            Settings.JWT_REFRESH_TOKEN_TIME_TO_EXPIRE
            - Settings.JWT_TOKEN_TIME_TO_EXPIRE
        )
        assert time_diference > (settings_time_diference - 0.01) and time_diference <= (
            settings_time_diference + 0.01
        )
