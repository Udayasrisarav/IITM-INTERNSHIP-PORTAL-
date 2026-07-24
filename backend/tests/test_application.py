import json
import unittest
import uuid

from app import app
from database import db
from models import Profile, Role, RoleMapping, User, Module
from utils.password_utils import hash_password


class ApplicationModuleTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.client = cls.app.test_client()
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        cls.app_context.pop()

    def setUp(self):
        db.session.begin_nested()

    def tearDown(self):
        db.session.rollback()

    def _get_or_create_role(self, role_name):
        role = Role.query.filter_by(role_name=role_name).first()
        if role:
            return role
        role = Role(role_name=role_name, description=f"{role_name} role")
        db.session.add(role)
        db.session.flush()
        return role

    def _get_or_create_module(self, module_name, module_id):
        module = Module.query.filter_by(module_name=module_name).first()
        if module:
            return module
        module = Module(module_id=module_id, module_name=module_name, description=f"{module_name} module")
        db.session.add(module)
        db.session.flush()
        return module

    def _create_user(self, username, email=None, role_name="Applicant"):
        unique_suffix = uuid.uuid4().hex[:8]
        email = email or f"{username}_{unique_suffix}@iitm.ac.in"
        role = self._get_or_create_role(role_name)
        module = self._get_or_create_module("APPLICATIONS", "APPLICATIONS")
        mapping = RoleMapping.query.filter_by(role_id=role.id, module_id=module.id).first()
        if not mapping:
            mapping = RoleMapping(role_id=role.id, module_id=module.id, can_read=True, can_update=True, can_delete=False)
            db.session.add(mapping)
            db.session.flush()

        user = User(
            email=email,
            username=username,
            password_hash=hash_password("Password123!"),
            role_mapping_id=mapping.id,
            is_active=True,
        )
        db.session.add(user)
        db.session.flush()
        return user

    def _create_profile(self, user):
        profile = Profile(user_id=user.id, full_name=f"Profile {user.username}")
        db.session.add(profile)
        db.session.flush()
        return profile

    def _login(self, username):
        response = self.client.post(
            "/api/v1/auth/login",
            data=json.dumps({"username": username, "password": "Password123!"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        return response.get_json().get("access_token")

    def test_create_application_success(self):
        user = self._create_user("applicant_create")
        self._create_profile(user)
        token = self._login(user.username)

        response = self.client.post(
            "/api/v1/applications/",
            headers={"Authorization": f"Bearer {token}"},
            data=json.dumps({"referred_by": "Professor", "referred_from": "Within IIT"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 201)
        payload = response.get_json()
        self.assertEqual(payload.get("status"), "Draft")
        self.assertTrue(payload.get("application_number", "").startswith("IITM-"))
        self.assertEqual(payload.get("referred_by"), "Professor")

    def test_create_application_requires_profile(self):
        user = self._create_user("applicant_without_profile")
        token = self._login(user.username)

        response = self.client.post(
            "/api/v1/applications/",
            headers={"Authorization": f"Bearer {token}"},
            data=json.dumps({"referred_by": "Professor"}),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.get_json())

    def test_get_application_success(self):
        user = self._create_user("applicant_get")
        self._create_profile(user)
        token = self._login(user.username)

        create_response = self.client.post(
            "/api/v1/applications/",
            headers={"Authorization": f"Bearer {token}"},
            data=json.dumps({"referred_by": "Supervisor"}),
            content_type="application/json",
        )
        application_id = create_response.get_json().get("id")

        response = self.client.get(
            f"/api/v1/applications/{application_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload.get("id"), application_id)
        self.assertEqual(payload.get("referred_by"), "Supervisor")

    def test_update_application_only_when_draft(self):
        user = self._create_user("applicant_update")
        self._create_profile(user)
        token = self._login(user.username)

        create_response = self.client.post(
            "/api/v1/applications/",
            headers={"Authorization": f"Bearer {token}"},
            data=json.dumps({"referred_by": "Old Referral"}),
            content_type="application/json",
        )
        application_id = create_response.get_json().get("id")

        update_response = self.client.put(
            f"/api/v1/applications/{application_id}",
            headers={"Authorization": f"Bearer {token}"},
            data=json.dumps({"referred_by": "New Referral"}),
            content_type="application/json",
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.get_json().get("referred_by"), "New Referral")

    def test_submit_application_sets_status_and_timestamp(self):
        user = self._create_user("applicant_submit")
        self._create_profile(user)
        token = self._login(user.username)

        create_response = self.client.post(
            "/api/v1/applications/",
            headers={"Authorization": f"Bearer {token}"},
            data=json.dumps({"referred_by": "Referral"}),
            content_type="application/json",
        )
        application_id = create_response.get_json().get("id")

        response = self.client.post(
            f"/api/v1/applications/{application_id}/submit",
            headers={"Authorization": f"Bearer {token}"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.get_json()
        self.assertEqual(payload.get("status"), "Submitted")
        self.assertIsNotNone(payload.get("submitted_at"))

    def test_owner_access_is_enforced(self):
        owner = self._create_user("applicant_owner")
        self._create_profile(owner)
        owner_token = self._login(owner.username)

        other_user = self._create_user("applicant_other")
        self._create_profile(other_user)
        other_token = self._login(other_user.username)

        create_response = self.client.post(
            "/api/v1/applications/",
            headers={"Authorization": f"Bearer {owner_token}"},
            data=json.dumps({"referred_by": "Owner referral"}),
            content_type="application/json",
        )
        application_id = create_response.get_json().get("id")

        response = self.client.get(
            f"/api/v1/applications/{application_id}",
            headers={"Authorization": f"Bearer {other_token}"},
        )

        self.assertEqual(response.status_code, 403)
        self.assertIn("error", response.get_json())


if __name__ == "__main__":
    print("Running Application Module Test Suite...")
    unittest.main()
