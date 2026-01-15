import os
from unittest import TestCase
from tests.factories import AccountFactory
from service.common import status
from service.models import db, Account, init_db
from service.routes import app

DATABASE_URI = os.getenv("DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres")

class TestAccountService(TestCase):
    @classmethod
    def setUpClass(cls):
        app.config["TESTING"], app.config["SQLALCHEMY_DATABASE_URI"] = True, DATABASE_URI
        init_db(app)

    def setUp(self):
        db.session.query(Account).delete()
        db.session.commit()
        self.client = app.test_client()

    def _create_accounts(self, count):
        accounts = []
        for _ in range(count):
            account = AccountFactory()
            resp = self.client.post("/accounts", json=account.serialize())
            account.id = resp.get_json()["id"]
            accounts.append(account)
        return accounts

    def test_index(self):
        self.assertEqual(self.client.get("/").status_code, status.HTTP_200_OK)

    def test_create_account(self):
        account = AccountFactory()
        resp = self.client.post("/accounts", json=account.serialize(), content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(resp.headers.get("Location"))

    def test_get_account_list(self):
        self._create_accounts(3)
        resp = self.client.get("/accounts")
        self.assertEqual(len(resp.get_json()), 3)

    def test_get_account(self):
        account = self._create_accounts(1)[0]
        resp = self.client.get(f"/accounts/{account.id}")
        self.assertEqual(resp.get_json()["name"], account.name)

    def test_update_account(self):
        account = self._create_accounts(1)[0]
        account.name = "Updated"
        resp = self.client.put(f"/accounts/{account.id}", json=account.serialize())
        self.assertEqual(resp.get_json()["name"], "Updated")

    def test_delete_account(self):
        account = self._create_accounts(1)[0]
        self.assertEqual(self.client.delete(f"/accounts/{account.id}").status_code, status.HTTP_204_NO_CONTENT)