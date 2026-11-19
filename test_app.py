"""Basic regression tests for SecureGate's important user flows."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import app as secure_app


class SecureGateTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database = Path(self.temp_dir.name) / "test_users.db"
        self.database_patch = patch.object(secure_app, "DATABASE", self.database)
        self.database_patch.start()
        secure_app.app.config.update(TESTING=True, SECRET_KEY="test-secret-key")
        secure_app.init_db()
        self.client = secure_app.app.test_client()

    def tearDown(self):
        self.database_patch.stop()
        self.temp_dir.cleanup()

    def token(self, page):
        response = self.client.get(page)
        self.assertEqual(response.status_code, 200)
        with self.client.session_transaction() as session:
            return session["_csrf_token"]

    def register(self, username="test_user", password="StrongPass123"):
        token = self.token("/register")
        return self.client.post(
            "/register",
            data={"_csrf_token": token, "username": username, "password": password},
            follow_redirects=True,
        )

    def login(self, username="test_user", password="StrongPass123"):
        token = self.token("/login")
        return self.client.post(
            "/login",
            data={"_csrf_token": token, "username": username, "password": password},
            follow_redirects=True,
        )

    def test_registration_stores_hash_not_plain_password(self):
        self.register()
        with secure_app.app.app_context():
            row = secure_app.get_db().execute(
                "SELECT password_hash FROM users WHERE username = ?", ("test_user",)
            ).fetchone()
        self.assertNotEqual(bytes(row["password_hash"]), b"StrongPass123")
        self.assertTrue(bytes(row["password_hash"]).startswith(b"$2b$"))

    def test_login_and_logout(self):
        self.register()
        response = self.login()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Welcome, test_user", response.data)

        token = self.token("/dashboard")
        response = self.client.post(
            "/logout", data={"_csrf_token": token}, follow_redirects=True
        )
        self.assertIn(b"Log in to your account", response.data)

    def test_dashboard_requires_login(self):
        response = self.client.get("/dashboard")
        self.assertEqual(response.status_code, 302)
        self.assertIn("/login", response.headers["Location"])

    def test_wrong_password_is_rejected(self):
        self.register()
        response = self.login(password="WrongPass123")
        self.assertEqual(response.status_code, 401)
        self.assertIn(b"Invalid username or password", response.data)

    def test_registration_rejects_weak_password(self):
        token = self.token("/register")
        response = self.client.post(
            "/register",
            data={"_csrf_token": token, "username": "another_user", "password": "weak"},
        )
        self.assertEqual(response.status_code, 400)

    def test_post_without_csrf_token_is_rejected(self):
        response = self.client.post(
            "/register", data={"username": "no_token", "password": "StrongPass123"}
        )
        self.assertEqual(response.status_code, 400)

    def test_security_headers_are_present(self):
        response = self.client.get("/login")
        self.assertEqual(response.headers["X-Frame-Options"], "DENY")
        self.assertEqual(response.headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(response.headers["Cache-Control"], "no-store")


if __name__ == "__main__":
    unittest.main()
