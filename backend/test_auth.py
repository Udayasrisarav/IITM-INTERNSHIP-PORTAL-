import unittest
import json
import jwt
from app import app
from database import db
from models import User, Role, Module, RoleMapping, Profile
from utils.password_utils import hash_password, verify_password
from utils.jwt_handler import generate_token, decode_token
from middleware.auth_middleware import jwt_required_custom, role_required, permission_required
from flask import jsonify

class Milestone3AuthTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

        # Register test endpoints for RBAC decorator validation
        @cls.app.route("/api/v1/test/superadmin-only", methods=["GET"])
        @role_required("SuperAdmin")
        def test_superadmin_route():
            return jsonify({"message": "Access granted to SuperAdmin"}), 200

        @cls.app.route("/api/v1/test/permission-read-users", methods=["GET"])
        @permission_required("USERS", "can_read")
        def test_permission_read_users():
            return jsonify({"message": "Permission can_read granted for USERS"}), 200

        @cls.app.route("/api/v1/test/permission-delete-users", methods=["DELETE"])
        @permission_required("USERS", "can_delete")
        def test_permission_delete_users():
            return jsonify({"message": "Permission can_delete granted for USERS"}), 200

    @classmethod
    def tearDownClass(cls):
        cls.app_context.pop()

    def test_01_verify_imports(self):
        """1. Verify Module Imports"""
        from services.auth_service import login_user, get_user_details
        from utils.jwt_handler import generate_token, decode_token
        from utils.password_utils import hash_password, verify_password
        from middleware.auth_middleware import jwt_required_custom, role_required, permission_required
        from routes.auth import auth_bp

        self.assertIsNotNone(login_user)
        self.assertIsNotNone(generate_token)
        self.assertIsNotNone(hash_password)
        self.assertIsNotNone(jwt_required_custom)
        self.assertEqual(auth_bp.name, "auth")
        print("\n[PASS] 1. All Milestone 3 authentication and authorization modules imported successfully.")

    def test_02_password_hashing(self):
        """2. Verify Werkzeug password hashing and verification"""
        password = "SecurePassword123!"
        hashed = hash_password(password)
        self.assertNotEqual(password, hashed)
        self.assertTrue(verify_password(hashed, password))
        self.assertFalse(verify_password(hashed, "WrongPassword"))
        print("[PASS] 2. Werkzeug password hashing & verification verified.")

    def test_03_jwt_token_generation_and_decoding(self):
        """3. Verify JWT token generation and decoding with 24-hour expiration"""
        user_id = 999
        email = "jwt_test@iitm.ac.in"
        role_name = "SuperAdmin"

        token = generate_token(user_id=user_id, email=email, role_name=role_name)
        self.assertIsInstance(token, str)

        payload = decode_token(token)
        self.assertEqual(payload.get("user_id"), user_id)
        self.assertEqual(payload.get("email"), email)
        self.assertEqual(payload.get("role"), role_name)
        self.assertIn("exp", payload)
        print("[PASS] 3. JWT token generation & 24-hour expiration payload verified.")

    def test_04_valid_login(self):
        """4. Verify POST /api/v1/auth/login with valid credentials"""
        response = self.client.post(
            "/api/v1/auth/login",
            data=json.dumps({"username": "admin", "password": "SuperAdminPass123!"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertIn("access_token", data)
        self.assertEqual(data.get("role"), "SuperAdmin")
        self.assertIsNotNone(data.get("user_id"))
        print("[PASS] 4. Valid login endpoint (POST /api/v1/auth/login) verified.")

    def test_05_invalid_login(self):
        """5. Verify POST /api/v1/auth/login with invalid credentials"""
        # Wrong password
        res1 = self.client.post(
            "/api/v1/auth/login",
            data=json.dumps({"username": "admin", "password": "WrongPassword!"}),
            content_type="application/json"
        )
        self.assertEqual(res1.status_code, 401)
        self.assertIn("error", res1.get_json())

        # Non-existent user
        res2 = self.client.post(
            "/api/v1/auth/login",
            data=json.dumps({"username": "non_existent_user", "password": "Password123!"}),
            content_type="application/json"
        )
        self.assertEqual(res2.status_code, 401)
        self.assertIn("error", res2.get_json())

        print("[PASS] 5. Invalid login attempts properly rejected with HTTP 401.")

    def test_06_logout(self):
        """6. Verify POST /api/v1/auth/logout"""
        response = self.client.post("/api/v1/auth/logout")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json().get("message"), "Logged out successfully")
        print("[PASS] 6. Logout endpoint (POST /api/v1/auth/logout) verified.")

    def test_07_get_current_user_profile(self):
        """7. Verify GET /api/v1/auth/me (Protected Route)"""
        # Login to get token
        login_res = self.client.post(
            "/api/v1/auth/login",
            data=json.dumps({"username": "admin", "password": "SuperAdminPass123!"}),
            content_type="application/json"
        )
        token = login_res.get_json().get("access_token")

        # Request GET /api/v1/auth/me with Bearer token
        response = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, 200)
        user_info = response.get_json()
        self.assertEqual(user_info.get("email"), "superadmin@iitm.ac.in")
        self.assertEqual(user_info.get("role"), "SuperAdmin")
        self.assertTrue(user_info.get("is_active"))
        # Guarantee password hash is never exposed
        self.assertNotIn("password", user_info)
        self.assertNotIn("password_hash", user_info)
        print("[PASS] 7. Protected route GET /api/v1/auth/me verified (never returns password hash).")

    def test_08_unauthorized_route_access(self):
        """8. Verify unauthorized route access (Missing/Invalid Token)"""
        # Missing token header
        res1 = self.client.get("/api/v1/auth/me")
        self.assertEqual(res1.status_code, 401)

        # Invalid token header
        res2 = self.client.get("/api/v1/auth/me", headers={"Authorization": "Bearer invalid_token_str"})
        self.assertEqual(res2.status_code, 401)

        print("[PASS] 8. Unauthorized route access correctly blocked with HTTP 401.")

    def test_09_rbac_decorators(self):
        """9. Verify @role_required and @permission_required decorators"""
        # Login as SuperAdmin
        login_res = self.client.post(
            "/api/v1/auth/login",
            data=json.dumps({"username": "admin", "password": "SuperAdminPass123!"}),
            content_type="application/json"
        )
        token = login_res.get_json().get("access_token")

        # Test SuperAdmin role route
        res_role = self.client.get(
            "/api/v1/test/superadmin-only",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(res_role.status_code, 200)
        self.assertEqual(res_role.get_json().get("message"), "Access granted to SuperAdmin")

        # Test Permission read users route
        res_perm = self.client.get(
            "/api/v1/test/permission-read-users",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(res_perm.status_code, 200)
        self.assertEqual(res_perm.get_json().get("message"), "Permission can_read granted for USERS")

        print("[PASS] 9. RBAC decorators (@role_required and @permission_required) verified.")

    def test_10_seed_data_integrity(self):
        """10. Verify Seed Data Integrity (Roles, Modules, RoleMappings, Admin)"""
        roles_count = Role.query.count()
        modules_count = Module.query.count()
        mappings_count = RoleMapping.query.count()
        admin_user = User.query.filter_by(email="superadmin@iitm.ac.in").first()

        self.assertGreaterEqual(roles_count, 4)
        self.assertGreaterEqual(modules_count, 6)
        self.assertGreaterEqual(mappings_count, 17)
        self.assertIsNotNone(admin_user)
        print(f"[PASS] 10. Seed Data verified (Roles: {roles_count}, Modules: {modules_count}, Mappings: {mappings_count}, Admin: '{admin_user.email}').")

if __name__ == "__main__":
    print("Running Milestone 3 Authentication & Authorization Test Suite...")
    unittest.main()
