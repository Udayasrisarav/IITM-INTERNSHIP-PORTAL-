import unittest
import json
from app import app
from database import db
from models import User, Role, Module, RoleMapping, Profile
from utils.password_utils import hash_password


class ProfileModuleTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.drop_all()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        cls.app_context.pop()

    def setUp(self):
        db.session.begin_nested()

    def tearDown(self):
        db.session.rollback()

    def _create_role_mapping(self, role_name="Applicant", module_id="PROFILES"):
        role = Role.query.filter_by(role_name=role_name).first()
        if not role:
            role = Role(role_name=role_name, description=f"{role_name} role")
            db.session.add(role)
            db.session.flush()

        module = Module.query.filter_by(module_id=module_id).first()
        if not module:
            module = Module(module_id=module_id, module_name=module_id, description=f"{module_id} module")
            db.session.add(module)
            db.session.flush()

        mapping = RoleMapping.query.filter_by(role_id=role.id, module_id=module.id).first()
        if not mapping:
            mapping = RoleMapping(role_id=role.id, module_id=module.id, can_read=True, can_update=True, can_delete=False)
            db.session.add(mapping)
            db.session.flush()

        return mapping

    def _create_user(self, email, username, password, role_mapping):
        user = User(
            email=email,
            username=username,
            password_hash=hash_password(password),
            role_mapping_id=role_mapping.id,
            is_active=True,
        )
        db.session.add(user)
        db.session.flush()
        return user

    def _login(self, identifier, password):
        response = self.client.post(
            "/api/v1/auth/login",
            data=json.dumps({"username": identifier, "password": password}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        return response.get_json().get("access_token")

    def test_create_profile_success(self):
        mapping = self._create_role_mapping()
        user = self._create_user("applicant1@iitm.ac.in", "applicant1", "Password123!", mapping)
        token = self._login(user.username, "Password123!")

        response = self.client.post(
            "/api/v1/profile",
            headers={"Authorization": f"Bearer {token}"},
            data=json.dumps({
                "full_name": "Applicant One",
                "mobile_number": "1234567890",
                "department": "Computer Science",
            }),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        payload = response.get_json()
        self.assertEqual(payload.get("full_name"), "Applicant One")
        self.assertEqual(payload.get("user_id"), user.id)
        self.assertEqual(payload.get("mobile_number"), "1234567890")

    def test_duplicate_profile_prevention(self):
        mapping = self._create_role_mapping()
        user = self._create_user("applicant2@iitm.ac.in", "applicant2", "Password123!", mapping)
        token = self._login(user.username, "Password123!")

        response1 = self.client.post(
            "/api/v1/profile",
            headers={"Authorization": f"Bearer {token}"},
            data=json.dumps({"full_name": "Applicant Two"}),
            content_type="application/json",
        )
        self.assertEqual(response1.status_code, 201)

        response2 = self.client.post(
            "/api/v1/profile",
            headers={"Authorization": f"Bearer {token}"},
            data=json.dumps({"full_name": "Applicant Two Duplicate"}),
            content_type="application/json",
        )
        self.assertEqual(response2.status_code, 409)
        self.assertIn("error", response2.get_json())

    def test_get_profile_success(self):
        mapping = self._create_role_mapping()
        user = self._create_user("applicant3@iitm.ac.in", "applicant3", "Password123!", mapping)
        token = self._login(user.username, "Password123!")

        profile = Profile(user_id=user.id, full_name="Applicant Three")
        db.session.add(profile)
        db.session.flush()

        response = self.client.get(
            "/api/v1/profile",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload.get("full_name"), "Applicant Three")
        self.assertEqual(payload.get("user_id"), user.id)

    def test_update_profile_success(self):
        mapping = self._create_role_mapping()
        user = self._create_user("applicant4@iitm.ac.in", "applicant4", "Password123!", mapping)
        token = self._login(user.username, "Password123!")

        profile = Profile(user_id=user.id, full_name="Applicant Four", address="Old Address")
        db.session.add(profile)
        db.session.flush()

        response = self.client.put(
            "/api/v1/profile",
            headers={"Authorization": f"Bearer {token}"},
            data=json.dumps({"address": "New Updated Address", "skills": "Python, Flask"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload.get("address"), "New Updated Address")
        self.assertEqual(payload.get("skills"), "Python, Flask")

    def test_unauthorized_access_without_jwt(self):
        response = self.client.get("/api/v1/profile")
        self.assertEqual(response.status_code, 401)
        self.assertIn("error", response.get_json())

        response = self.client.post(
            "/api/v1/profile",
            data=json.dumps({"full_name": "No Token"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertIn("error", response.get_json())

    def test_profile_not_found(self):
        mapping = self._create_role_mapping()
        user = self._create_user("applicant5@iitm.ac.in", "applicant5", "Password123!", mapping)
        token = self._login(user.username, "Password123!")

        response_get = self.client.get(
            "/api/v1/profile",
            headers={"Authorization": f"Bearer {token}"},
        )
        self.assertEqual(response_get.status_code, 404)

        response_put = self.client.put(
            "/api/v1/profile",
            headers={"Authorization": f"Bearer {token}"},
            data=json.dumps({"address": "Should Fail"}),
            content_type="application/json",
        )
        self.assertEqual(response_put.status_code, 404)

    def test_superadmin_access_validation(self):
        profile_mapping = self._create_role_mapping(role_name="Applicant", module_id="PROFILES")
        applicant = self._create_user("applicant6@iitm.ac.in", "applicant6", "Password123!", profile_mapping)
        applicant_profile = Profile(user_id=applicant.id, full_name="Applicant Six", department="AI")
        db.session.add(applicant_profile)
        db.session.flush()

        admin_mapping = self._create_role_mapping(role_name="SuperAdmin", module_id="PROFILES")
        superadmin = self._create_user("superadmin_test@iitm.ac.in", "superadmin_test", "SuperAdminPass123!", admin_mapping)
        token = self._login(superadmin.username, "SuperAdminPass123!")

        response = self.client.get(
            f"/api/v1/profile?user_id={applicant.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload.get("full_name"), "Applicant Six")
        self.assertEqual(payload.get("user_id"), applicant.id)


if __name__ == "__main__":
    print("Running Profile Module Test Suite...")
    unittest.main()
