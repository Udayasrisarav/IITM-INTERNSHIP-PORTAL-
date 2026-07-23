from models import User, RoleMapping, Role, Profile
from utils.password_utils import verify_password
from utils.jwt_handler import generate_token
import logging

def login_user(identifier: str, password: str) -> tuple[dict | None, str | None, int]:
    """
    Authenticate user by username or email and password.
    Returns (result_dict, error_message, status_code)
    """
    if not identifier or not password:
        return None, "Username/email and password are required", 400

    # Query user by email or username
    user = User.query.filter(
        (User.email == identifier) | (User.username == identifier)
    ).first()

    if not user:
        return None, "Invalid credentials", 401

    if not user.password_hash or not verify_password(user.password_hash, password):
        return None, "Invalid credentials", 401

    if not user.is_active:
        return None, "User account is inactive", 403

    # Resolve role name from role_mapping -> role
    role_name = "Applicant"
    if user.role_mapping and user.role_mapping.role:
        role_name = user.role_mapping.role.role_name

    access_token = generate_token(user_id=user.id, email=user.email, role_name=role_name)

    return {
        "access_token": access_token,
        "role": role_name,
        "user_id": user.id
    }, None, 200


def get_user_details(user: User) -> dict:
    """Return sanitized user details without password hashes."""
    role_name = "Applicant"
    if user.role_mapping and user.role_mapping.role:
        role_name = user.role_mapping.role.role_name

    full_name = user.username or user.email
    if user.profile and user.profile.full_name:
        full_name = user.profile.full_name

    return {
        "id": user.id,
        "full_name": full_name,
        "email": user.email,
        "role": role_name,
        "is_active": bool(user.is_active)
    }


def google_oauth_authenticate(id_token: str) -> tuple[dict | None, str | None, int]:
    """
    Integration-ready Google OAuth authentication handler.
    Validates Google ID token and resolves user account & pre-defined role.
    """
    if not id_token:
        return None, "Google ID token is required", 400

    # Structural placeholder for google.oauth2.id_token verification
    # Production integration will verify against GOOGLE_CLIENT_ID
    return None, "Google OAuth verification is ready for configuration", 501
