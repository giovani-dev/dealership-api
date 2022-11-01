# TODO: Testar implementação do banco de dados em conjunto com a chamada de api
import os, sys

import pytest


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.realpath(ROOT_DIR + "../../../"))


from main import app as flask_app
from dealership.infra.database.connection import Database
from dealership.infra.database.models.user import User
from dealership.infra.database.models.claim import Claim
from dealership.infra.database.models.company import Company
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from passlib.hash import pbkdf2_sha256


class TestCompanyUserE2E:
    @classmethod
    def setup_class(cls):
        Database().start()
        cls.content = {
            "user": {
                "password": "123",
                "name": "Teste",
                "email": "teste@gmail.com",
            },
            "company": {
                "name": "name test",
                "cnpj": "6166516165165",
                "owner_name": "owner name test",
            },
        }

    def teardown_method(self, method):
        if (
            method.__name__
            == "test_create__user_with_valid_data__expected_success_callback"
        ):
            with Session(Database.instance.engine) as session:
                user = (
                    session.query(User)
                    .filter(User.email == self.content["user"]["email"])
                    .one()
                )
                session.query(Claim).filter(Claim.user_id == user.id).delete()
                session.query(User).filter(
                    User.email == self.content["user"]["email"]
                ).delete()
                session.query(Company).filter(Company.id == user.company_id).delete()
                session.commit()

    def test_create__user_with_valid_data__expected_success_callback(self):
        with flask_app.test_client() as client:
            response = client.post(
                "/user/company",
                json=self.content,
            )
        response_data = response.get_json()
        company_id = response_data["company"].pop("id")
        user_id = response_data["user"].pop("id")
        user_company_id = response_data["user"].pop("company_id")

        assert response.status_code == 201
        assert isinstance(company_id, int)
        assert isinstance(user_id, int)
        assert isinstance(user_company_id, int)
        assert response_data == {
            "company": {
                "cnpj": "6166516165165",
                "name": "name test",
                "owner_name": "owner name test",
            },
            "user": {
                "email": "teste@gmail.com",
                "name": "Teste",
            },
        }
        with Session(Database.instance.engine) as session:
            user = session.query(User).get(user_id)
            company = session.query(Company).get(company_id)
            claims = session.query(Claim.name).filter(Claim.user_id == user_id).all()
            claims = [claim[0].name for claim in claims]

            assert company.company_name == response_data["company"].get("name")
            assert company.owner_name == response_data["company"].get("owner_name")
            assert company.cnpj == response_data["company"].get("cnpj")

            assert user.name == response_data["user"].get("name")
            assert user.email == response_data["user"].get("email")
            assert user.company_id == user_company_id
            assert pbkdf2_sha256.verify(self.content["user"]["password"], user.password)

            assert claims == ["Company"]

    def test_create__company_with_invalid_email__expected_unprocessable_entry(
        self,
    ):
        self.content["user"]["email"] = "email.com"
        with flask_app.test_client() as client:
            response = client.post(
                "/user/company",
                json=self.content,
            )
        response_data = response.get_json()
        assert response.status_code == 422
        assert isinstance(response_data, list)
        assert {
            "loc": ["user", "email"],
            "msg": "value is not a valid email address",
            "type": "value_error.email",
        } in response_data

        with Session(Database.instance.engine) as session:
            with pytest.raises(NoResultFound):
                session.query(User).filter(
                    User.email == self.content["user"]["email"]
                ).one()

    def test_create__company_with_any_data__expected_unprocessable_entry(self):
        with flask_app.test_client() as client:
            response = client.post(
                "/user/company",
                json={},
            )
            response_data = response.get_json()
            assert response.status_code == 422
            assert {
                "loc": ["company"],
                "msg": "field required",
                "type": "value_error.missing",
            } in response_data
            assert {
                "loc": ["user"],
                "msg": "field required",
                "type": "value_error.missing",
            } in response_data


class TestSellerUserE2E:
    @classmethod
    def setup_class(cls):
        cls.content = {
            "password": "1131313asd",
            "name": "teste testando",
            "email": "email@email.ru",
        }

    def setup_method(self, method):
        with Session(Database.instance.engine) as session:
            company = Company(
                company_name="teste", owner_name="teste", cnpj="15936987413325"
            )
            session.add(company)
            session.commit()
            self.company_id = company.id

    def teardown_method(self, method):
        if (
            method.__name__
            == "test_create__seller_with_valid_data__expected_success_callback"
        ):
            with Session(Database.instance.engine) as session:
                user = (
                    session.query(User)
                    .filter(User.email == self.content["email"])
                    .filter(User.company_id == self.company_id)
                    .one()
                )
                session.query(Claim).filter(Claim.user_id == user.id).delete()
                session.query(User).filter(User.email == self.content["email"]).filter(
                    User.company_id == self.company_id
                ).delete()
                session.query(Company).filter(Company.id == self.company_id).delete()
                session.commit()

    def test_create__seller_with_valid_data__expected_success_callback(self):
        with flask_app.test_client() as client:
            response = client.post(
                f"/user/seller/{self.company_id}",
                json=self.content,
            )
        response_data = response.get_json()
        user_id = response_data.pop("id")

        assert response.status_code == 201
        assert isinstance(user_id, int)
        assert response_data == {
            "company_id": self.company_id,
            "email": "email@email.ru",
            "name": "teste testando",
        }
        with Session(Database.instance.engine) as session:
            user = session.query(User).filter(User.id == user_id).one()
            claims = session.query(Claim.name).filter(Claim.user_id == user_id).all()
            claims = [claim[0].name for claim in claims]

            assert user.id == user_id
            assert user.name == response_data["name"]
            assert user.email == response_data["email"]
            assert user.company_id == response_data["company_id"]
            assert pbkdf2_sha256.verify(self.content["password"], user.password)

            assert claims == ["Seller"]

    def test_create__seller_with_invalid_email__expected_unprocessable_entry(
        self,
    ):
        self.content["email"] = "email.com"
        with flask_app.test_client() as client:
            response = client.post(
                f"/user/seller/{self.company_id}",
                json=self.content,
            )
        response_data = response.get_json()
        assert response.status_code == 422
        assert isinstance(response_data, list)
        assert {
            "loc": ["email"],
            "msg": "value is not a valid email address",
            "type": "value_error.email",
        } in response_data

        with Session(Database.instance.engine) as session:
            with pytest.raises(NoResultFound):
                session.query(User).filter(User.email == self.content["email"]).one()

    def test_create__seller_with_any_data__expected_unprocessable_entry(self):
        with flask_app.test_client() as client:
            response = client.post(
                f"/user/seller/{self.company_id}",
                json={},
            )
            response_data = response.get_json()
        assert response.status_code == 422

        assert {
            "loc": ["password"],
            "msg": "field required",
            "type": "value_error.missing",
        } in response_data
        assert {
            "loc": ["name"],
            "msg": "field required",
            "type": "value_error.missing",
        } in response_data
        assert {
            "loc": ["email"],
            "msg": "field required",
            "type": "value_error.missing",
        } in response_data

    def test_create__seller_with_company_id_on_string_format__expected_not_found_error(
        self,
    ):
        with flask_app.test_client() as client:
            response = client.post(
                "/user/seller/um",
                json={},
            )
        assert response.status_code == 404
