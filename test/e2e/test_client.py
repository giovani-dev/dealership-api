import os, sys


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.realpath(ROOT_DIR + "../../../"))


from main import app as flask_app


class TestClientE2E:
    def test_create__using_company_credentials__expected_unhautorized_response(self):
        pass
