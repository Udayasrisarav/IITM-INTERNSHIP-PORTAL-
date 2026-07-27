import json
import unittest
import uuid

from app import app
from database import db
from models import (
    User,
    Role,
    Module,
    RoleMapping,
    Profile
)
from utils.password_utils import hash_password


class ApplicationModuleTestCase(unittest.TestCase):

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
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        db.session.begin_nested()

    def tearDown(self):
        db.session.rollback()

    def _get_or_create_role(self, role_name):
        role = Role.query.filter_by(role_name=role_name).first()

        if role:
            return role

        role = Role(
            role_name=role_name,
            description=f"{role_name} role"
        )

        db.session.add(role)
        db.session.flush()

        return role

    def _get_or_create_module(self):
        module = Module.query.filter_by(
            module_id="APPLICATIONS"
        ).first()

        if module:
            return module

        module = Module(
            module_id="APPLICATIONS",
            module_name="APPLICATIONS",
            description="Applications module"
        )

        db.session.add(module)
        db.session.flush()

        return module

    def _get_or_create_mapping(self, role):
        module = self._get_or_create_module()

        mapping = RoleMapping.query.filter_by(
            role_id=role.id,
            module_id=module.id
        ).first()

        if mapping:
            return mapping

        mapping = RoleMapping(
            role_id=role.id,
            module_id=module.id,
            can_read=True,
            can_update=True,
            can_delete=False
        )

        db.session.add(mapping)
        db.session.flush()

        return mapping

    def _create_user(self, username, role_name="Applicant"):
        role = self._get_or_create_role(role_name)
        mapping = self._get_or_create_mapping(role)

        unique = uuid.uuid4().hex[:8]

        user = User(
            email=f"{username}_{unique}@iitm.ac.in",
            username=username,
            password_hash=hash_password("Password123!"),
            role_mapping_id=mapping.id,
            is_active=True
        )

        db.session.add(user)
        db.session.flush()

        return user

    def _create_profile(self, user):
        profile = Profile(
            user_id=user.id,
            full_name=f"Profile {user.username}"
        )

        db.session.add(profile)
        db.session.flush()

        return profile

    def _login(self, username):
        response = self.client.post(
            "/api/v1/auth/login",
            data=json.dumps({
                "username": username,
                "password": "Password123!"
            }),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)

        return response.get_json()["access_token"]

    def test_create_application_success(self):

        user = self._create_user("applicant_create")
        self._create_profile(user)

        token = self._login(user.username)

        response = self.client.post(
            "/api/v1/applications/",
            headers={
                "Authorization": f"Bearer {token}"
            },
            data=json.dumps({
                "referred_by": "Professor",
                "referred_from": "Within IIT"
            }),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 201)

        payload = response.get_json()

        self.assertEqual(
            payload.get("status"),
            "Draft"
        )

        self.assertTrue(
            payload.get("application_number").startswith("IITM-")
        )

    def test_create_application_requires_profile(self):

        user = self._create_user("applicant_no_profile")

        token = self._login(user.username)

        response = self.client.post(
            "/api/v1/applications/",
            headers={
                "Authorization": f"Bearer {token}"
            },
            data=json.dumps({
                "referred_by": "Professor"
            }),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)

    def test_get_application_success(self):

        user = self._create_user("applicant_get")
        self._create_profile(user)

        token = self._login(user.username)

        create_response = self.client.post(
            "/api/v1/applications/",
            headers={
                "Authorization": f"Bearer {token}"
            },
            data=json.dumps({
                "referred_by": "Supervisor"
            }),
            content_type="application/json"
        )

        application_id = create_response.get_json()["id"]

        response = self.client.get(
            f"/api/v1/applications/{application_id}",
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

        self.assertEqual(response.status_code, 200)

    def test_update_application_only_when_draft(self):

        user = self._create_user("applicant_update")
        self._create_profile(user)

        token = self._login(user.username)

        create_response = self.client.post(
            "/api/v1/applications/",
            headers={
                "Authorization": f"Bearer {token}"
            },
            data=json.dumps({
                "referred_by": "Old"
            }),
            content_type="application/json"
        )

        application_id = create_response.get_json()["id"]

        response = self.client.put(
            f"/api/v1/applications/{application_id}",
            headers={
                "Authorization": f"Bearer {token}"
            },
            data=json.dumps({
                "referred_by": "New"
            }),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.get_json()["referred_by"],
            "New"
        )

    def test_submit_application_sets_status_and_timestamp(self):

        user = self._create_user("applicant_submit")
        self._create_profile(user)

        token = self._login(user.username)

        create_response = self.client.post(
            "/api/v1/applications/",
            headers={
                "Authorization": f"Bearer {token}"
            },
            data=json.dumps({
                "referred_by": "Referral"
            }),
            content_type="application/json"
        )

        application_id = create_response.get_json()["id"]

        response = self.client.post(
            f"/api/v1/applications/{application_id}/submit",
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

        self.assertEqual(response.status_code, 200)

        payload = response.get_json()

        self.assertEqual(
            payload["status"],
            "Submitted"
        )

        self.assertIsNotNone(
            payload["submitted_at"]
        )

    def test_owner_access_is_enforced(self):

        owner = self._create_user("owner")
        self._create_profile(owner)

        owner_token = self._login(owner.username)

        other = self._create_user("other")
        self._create_profile(other)

        other_token = self._login(other.username)

        create_response = self.client.post(
            "/api/v1/applications/",
            headers={
                "Authorization": f"Bearer {owner_token}"
            },
            data=json.dumps({
                "referred_by": "Owner"
            }),
            content_type="application/json"
        )

        application_id = create_response.get_json()["id"]

        response = self.client.get(
            f"/api/v1/applications/{application_id}",
            headers={
                "Authorization": f"Bearer {other_token}"
            }
        )

        self.assertEqual(response.status_code, 403)


if __name__ == "__main__":
    print("Running Application Module Test Suite...")
    unittest.main()